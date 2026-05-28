"""Motor de clustering local — versão script do notebook Colab.

Executa o pipeline completo de clustering e exporta cluster_profiles.json.
Uso: uv run python -m engine.clustering
"""

import json
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# Seed para reprodutibilidade
RANDOM_STATE: int = 42
np.random.seed(RANDOM_STATE)

# Caminhos
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_PATH: Path = BASE_DIR / "data" / "dados_sinteticos.csv"
OUTPUT_PATH: Path = BASE_DIR / "data" / "cluster_profiles.json"

# Mapeamento ordinal de frequência de compra
ORDEM_FREQUENCIA: dict[str, int] = {
    "trimestral": 1,
    "bimestral": 2,
    "mensal": 3,
    "quinzenal": 4,
    "semanal": 5,
}

# Faixas etárias (intervalos de 5 anos)
BINS_IDADE: list[int] = [0, 18, 25, 40, 55, 70, 120]
LABELS_IDADE: list[str] = [
    '<18', '18-25', '25-40', '40-55', '55-70', '70+'
]

# Categóricas para análise
CATEGORICAS_VIZ: list[str] = [
    "canal_preferido", "categoria_favorita", "regiao",
    "frequencia_compra", "pagamento", "genero",
]

# Nomes amigáveis para os segmentos do quadrante RFM
NOMES_PLANTILHA: dict[int, str] = {
    0: "Cliente VIP Fiel",
    1: "Comprador Premium",
    2: "Comprador Ocasional",
    3: "Cliente Popular",
}


def carregar_dados(caminho: Path) -> pd.DataFrame:
    """Carrega o CSV e retorna o DataFrame bruto."""
    df: pd.DataFrame = pd.read_csv(caminho)
    print(f"📊 Dataset: {df.shape[0]} linhas × {df.shape[1]} colunas")
    return df


