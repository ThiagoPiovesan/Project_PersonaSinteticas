"""🌌 Galaxies — Interface Streamlit para o Sistema Multi-Agente.

Interface para stakeholders interagirem com personas de consumidores:
- Selecionar persona(s) para conversar
- Fazer perguntas de negócio
- Visualizar respostas lado a lado

Uso: uv run streamlit run app.py
"""

import json
from pathlib import Path

import streamlit as st

# --- Configuração da página ---
st.set_page_config(
    page_title="Galaxies — Personas de Consumidores",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS customizado ---
st.markdown("""
<style>
    /* Fundo e tipografia */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* Cards de resposta */
    .persona-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
    }

    .persona-header {
        font-size: 1.2em;
        font-weight: 700;
        color: #a29bfe;
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(162, 155, 254, 0.3);
        padding-bottom: 8px;
    }

    .persona-meta {
        font-size: 0.85em;
        color: #b2bec3;
        margin-bottom: 12px;
    }

    .persona-response {
        color: #dfe6e9;
        line-height: 1.7;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95);
    }

    /* Input */
    .stChatInput > div {
        border-color: rgba(162, 155, 254, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# Funções auxiliares
# ============================================

BASE_DIR: Path = Path(__file__).resolve().parent
PROFILES_PATH: Path = BASE_DIR / "data" / "cluster_profiles.json"


@st.cache_data
def carregar_perfis() -> dict | None:
    """Carrega perfis de cluster do JSON (com cache).

    Returns:
        Dicionário com metadados e clusters, ou None se não existir.
    """
    if not PROFILES_PATH.exists():
        return None
    with open(PROFILES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def inicializar_sistema():
    """Inicializa o SistemaMultiAgente (lazy, uma vez por sessão)."""
    if "sistema" not in st.session_state:
        try:
            from agent.agents import SistemaMultiAgente
            st.session_state.sistema = SistemaMultiAgente()
            st.session_state.sistema_ok = True
        except (ValueError, FileNotFoundError) as e:
            st.session_state.sistema = None
            st.session_state.sistema_ok = False
            st.session_state.erro_sistema = str(e)


def inicializar_historicos(n_clusters: int) -> None:
    """Inicializa históricos de conversa por persona."""
    if "historicos" not in st.session_state:
        st.session_state.historicos = {i: [] for i in range(n_clusters)}
    if "mensagens_chat" not in st.session_state:
        st.session_state.mensagens_chat = []


# ============================================
# Layout principal
# ============================================

def main() -> None:
    """Função principal da interface Streamlit."""
    # Título
    st.markdown("# 🌌 Galaxies")
    st.markdown("### Sistema Multi-Agente de Personas de Consumidores")
    st.markdown("---")

    # Verificar se perfis existem
    perfis: dict | None = carregar_perfis()

    if perfis is None:
        st.error(
            "⚠️ **Perfis de cluster não encontrados.**\n\n"
            "Execute o pipeline de clustering primeiro:\n"
            "```bash\n"
            "uv run python -m engine.clustering\n"
            "```"
        )
        return

    metadata: dict = perfis["metadata"]
    clusters: list[dict] = perfis["clusters"]

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("## ⚙️ Configuração")

        # Informações do clustering
        st.markdown("### 📊 Clustering")
        st.markdown(f"**Algoritmo:** {metadata['algoritmo']}")
        st.markdown(f"**Clusters:** {metadata['n_clusters']}")
        st.markdown(f"**Silhouette:** {metadata['silhouette_score']:.4f}")
        st.markdown(f"**Amostras:** {metadata['total_amostras']}")
        st.markdown("---")

        # Seleção de personas
        st.markdown("### 🎭 Selecionar Personas")

        selecionar_todas: bool = st.checkbox(
            "Todas as personas", value=True, key="sel_todas"
        )

        personas_selecionadas: list[int] = []

        if selecionar_todas:
            personas_selecionadas = [c["cluster_id"] for c in clusters]
        else:
            for cluster in clusters:
                cid: int = cluster["cluster_id"]
                nome_seg: str = cluster.get("nome", "")
                label: str = (
                    f"Persona {cid} ({nome_seg}) — "
                    f"{cluster['tamanho']} consumidores "
                    f"({cluster['percentual']}%)"
                )
                if st.checkbox(label, value=False, key=f"sel_{cid}"):
                    personas_selecionadas.append(cid)

        st.markdown("---")

        # Perfil resumido
        if len(personas_selecionadas) > 0:
            st.markdown("### 📋 Perfil Resumido")
            for cid in personas_selecionadas:
                cluster_data: dict = clusters[cid]
                nome_seg: str = cluster_data.get("nome", "")
                num: dict = cluster_data["numericas"]
                cat: dict = cluster_data["categoricas"]

                with st.expander(f"Persona {cid} ({nome_seg})", expanded=False):
                    st.markdown(f"**Tamanho:** {cluster_data['tamanho']} ({cluster_data['percentual']}%)")
                    st.markdown(f"**Ticket médio:** R$ {num['ticket_medio']['media']:.2f}")
                    st.markdown(f"**Idade média:** {num['idade']['media']:.0f} anos")
                    st.markdown(f"**Canal:** {cat['canal_preferido']['moda']}")
                    st.markdown(f"**Categoria:** {cat['categoria_favorita']['moda']}")
                    st.markdown(f"**Frequência:** {cat['frequencia_compra']['moda']}")
                    st.markdown(f"**Pagamento:** {cat['pagamento']['moda']}")
                    st.markdown(f"**Região:** {cat['regiao']['moda']}")
                    st.markdown(f"**Gênero:** {cat['genero']['moda']}")

        st.markdown("---")

        # Limpar conversa
        if st.button("🗑️ Limpar Conversa", use_container_width=True):
            st.session_state.historicos = {
                i: [] for i in range(metadata["n_clusters"])
            }
            st.session_state.mensagens_chat = []
            st.rerun()

        # Sugestões de perguntas
        st.markdown("### 💡 Perguntas Sugeridas")
        perguntas_sugeridas: list[str] = [
            "Como você reagiria a um aumento de preço de 10%?",
            "O que te faria trocar de canal de compra?",
            "Qual promoção te atrairia mais?",
            "Com que frequência você experimentaria um produto novo?",
            "O que te faz escolher uma marca em vez de outra?",
        ]
        for pergunta in perguntas_sugeridas:
            if st.button(f"📝 {pergunta}", key=f"sug_{hash(pergunta)}", use_container_width=True):
                st.session_state.pergunta_sugerida = pergunta
                st.rerun()

    # --- Área principal ---

    # Inicializar sistema
    inicializar_sistema()
    inicializar_historicos(metadata["n_clusters"])

    if not st.session_state.get("sistema_ok", False):
        st.warning(
            f"⚠️ **Sistema não inicializado:**\n\n"
            f"{st.session_state.get('erro_sistema', 'Erro desconhecido')}\n\n"
            "Configure o `.env` com sua `OPENAI_API_KEY`."
        )
        # Mostrar modo de visualização apenas
        st.info("📊 **Modo visualização:** Você pode explorar os perfis na sidebar.")
        return

    if not personas_selecionadas:
        st.info("👈 Selecione pelo menos uma persona na sidebar para começar.")
        return

    # Exibir histórico de mensagens
    for msg in st.session_state.mensagens_chat:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["content"])
        else:
            # Exibir respostas em colunas
            _exibir_respostas(msg["respostas"])

    # Input de pergunta
    pergunta_sugerida: str = st.session_state.pop("pergunta_sugerida", "")

    pergunta: str | None = st.chat_input(
        "Faça uma pergunta de negócio para as personas...",
        key="chat_input",
    )

    # Usar pergunta sugerida se disponível
    if pergunta_sugerida and not pergunta:
        pergunta = pergunta_sugerida

    if pergunta:
        # Exibir pergunta do usuário
        st.chat_message("user").markdown(pergunta)

        # Consultar personas selecionadas
        with st.spinner("🤔 Personas pensando..."):
            sistema = st.session_state.sistema
            respostas: list[dict[str, str]] = sistema.consultar_personas(
                personas_selecionadas,
                pergunta,
                st.session_state.historicos,
            )

        # Exibir respostas
        _exibir_respostas(respostas)

        # Salvar no histórico
        st.session_state.mensagens_chat.append(
            {"role": "user", "content": pergunta}
        )
        st.session_state.mensagens_chat.append(
            {"role": "assistant", "respostas": respostas}
        )

        # Atualizar históricos individuais
        for resp in respostas:
            # Extrair cluster_id robustamente (ex: de "Persona 0 (VIP)" ou "Persona 0")
            import re
            match = re.search(r"Persona\s+(\d+)", resp["nome"])
            cid_int: int = int(match.group(1)) if match else 0
            st.session_state.historicos[cid_int].append(
                {"role": "user", "content": pergunta}
            )
            st.session_state.historicos[cid_int].append(
                {"role": "assistant", "content": resp["resposta"]}
            )


def _exibir_respostas(respostas: list[dict[str, str]]) -> None:
    """Exibe respostas das personas lado a lado em colunas."""
    n_respostas: int = len(respostas)

    if n_respostas == 0:
        return

    # Até 4 colunas; se mais, dividir em linhas
    max_colunas: int = min(n_respostas, 4)

    for i in range(0, n_respostas, max_colunas):
        lote: list[dict] = respostas[i : i + max_colunas]
        colunas = st.columns(len(lote))

        for col, resp in zip(colunas, lote):
            with col:
                st.markdown(
                    f"""<div class="persona-card">
                        <div class="persona-header">🎭 {resp['nome']}</div>
                        <div class="persona-response">{resp['resposta']}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    main()
