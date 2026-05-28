"""Construtor de personas a partir dos perfis de cluster.

Lê cluster_profiles.json e gera prompts de sistema para cada persona-agente.
Cada persona fala em 1ª pessoa como membro típico do seu segmento.
"""

import json
from pathlib import Path


# Caminho padrão do perfil de clusters
BASE_DIR: Path = Path(__file__).resolve().parent.parent
PROFILES_PATH: Path = BASE_DIR / "data" / "cluster_profiles.json"


def carregar_perfis(caminho: Path = PROFILES_PATH) -> dict:
    """Carrega os perfis de cluster do JSON exportado pelo pipeline ML.

    Args:
        caminho: Caminho para cluster_profiles.json.

    Returns:
        Dicionário com metadata e lista de clusters.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
    """
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}\n"
            "Execute primeiro: uv run python -m engine.clustering"
        )
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def _traduzir_frequencia(freq: str) -> str:
    """Traduz código de frequência para linguagem natural."""
    mapa: dict[str, str] = {
        "semanal": "toda semana",
        "quinzenal": "a cada duas semanas",
        "mensal": "uma vez por mês",
        "bimestral": "a cada dois meses",
        "trimestral": "a cada três meses",
    }
    return mapa.get(freq, freq)


def _traduzir_canal(canal: str) -> str:
    """Traduz código de canal para linguagem natural."""
    mapa: dict[str, str] = {
        "loja_fisica": "loja física",
        "ecommerce": "e-commerce (loja online)",
        "app": "aplicativo do celular",
        "whatsapp": "WhatsApp",
        "parceiros": "lojas parceiras",
    }
    return mapa.get(canal, canal)


def _traduzir_pagamento(pag: str) -> str:
    """Traduz código de pagamento para linguagem natural."""
    mapa: dict[str, str] = {
        "credito": "cartão de crédito",
        "debito": "cartão de débito",
        "pix": "Pix",
        "boleto": "boleto bancário",
        "carteira_digital": "carteira digital",
    }
    return mapa.get(pag, pag)


def _traduzir_genero(genero: str) -> str:
    """Traduz código de gênero para linguagem natural."""
    mapa: dict[str, str] = {
        "masculino": "masculino",
        "feminino": "feminino",
        "outro": "outro/não-binário",
        "nao_informado": "prefiro não informar",
    }
    return mapa.get(genero, genero)


def _formatar_distribuicao(dist: dict[str, float], tradutor=None) -> str:
    """Formata distribuição como texto legível.

    Args:
        dist: Dicionário {categoria: percentual}.
        tradutor: Função de tradução opcional.

    Returns:
        String formatada, ex: "loja física (28%), app (22%)".
    """
    itens: list[str] = []
    # Ordenar por percentual decrescente
    for cat, pct in sorted(dist.items(), key=lambda x: x[1], reverse=True):
        nome: str = tradutor(cat) if tradutor else cat
        itens.append(f"{nome} ({pct:.0f}%)")
    return ", ".join(itens)


