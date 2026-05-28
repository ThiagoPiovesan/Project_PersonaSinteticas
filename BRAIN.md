# BRAIN — Galaxies

> Sistema multi-agente de segmentação de consumidores via clustering + personas conversacionais.

---

## Visão Geral

Projeto para a empresa Galaxies: segmentar consumidores via análise de clusters (ML) e criar agentes que personificam cada segmento, permitindo que stakeholders façam perguntas de negócio em linguagem natural.

## Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| ML / Notebook | Python, pandas, scikit-learn, Google Colab |
| Agentic | LangGraph, LangChain, OpenAI GPT-4o-mini/4o |
| Interface | Streamlit |
| Pacotes | UV (local) |
| Linguagem docs | Português PT-BR |

## Dados

- **Arquivo**: `data/dados_sinteticos.csv`
- **Linhas**: 3.001 (header + 3.000 registros)
- **Colunas**: 11

| Coluna | Tipo | Únicos | Notas |
|--------|------|--------|-------|
| canal_preferido | Categórica | 5 | loja_fisica, parceiros, app, ecommerce, whatsapp |
| categoria_favorita | Categórica | 6 | bebidas, snacks, limpeza, mercearia, higiene, laticinios |
| regiao | Categórica | 5 | sudeste, sul, norte, centro_oeste, nordeste |
| marca_preferida | Categórica | 60 | marca_00..marca_59 (alta cardinalidade) |
| influenciador | Categórica | 120 | influencer_000..influencer_119 (alta cardinalidade) |
| frequencia_compra | Categórica/Ordinal | 5 | semanal, quinzenal, mensal, bimestral, trimestral |
| pagamento | Categórica | 5 | credito, boleto, carteira_digital, debito, pix |
| genero | Categórica | 4 | masculino, feminino, outro, nao_informado |
| ticket_medio | Numérica | ~2995 | Range: 10–253, Média: ~122 |
| qtd_itens | Numérica | 13 | Range: 0–12, Média: ~4 |
| data_nascimento | Data | ~2766 | DD/MM/YYYY → derivar `idade` |

## Arquitetura Multi-Agente

**Padrão**: Supervisor/Orchestrator (via LangGraph)

```
Stakeholder → Streamlit UI → Router Agent → [Persona 1, Persona 2, ..., Persona N] → Respostas lado a lado
```

- Cada cluster gera um agente-persona que fala em 1ª pessoa
- O Router direciona perguntas para persona(s) selecionada(s)
- Personas são construídas proceduralmente a partir do perfil estatístico do cluster

## Decisões de Projeto

- **Segmentação Híbrida RFM (Quadrantes)**: Substituição de KMeans/GMM puramente estatístico por segmentação híbrida utilizando os eixos `ticket_medio` e `frequencia_compra` com limiares estatísticos (mediana). Isso garante quadrantes mutuamente exclusivos e personas de negócio extremamente claras:
  - **Cluster 0**: Cliente VIP Fiel (Frequência Alta + Ticket Alto)
  - **Cluster 1**: Comprador Premium (Frequência Baixa + Ticket Alto)
  - **Cluster 2**: Comprador Ocasional (Frequência Baixa + Ticket Baixo)
  - **Cluster 3**: Cliente Popular (Frequência Alta + Ticket Baixo)
- **Faixas etárias**: Utilização de faixas etárias agregadas (18-20, 20-25, ..., 70+) no pipeline de encoding/clustering no lugar da idade contínua para maior interpretabilidade.
- **Correção de Dados**: Correção de anomalias na base: registros com `qtd_itens == 0` mas `ticket_medio > 0` foram limpos e ajustados para `qtd_itens = 1`.
- **LLM**: OpenAI GPT-4o-mini (custo) ou GPT-4o (qualidade).
- **Framework**: LangGraph / LangChain com padrão Supervisor/Orchestrator leve.
- **Apresentação executiva**: Fase futura (follow-up).

## Estrutura do Projeto

```
Galaxies/
├── agent/         # Sistema multi-agente (LangGraph)
├── data/          # Dados sintéticos
├── docs/          # Documentação e relatórios
├── engine/        # Construção de personas
├── knowledge/     # Descrição do problema
├── notebook/      # Google Colab notebook (ML)
├── app.py         # Interface Streamlit
├── main.py        # Entry point
└── BRAIN.md       # Este arquivo
```
