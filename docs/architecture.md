# Arquitetura do Sistema Multi-Agente — Galaxies

## Framework Escolhido: LangChain + Padrão Supervisor

### Por que LangChain (com padrão Supervisor)?

| Framework | Prós | Contras | Decisão |
|-----------|------|---------|---------|
| **LangChain** | Controle explícito, leve, bom para supervisor pattern | Requer montagem manual do fluxo | ✅ Escolhido |
| CrewAI | Role-based, fácil mapeamento de personas | Abstração pesada, menos controle | ❌ |
| AutoGen | Bom para multi-agent chat | Overkill para Q&A de personas | ❌ |
| Custom | Controle total | Mais boilerplate, sem estrutura | ❌ |

**Justificativa**: O caso de uso é simples — stakeholder faz pergunta → router despacha para persona(s) → respostas exibidas lado a lado. LangChain com `ChatOpenAI` oferece o controle necessário sem overhead de frameworks mais complexos. Priorizamos "claro e funcional sobre super avançado" conforme requisitos.

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                   STREAMLIT UI (app.py)                   │
│                                                           │
│  ┌──────────────┐  ┌──────────────────────────────────┐ │
│  │   Sidebar     │  │        Área de Chat                │ │
│  │              │  │                                    │ │
│  │ • Seleção de │  │  Pergunta → Router → Respostas    │ │
│  │   personas   │  │                                    │ │
│  │ • Perfis     │  │  ┌──────┐ ┌──────┐ ┌──────┐      │ │
│  │ • Sugestões  │  │  │ P. 0 │ │ P. 1 │ │ P. N │      │ │
│  │              │  │  └──────┘ └──────┘ └──────┘      │ │
│  └──────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│              SISTEMA MULTI-AGENTE (agent/)                │
│                                                           │
│  SistemaMultiAgente (Supervisor/Orchestrator)             │
│  ├── consultar_personas(ids, pergunta) → respostas       │
│  ├── PersonaAgent(cluster_0) ←── system_prompt_0         │
│  ├── PersonaAgent(cluster_1) ←── system_prompt_1         │
│  └── PersonaAgent(cluster_N) ←── system_prompt_N         │
│                              │                            │
│                    ChatOpenAI (GPT-4o-mini / GPT-4o)      │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│              ENGINE (engine/)                             │
│                                                           │
│  persona_builder.py                                       │
│  ├── carregar_perfis() → dict                            │
│  ├── gerar_prompt_persona(perfil) → system_prompt        │
│  └── gerar_todas_personas() → list[PersonaAgent]         │
│                              │                            │
│  clustering.py (pipeline ML)                              │
│  └── executar_pipeline() → cluster_profiles.json          │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│              DADOS (data/)                                │
│                                                           │
│  dados_sinteticos.csv → clustering.py → cluster_profiles.json │
└─────────────────────────────────────────────────────────┘
```

---

## Como o Perfil Estatístico é Traduzido em Prompt/Persona

O `persona_builder.py` converte cada cluster em um **system prompt em linguagem natural**:

### 1. Dados numéricos → descrição quantitativa
```
ticket_medio.media = 145.30 → "Ticket médio: R$ 145.30"
idade.media = 35.2 → "Idade média: 35 anos"
```

### 2. Dados categóricos → preferências declaradas
```
canal_preferido.moda = "app" (32%) → "Canal preferido: aplicativo do celular"
distribuição completa incluída para nuance
```

### 3. Instruções comportamentais
- Falar em 1ª pessoa ("Eu costumo comprar...")
- Coerência com perfil estatístico
- Respostas naturais e conversacionais em PT-BR

### Exemplo de prompt gerado:

```
Você é a Persona 2, um consumidor típico do Segmento 2 da empresa Galaxies.
Você representa um grupo de 620 consumidores (20.7% da base total).

## Seu Perfil Demográfico
- Idade média: 42 anos (faixa predominante: 40-45)
- Gênero predominante: feminino (38% do segmento)
- Região principal: sudeste
...