def gerar_prompt_persona(perfil: dict, cluster_id: int) -> str:
    """Gera o system prompt para um agente-persona de cluster.

    O prompt é construído proceduralmente a partir do perfil estatístico,
    fazendo o agente "viver" como um consumidor típico daquele segmento.

    Args:
        perfil: Dicionário com o perfil de um cluster.
        cluster_id: ID do cluster (para nomear a persona).

    Returns:
        String do system prompt completo.
    """
    num: dict = perfil["numericas"]
    cat: dict = perfil["categoricas"]
    nome_seg: str = perfil.get("nome_segmento", f"Segmento {cluster_id}")

    # Dados demográficos
    idade_media: float = num["idade"]["media"]
    faixa: str = cat["faixa_etaria"]["moda"]
    genero_moda: str = _traduzir_genero(cat["genero"]["moda"])
    genero_pct: float = cat["genero"]["moda_pct"]
    regiao_moda: str = cat["regiao"]["moda"]
    regiao_dist: str = _formatar_distribuicao(cat["regiao"]["distribuicao"])

    # Hábitos de compra
    canal_moda: str = _traduzir_canal(cat["canal_preferido"]["moda"])
    canal_dist: str = _formatar_distribuicao(
        cat["canal_preferido"]["distribuicao"], _traduzir_canal
    )
    freq_moda: str = _traduzir_frequencia(cat["frequencia_compra"]["moda"])
    freq_dist: str = _formatar_distribuicao(
        cat["frequencia_compra"]["distribuicao"], _traduzir_frequencia
    )
    pagamento_moda: str = _traduzir_pagamento(cat["pagamento"]["moda"])
    pagamento_dist: str = _formatar_distribuicao(
        cat["pagamento"]["distribuicao"], _traduzir_pagamento
    )

    # Preferências
    categoria_moda: str = cat["categoria_favorita"]["moda"]
    categoria_dist: str = _formatar_distribuicao(
        cat["categoria_favorita"]["distribuicao"]
    )
    ticket: dict = num["ticket_medio"]
    qtd: dict = num["qtd_itens"]

    # Tamanho do segmento
    tamanho: int = perfil["tamanho"]
    percentual: float = perfil["percentual"]

    prompt: str = f"""Você é a Persona {cluster_id} ({nome_seg}), um consumidor típico do segmento "{nome_seg}" da empresa Galaxies.

Você representa um grupo de {tamanho} consumidores ({percentual}% da base total).

## Seu Perfil Demográfico
- Idade média: {idade_media:.0f} anos (faixa predominante: {faixa})
- Gênero predominante: {genero_moda} ({genero_pct:.0f}% do segmento)
- Região principal: {regiao_moda}
- Distribuição regional: {regiao_dist}

## Seus Hábitos de Compra
- Canal preferido: {canal_moda}
- Distribuição de canais: {canal_dist}
- Frequência de compra: {freq_moda}
- Distribuição de frequência: {freq_dist}
- Forma de pagamento preferida: {pagamento_moda}
- Distribuição de pagamento: {pagamento_dist}

## Suas Preferências de Produto
- Categoria favorita: {categoria_moda}
- Distribuição de categorias: {categoria_dist}
- Ticket médio: R$ {ticket['media']:.2f} (mediana R$ {ticket['mediana']:.2f}, variando de R$ {ticket['min']:.2f} a R$ {ticket['max']:.2f})
- Quantidade média de itens por compra: {qtd['media']:.1f} (de {qtd['min']} a {qtd['max']})

## Instruções de Comportamento

1. **Fale sempre em primeira pessoa** como se VOCÊ fosse esse consumidor típico.
2. Suas respostas devem ser **coerentes com o perfil estatístico** acima.
3. Quando perguntado sobre hábitos, preferências ou reações a cenários de negócio, responda baseando-se nos dados do seu perfil.
4. Seja **natural e conversacional**, como um consumidor real responderia.
5. Se perguntado sobre algo fora do seu perfil, responda de forma plausível mas coerente com suas características.
6. Nunca quebre o personagem — você É esse consumidor.
7. Responda sempre em **português brasileiro (PT-BR)**.
8. Mantenha respostas **concisas** (3-5 parágrafos no máximo).
"""
    return prompt.strip()


def gerar_todas_personas(caminho: Path = PROFILES_PATH) -> list[dict]:
    """Gera prompts para todas as personas a partir do arquivo de perfis.

    Returns:
        Lista de dicionários com:
            - cluster_id: int
            - nome: str (ex: "Persona 0 (Cliente VIP Fiel)")
            - tamanho: int
            - percentual: float
            - system_prompt: str
    """
    dados: dict = carregar_perfis(caminho)
    personas: list[dict] = []

    for perfil in dados["clusters"]:
        cid: int = perfil["cluster_id"]
        prompt: str = gerar_prompt_persona(perfil, cid)
        nome_seg: str = perfil.get("nome_segmento", f"Segmento {cid}")

        personas.append({
            "cluster_id": cid,
            "nome": f"Persona {cid} ({nome_seg})",
            "tamanho": perfil["tamanho"],
            "percentual": perfil["percentual"],
            "system_prompt": prompt,
        })
    print(f"✅ {len(personas)} personas geradas a partir de {caminho.name}")
    return personas


if __name__ == "__main__":
    # Teste: gerar e exibir prompts
    personas = gerar_todas_personas()
    for p in personas:
        print(f"\n{'='*60}")
        print(f"  {p['nome']} — {p['tamanho']} consumidores ({p['percentual']}%)")
        print(f"{'='*60}")
        print(p["system_prompt"][:500] + "...")
