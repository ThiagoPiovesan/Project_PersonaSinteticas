# 🌌 Galaxies — Sistema Multi-Agente de Segmentação de Consumidores

Sistema que combina **análise de clusters (ML)** com **agentes conversacionais (LLM)** para segmentar consumidores e permitir que stakeholders interajam com as personas de cada segmento.

---

## 📋 Visão Geral

1. **Parte 1 (ML)**: Pipeline de clustering que segmenta 3.000 consumidores em clusters distintos usando KMeans e GMM.
2. **Parte 2 (Agentes)**: Cada cluster se torna um agente-persona que responde perguntas de negócio em 1ª pessoa.
3. **Interface**: Streamlit permite selecionar personas e comparar respostas lado a lado.

---

## 🚀 Setup Rápido

### Pré-requisitos

- Python 3.12+
- [UV](https://docs.astral.sh/uv/) (gerenciador de pacotes)
- Chave de API OpenAI

### 1. Instalar dependências

```bash
uv sync
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env e preencha OPENAI_API_KEY
```

### 3. Executar o pipeline de clustering

```bash
uv run python -m engine.clustering
```

Isso gera `data/cluster_profiles.json` com os perfis dos clusters.

### 4. Iniciar a interface Streamlit

```bash
uv run streamlit run app.py
```

Acesse: http://localhost:8501

---

## 📁 Estrutura do Projeto

```
Galaxies/
├── agent/                      # Sistema multi-agente
│   ├── __init__.py
│   ├── agents.py               # PersonaAgent + SistemaMultiAgente
│   └── config.py               # Configuração (env vars, caminhos)
├── data/
│   ├── dados_sinteticos.csv    # Dataset original (3.000 registros)
│   └── cluster_profiles.json   # Perfis gerados pelo clustering
├── docs/
│   ├── architecture.md         # Arquitetura e decisões técnicas
│   └── cluster_report.md       # Relatório de clustering
├── engine/
│   ├── __init__.py
│   ├── clustering.py           # Pipeline de clustering (versão local)
│   └── persona_builder.py      # Gerador de prompts de persona
├── knowledge/
│   ├── PROBLEM_DESC.md         # Descrição do problema
│   └── Case_Tecnico_ML_AI_Engineer.pdf
├── notebook/
│   └── galaxies_clustering.ipynb  # Notebook Colab (ML detalhado)
├── app.py                      # Interface Streamlit
├── main.py                     # Entry point
├── pyproject.toml              # Dependências (UV)
├── .env.example                # Template de variáveis de ambiente
├── BRAIN.md                    # Base de conhecimento do projeto
└── README.md                   # Este arquivo
```

---

## 🧠 Como Funciona

### Pipeline ML (Parte 1)

1. **Carregamento**: Dados sintéticos com 11 features (demográficas + compras)
2. **Tratamento**: Ordinal encoding (frequência), frequency encoding (marca), one-hot (demais)
3. **Feature Engineering**: Idade derivada de data_nascimento, faixas etárias de 5 anos
4. **Clustering**: KMeans + GMM, seleção de K via Silhouette Score
5. **Exportação**: `cluster_profiles.json` com perfil completo de cada cluster

### Sistema Multi-Agente (Parte 2)

1. **Persona Builder**: Lê perfis JSON e gera system prompts proceduralmente
2. **Agentes**: Cada persona responde em 1ª pessoa, coerente com seu perfil estatístico
3. **Supervisor**: Router despacha perguntas para persona(s) selecionada(s)
4. **Interface**: Streamlit com seleção de personas e respostas lado a lado

---

## 💬 Exemplos de Uso

### Perguntas de negócio para as personas:

- *"Como você reagiria a um aumento de preço de 10%?"*
- *"O que te faria trocar de canal de compra?"*
- *"Qual promoção te atrairia mais?"*
- *"Com que frequência você experimentaria um produto novo?"*
- *"O que te faz escolher uma marca em vez de outra?"*

---

## ⚙️ Configuração Avançada

### Variáveis de ambiente (.env)

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `OPENAI_API_KEY` | — | Chave da API OpenAI (obrigatório) |
| `LLM_MODEL` | `gpt-4o-mini` | Modelo: `gpt-4o-mini` ou `gpt-4o` |
| `LLM_TEMPERATURE` | `0.7` | Temperatura (0.0 = determinístico) |
| `LLM_MAX_TOKENS` | `1024` | Tokens máximos por resposta |

---

## 📄 Licença

Projeto — Case Técnico ML/AI Engineer para Galaxies.
