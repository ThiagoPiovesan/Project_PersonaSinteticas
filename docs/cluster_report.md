# Relatório de Clustering — Galaxies

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

> - **K selecionado**: 2
> - **Algoritmo final**: K-Means
> - **Silhouette Score**: 0.096 (K-Means) e 0.030 (GMM) respectivamente
> - **Calinski-Harabasz**: 334.76 (K-Means) e 2.9279 (GMM) respectivamente
> - **Davies-Bouldin**: 55.5711 (K-Means) e 5.1449 (GMM) respectivamente

Distribuição dos clusters:
  Cluster 0: 1273 consumidores (42.4%)
  Cluster 1: 1727 consumidores (57.6%)

---

## 2. Perfil Principal de Cada Cluster

| Cluster | Tamanho | Ticket Médio | Qtd Itens | Idade | Canal | Categoria | Região | Freq. Compra |
|---------|---------|-------------|-----------|-------|-------|-----------|--------|-------------|
| 0 | 1273 | R$ 122.07 | 4.07 | 44.1 | loja_fisica | bebidas | sudeste | semanal |
| 1 | 1727 | R$ 121.63 | 4.03 | 45.04 | loja_fisica | bebidas | sudeste | trimestral |

### Cluster 0 (1273 consumidores, 42.4%)

  Ticket médio: R$ 122.07 (mediana: R$ 122.87)
  Qtd itens: 4.07 (mediana: 4.0)
  Idade média: 44.1 anos (mediana: 44.0)
  Faixa etária principal: 25-40 (28.8%)
  Canal preferido: loja_fisica (25.1%)
  Categoria favorita: bebidas (20.7%)
  Região: sudeste (24.0%)
  Frequência compra: semanal (56.5%)
  Pagamento: credito (22.0%)
  Gênero predominante: masculino (27.1%)

### Cluster 1 (1727 consumidores, 57.6%)

  Ticket médio: R$ 121.63 (mediana: R$ 121.82)
  Qtd itens: 4.03 (mediana: 4.0)
  Idade média: 45.04 anos (mediana: 45.0)
  Faixa etária principal: 55-70 (31.2%)
  Canal preferido: loja_fisica (23.8%)
  Categoria favorita: bebidas (20.9%)
  Região: sudeste (22.9%)
  Frequência compra: trimestral (34.5%)
  Pagamento: credito (24.3%)
  Gênero predominante: masculino (30.6%)

---

## 3. Aplicações Potenciais para a Galaxies

### Marketing Segmentado

- Campanhas direcionadas por cluster com mensagens personalizadas
- Escolha de canais de comunicação baseada no canal preferido de cada segmento
- O agente de IA pode adotar tom e urgência distintos para cada perfil — conversacional e de reposição para o Ativo, consultivo e de impacto para o Esporádico
- Acionar o Cluster 1 com campanhas de reativação e incentivos de frequência, buscando migrar esses consumidores para um comportamento mais próximo ao do Cluster 0

### Estratégia de Preços

- O Cluster 0 sustenta demanda contínua enquanto o Cluster 1 pode gerar picos sazonais, permitindo estratégias de abastecimento diferenciadas

### Expansão de Canais

- Investir nos canais preferidos dos segmentos mais rentáveis
- Identificar segmentos subatendidos em canais específicos

### Sortimento de Produtos

- Adequar mix de produtos à categoria favorita de cada segmento
- Cross-selling baseado em preferências de categoria

### Programa de Fidelidade

- Segmentos com alta frequência de compra: recompensas por volume
- Segmentos com baixa frequência: incentivos para aumento de visitas
- Para o Cluster 0, programas de fidelidade e benefícios por volume fazem sentido, dado o padrão de compra recorrente
