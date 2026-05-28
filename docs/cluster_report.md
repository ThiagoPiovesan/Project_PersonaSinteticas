# Relatório de Clustering — Galaxies

> Documento gerado após execução do pipeline de clustering.
> Atualizar com resultados reais após rodar `uv run python -m engine.clustering`.

---

## 1. Quantidade de Clusters e Critério de Seleção

### Método de seleção
- **Elbow Method**: Análise da curva de inércia (KMeans)
- **Silhouette Score**: Métrica principal de decisão
- **BIC**: Critério bayesiano para GMM

### Algoritmos testados
1. **KMeans**: Clustering baseado em centróides, assume clusters esféricos
2. **GMM (Gaussian Mixture Models)**: Clustering probabilístico, permite clusters elípticos

### Range testado
- K de 2 a 10
- Seleção automática do melhor K via maior Silhouette Score

### Resultado
> ⏳ *Preencher após execução do pipeline*
>
> - **K selecionado**: ?
> - **Algoritmo final**: ?
> - **Silhouette Score**: ?
> - **Calinski-Harabasz**: ?
> - **Davies-Bouldin**: ?

---

## 2. Perfil Principal de Cada Cluster

> ⏳ *Tabela será preenchida com resultados reais*

| Cluster | Tamanho | Ticket Médio | Qtd Itens | Idade | Canal | Categoria | Região | Freq. Compra |
|---------|---------|-------------|-----------|-------|-------|-----------|--------|-------------|
| 0 | ? | ? | ? | ? | ? | ? | ? | ? |
| 1 | ? | ? | ? | ? | ? | ? | ? | ? |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## 3. Aplicações Potenciais para a Galaxies

### Marketing Segmentado
- Campanhas direcionadas por cluster com mensagens personalizadas
- Escolha de canais de comunicação baseada no canal preferido de cada segmento

### Estratégia de Preços
- Diferenciação de ofertas por faixa de ticket médio
- Sensibilidade a preço varia entre segmentos (validar com agentes)

### Expansão de Canais
- Investir nos canais preferidos dos segmentos mais rentáveis
- Identificar segmentos subatendidos em canais específicos

### Sortimento de Produtos
- Adequar mix de produtos à categoria favorita de cada segmento
- Cross-selling baseado em preferências de categoria

### Programa de Fidelidade
- Segmentos com alta frequência de compra: recompensas por volume
- Segmentos com baixa frequência: incentivos para aumento de visitas