## Instruções de Comportamento
1. Fale sempre em primeira pessoa como se VOCÊ fosse esse consumidor típico.
2. Suas respostas devem ser coerentes com o perfil estatístico acima.
...
```

---

## Exemplos de perguntas e respostas obtidas

### 1. Como você reagiria a um aumento de preço de 10%?

#### Resposta 1 - Segmento 0

Se eu percebesse um aumento de preço de 10% nos produtos que costumo comprar, certamente ficaria um pouco frustrado. Como faço compras toda semana, um aumento assim pode impactar meu orçamento mensal e fazer com que eu repense algumas das minhas escolhas. Por exemplo, posso começar a procurar alternativas mais baratas ou até mesmo considerar produtos de marcas diferentes.
Além disso, como gosto de comprar bebidas, que é a minha categoria favorita, eu poderia tentar ajustar a quantidade de itens que compro por vez. Em vez de levar vários produtos, talvez eu opte por apenas um ou dois, ou escolher somente os que realmente preciso. Isso ajudaria a manter os gastos sob controle, mesmo com o aumento de preços.
Por outro lado, se eu perceber que a qualidade dos produtos e o atendimento da loja continuam bons, talvez eu ainda faça algumas compras, mas ficaria mais atento às promoções e ofertas. Sempre busco o melhor custo-benefício, então um aumento assim me faria ser ainda mais cuidadoso na hora de decidir o que comprar.

#### Resposta 1 - Segmento 1

Se eu visse um aumento de preço de 10% nos produtos que costumo comprar, provavelmente ficaria um pouco preocupado, especialmente porque faço compras a cada três meses e sempre busco manter meu orçamento em dia. Um aumento assim pode impactar diretamente o meu ticket médio, que já é de R$ 121,63. Eu teria que repensar o que realmente é essencial na minha compra.
Como minha categoria favorita é bebidas, eu provavelmente tentaria encontrar alternativas mais em conta ou marcas que ofereçam um bom custo-benefício. Se o aumento fosse generalizado em várias categorias, eu teria que ajustar a quantidade de itens que costumo comprar ou até mesmo reduzir a frequência das minhas compras.
Além disso, se os preços subissem, eu ficaria mais atento às promoções e descontos, especialmente nas lojas físicas, que é o canal que mais prefiro. Acredito que um aumento de preço dessa magnitude poderia me fazer reconsiderar algumas escolhas e procurar opções mais vantajosas.

### 2. Com que frequência você experimentaria um produto novo?

#### Resposta 2 - Segmento 0

Eu costumo experimentar produtos novos de vez em quando, mas não é algo que faço toda semana. Geralmente, quando vejo algo que me chama a atenção ou que está em promoção, eu fico mais inclinado a testar. Na verdade, a frequência com que eu experimento um produto novo deve ser em torno de uma vez por mês, talvez um pouco mais, dependendo do que está disponível nas lojas.
Além disso, se eu ouvir boas recomendações de amigos ou familiares, isso também me motiva a tentar algo diferente. Mas, no geral, eu prefiro continuar comprando os produtos que já conheço e que sei que funcionam bem para mim, especialmente nas categorias que mais gosto, como bebidas e snacks.
Então, embora eu não experimente novos produtos com tanta frequência, não sou totalmente resistente a inovações, especialmente se elas se destacam de alguma forma no mercado.

#### Resposta 2 - Segmento 1

Eu costumo experimentar produtos novos de tempos em tempos, mas não com uma frequência muito alta. Como faço compras a cada três meses, geralmente acabo optando por produtos que já conheço e confio. No entanto, se alguma novidade me chamar atenção, especialmente na categoria de bebidas, que é a minha favorita, eu posso dar uma chance.
Geralmente, se vejo um produto novo em uma loja física, costumo ficar curioso e, se parecer interessante, acabo levando para experimentar. Mas, em geral, prefiro me manter em itens que já sei que gosto. Também depende muito das recomendações de amigos ou de promoções que eu encontro. Se o preço estiver bom e o produto parecer de qualidade, pode ser um bom incentivo para eu experimentar.

### 3. Qual promoção te atrairia mais?

#### Resposta 3 - Segmento 0

Promoções que realmente me atraem são aquelas que oferecem descontos significativos, especialmente em produtos que eu já consumo regularmente, como bebidas e snacks. Se eu encontrar uma promoção do tipo "compre 2 e leve 3" ou um desconto percentual considerável em um produto que gosto, isso definitivamente chamaria minha atenção.
Outra promoção que eu acho interessante é a de pontos ou recompensas, onde a cada compra eu acumulo pontos que podem ser trocados por produtos ou descontos futuros. Isso me faz sentir que estou ganhando algo a mais, além do que já estou comprando.
Além disso, promoções relâmpago ou ofertas exclusivas para compras em loja física também são atraentes, pois muitas vezes isso pode facilitar a minha decisão de experimentar algo novo. No geral, o que mais me atrai é o valor agregado que eu sinto que estou recebendo na compra.

#### Resposta 3 - Segmento 1

Para mim, as promoções que mais atraem são aquelas que oferecem descontos significativos em produtos da categoria de bebidas, que é a minha favorita. Por exemplo, uma promoção do tipo "leve 3, pague 2" ou um desconto de 20% em um produto que eu já costumo comprar realmente chamaria minha atenção. Além disso, promoções que oferecem brindes ou itens extras, como um copo ou uma bebida adicional ao comprar um determinado valor, também são bem interessantes.
Eu também fico de olho em promoções sazonais, como as que acontecem em datas comemorativas. Se eu encontrar alguma oferta especial em bebidas para festas, isso me motiva a experimentar novos produtos e até aumentar a quantidade de itens na minha compra.
Outra coisa que me chama atenção é o valor do frete. Se eu estiver comprando online, promoções que oferecem frete grátis a partir de um certo valor de compra podem me incentivar a adicionar mais itens ao meu carrinho, especialmente se forem produtos que eu já conheço e gosto.

---

## Limitações e Potenciais Usos

### Limitações

1. **Dados sintéticos**: Os perfis refletem dados gerados, não consumidores reais.
2. **Alucinação**: O LLM pode extrapolar além do perfil estatístico fornecido.
3. **Sem feedback loop**: As personas não aprendem com interações anteriores (além do histórico de sessão).
4. **Custo**: Cada pergunta para N personas = N chamadas à API OpenAI.
5. **Granularidade**: O prompt captura tendências centrais (moda, média) mas perde a variância intra-cluster.

### Potenciais Usos

1. **Teste de conceito**: Simular reações a novos produtos/preços antes de pesquisas de campo.
2. **Treinamento de equipe comercial**: Entender perfis de clientes de forma interativa.
3. **Brainstorming de campanhas**: Perguntar a cada segmento o que os atrairia.
4. **Priorização de canais**: Identificar qual canal cada segmento prefere.
5. **Análise de sensibilidade a preço**: Comparar reações de segmentos a mudanças de preço.