def tratar_dados(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Trata dados categóricos e engenharia de features.

    Retorna:
        df_original: DataFrame original com coluna 'idade' e 'faixa_etaria'
        df_encoded: DataFrame codificado pronto para clustering
    """
    df_orig: pd.DataFrame = df.copy()
    df_proc: pd.DataFrame = df.copy()

    # 0. Correção: qtd_itens == 0 com ticket_medio != 0 → qtd_itens = 1
    mascara_correcao: pd.Series = (df_proc["qtd_itens"] == 0) & (df_proc["ticket_medio"] != 0)
    n_corrigidos: int = int(mascara_correcao.sum())
    df_proc.loc[mascara_correcao, "qtd_itens"] = 1
    df_orig.loc[mascara_correcao, "qtd_itens"] = 1
    print(f"🔧 Corrigidos {n_corrigidos} registros com qtd_itens=0 e ticket>0 → qtd_itens=1")

    # 1. data_nascimento → idade → faixa_etaria
    df_proc["data_nascimento"] = pd.to_datetime(
        df_proc["data_nascimento"], format="%d/%m/%Y", errors="coerce"
    )
    data_ref: datetime = datetime(2026, 5, 25)
    df_proc["idade"] = ((data_ref - df_proc["data_nascimento"]).dt.days / 365.25).astype(int)

    # Usar faixa etária (categórica) ao invés de idade bruta para clustering
    df_proc["faixa_etaria"] = pd.cut(
        df_proc["idade"], bins=BINS_IDADE, labels=LABELS_IDADE, right=False
    )
    df_proc.drop(columns=["data_nascimento", "idade"], inplace=True)

    # Adicionar idade ao original (para profiling)
    df_orig["data_nascimento_dt"] = pd.to_datetime(
        df_orig["data_nascimento"], format="%d/%m/%Y", errors="coerce"
    )
    df_orig["idade"] = ((data_ref - df_orig["data_nascimento_dt"]).dt.days / 365.25).astype(int)
    df_orig["faixa_etaria"] = pd.cut(
        df_orig["idade"], bins=BINS_IDADE, labels=LABELS_IDADE, right=False
    )

    # 2. Frequência ordinal
    df_proc["frequencia_ordinal"] = df_proc["frequencia_compra"].map(ORDEM_FREQUENCIA)

    # 3. Frequency encoding para marca_preferida
    freq_marca: pd.Series = df_proc["marca_preferida"].value_counts(normalize=True)
    df_proc["marca_freq"] = df_proc["marca_preferida"].map(freq_marca)

    # 4. Remover colunas desnecessárias
    df_proc.drop(
        columns=["influenciador", "frequencia_compra", "marca_preferida", "marca_freq"],
        inplace=True,
    )

    # 5. One-Hot Encoding (inclui faixa_etaria no lugar de idade bruta)
    colunas_onehot: list[str] = [
        "canal_preferido", "categoria_favorita", "regiao", "pagamento", "genero",
        "faixa_etaria",
    ]
    df_encoded: pd.DataFrame = pd.get_dummies(
        df_proc, columns=colunas_onehot, drop_first=False, dtype=int
    )

    # 6. Padronizar numéricas
    colunas_num: list[str] = ["ticket_medio", "qtd_itens", "frequencia_ordinal"]
    scaler: StandardScaler = StandardScaler()
    df_encoded[colunas_num] = scaler.fit_transform(df_encoded[colunas_num])

    print(f"✅ Features: {df_encoded.shape[1]} colunas após encoding")
    return df_orig, df_encoded


def segmentar_quadrantes(df: pd.DataFrame) -> np.ndarray:
    """Implementa a segmentação híbrida por quadrantes (RFM Simplificado).

    Mapeia os eixos de Frequência e Ticket Médio utilizando a mediana como corte:
    - Cluster 0: Cliente VIP Fiel (Frequência Alta + Ticket Alto)
    - Cluster 1: Comprador Premium (Frequência Baixa + Ticket Alto)
    - Cluster 2: Comprador Ocasional (Frequência Baixa + Ticket Baixo)
    - Cluster 3: Cliente Popular (Frequência Alta + Ticket Baixo)
    """
    df_temp = df.copy()
    df_temp["frequencia_ordinal"] = df_temp["frequencia_compra"].map(ORDEM_FREQUENCIA)

    # Cortes baseados na mediana dos dados
    corte_ticket = df_temp["ticket_medio"].median()
    corte_freq = df_temp["frequencia_ordinal"].median()

    print(f"📈 Limiares de corte (Medianas):")
    print(f"   • Ticket Médio: R$ {corte_ticket:.2f}")
    print(f"   • Frequência Ordinal: {corte_freq:.1f} (Corte entre mensal e quinzenal)")

    labels = np.zeros(len(df_temp), dtype=int)

    # Definição das regras de negócio para cada quadrante
    vip_fiel = (df_temp["ticket_medio"] >= corte_ticket) & (df_temp["frequencia_ordinal"] >= corte_freq)
    premium = (df_temp["ticket_medio"] >= corte_ticket) & (df_temp["frequencia_ordinal"] < corte_freq)
    ocasional = (df_temp["ticket_medio"] < corte_ticket) & (df_temp["frequencia_ordinal"] < corte_freq)
    popular = (df_temp["ticket_medio"] < corte_ticket) & (df_temp["frequencia_ordinal"] >= corte_freq)

    labels[vip_fiel] = 0
    labels[premium] = 1
    labels[ocasional] = 2
    labels[popular] = 3

    return labels


def construir_perfis(
    df: pd.DataFrame, labels: np.ndarray, X: np.ndarray
) -> dict:
    """Constrói o dicionário de perfis dos clusters para exportação JSON."""
    df["cluster"] = labels

    colunas_medias: list[str] = ["ticket_medio", "qtd_itens", "idade"]
    categoricas: list[str] = CATEGORICAS_VIZ + ["faixa_etaria"]

    profiles: list[dict] = []
    for cluster_id in sorted(df["cluster"].unique()):
        grupo: pd.DataFrame = df[df["cluster"] == cluster_id]

        perfil: dict = {
            "cluster_id": int(cluster_id),
            "nome_segmento": NOMES_PLANTILHA[cluster_id],
            "tamanho": int(len(grupo)),
            "percentual": round(len(grupo) / len(df) * 100, 1),
            "numericas": {},
            "categoricas": {},
        }

        # Numéricas
        for col in colunas_medias:
            perfil["numericas"][col] = {
                "media": round(float(grupo[col].mean()), 2),
                "mediana": round(float(grupo[col].median()), 2),
                "std": round(float(grupo[col].std()), 2),
                "min": round(float(grupo[col].min()), 2),
                "max": round(float(grupo[col].max()), 2),
            }

        # Categóricas
        for col in categoricas:
            dist: pd.Series = grupo[col].value_counts(normalize=True).round(4)
            perfil["categoricas"][col] = {
                "moda": str(dist.index[0]),
                "moda_pct": round(float(dist.iloc[0]) * 100, 1),
                "distribuicao": {
                    str(k_val): round(float(v) * 100, 1) for k_val, v in dist.items()
                },
            }

        profiles.append(perfil)

    output: dict = {
        "metadata": {
            "algoritmo": "Segmentação Híbrida RFM (Quadrantes)",
            "n_clusters": 4,
            "silhouette_score": round(float(silhouette_score(X, labels)), 4),
            "calinski_harabasz": round(float(calinski_harabasz_score(X, labels)), 2),
            "davies_bouldin": round(float(davies_bouldin_score(X, labels)), 4),
            "total_amostras": int(len(df)),
            "data_geracao": datetime.now().isoformat(),
        },
        "clusters": profiles,
    }

    return output


def executar_pipeline() -> None:
    """Executa o pipeline completo de clustering."""
    print("=" * 50)
    print("  🌌 GALAXIES — Pipeline de Clustering (Híbrido)")
    print("=" * 50)

    # 1. Carregar dados
    df_raw: pd.DataFrame = carregar_dados(DATA_PATH)

    # 2. Tratar e codificar
    df_original, df_encoded = tratar_dados(df_raw)
    X: np.ndarray = df_encoded.values

    # 3. Executar segmentação por quadrantes
    labels: np.ndarray = segmentar_quadrantes(df_original)

    # 4. Construir perfis
    perfis: dict = construir_perfis(df_original, labels, X)

    # 5. Exportar JSON
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(perfis, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Perfis exportados: {OUTPUT_PATH}")
    print(f"   4 clusters | Quadrantes RFM | Sil={perfis['metadata']['silhouette_score']}")
    print("=" * 50)


if __name__ == "__main__":
    executar_pipeline()
