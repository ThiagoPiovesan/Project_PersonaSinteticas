"""Sistema multi-agente Galaxies — LangGraph Supervisor/Orchestrator.

Arquitetura:
    Usuário → consultar_personas() → [Persona 0, Persona 1, ..., Persona N] → respostas

Cada persona é um nó do grafo com system prompt derivado do perfil do cluster.
O Router (supervisor) despacha a pergunta para persona(s) selecionada(s)
e coleta as respostas para exibição lado a lado.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from agent.config import (
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    OPENAI_API_KEY,
    PROFILES_PATH,
    validar_config,
)
from engine.persona_builder import gerar_todas_personas


@dataclass
class PersonaAgent:
    """Agente que representa um cluster/segmento de consumidores.

    Attributes:
        cluster_id: Identificador do cluster.
        nome: Nome amigável da persona (ex: "Persona 0").
        tamanho: Quantidade de consumidores no cluster.
        percentual: Percentual do cluster na base total.
        system_prompt: Prompt de sistema com o perfil do cluster.
        llm: Instância do modelo de linguagem.
    """

    cluster_id: int
    nome: str
    tamanho: int
    percentual: float
    system_prompt: str
    llm: ChatOpenAI = field(init=False)

    def __post_init__(self) -> None:
        """Inicializa o LLM após criação do dataclass."""
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            api_key=OPENAI_API_KEY,
        )

    def responder(self, pergunta: str) -> str:
        """Envia pergunta para a persona e retorna resposta.

        Args:
            pergunta: Pergunta do stakeholder em linguagem natural.

        Returns:
            Resposta da persona em 1ª pessoa.
        """
        mensagens = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=pergunta),
        ]
        resposta = self.llm.invoke(mensagens)
        return resposta.content

    def responder_com_historico(
        self, pergunta: str, historico: list[dict[str, str]]
    ) -> str:
        """Envia pergunta com histórico de conversa para contexto.

        Args:
            pergunta: Pergunta atual do stakeholder.
            historico: Lista de dicts {"role": "user"|"assistant", "content": "..."}.

        Returns:
            Resposta da persona considerando o histórico.
        """
        mensagens = [SystemMessage(content=self.system_prompt)]

        # Adicionar histórico
        for msg in historico:
            if msg["role"] == "user":
                mensagens.append(HumanMessage(content=msg["content"]))
            else:
                from langchain_core.messages import AIMessage
                mensagens.append(AIMessage(content=msg["content"]))

        # Pergunta atual
        mensagens.append(HumanMessage(content=pergunta))

        resposta = self.llm.invoke(mensagens)
        return resposta.content


class SistemaMultiAgente:
    """Orquestrador do sistema multi-agente Galaxies.

    Gerencia as personas e roteia perguntas conforme seleção do usuário.
    Implementa o padrão Supervisor/Orchestrator do multi-agent-patterns.

    Attributes:
        personas: Dicionário de PersonaAgent indexado por cluster_id.
        metadata: Metadados do clustering (algoritmo, métricas, etc).
    """

    def __init__(self) -> None:
        """Inicializa o sistema: valida config, carrega personas."""
        validar_config()
        self._carregar_personas()

    def _carregar_personas(self) -> None:
        """Carrega perfis de cluster e cria agentes-persona."""
        dados_personas: list[dict] = gerar_todas_personas(PROFILES_PATH)

        self.personas: dict[int, PersonaAgent] = {}
        for dados in dados_personas:
            agente = PersonaAgent(
                cluster_id=dados["cluster_id"],
                nome=dados["nome"],
                tamanho=dados["tamanho"],
                percentual=dados["percentual"],
                system_prompt=dados["system_prompt"],
            )
            self.personas[dados["cluster_id"]] = agente

        # Carregar metadata
        import json
        with open(PROFILES_PATH, "r", encoding="utf-8") as f:
            self.metadata: dict = json.load(f)["metadata"]

        print(f"✅ {len(self.personas)} agentes-persona carregados")

    def listar_personas(self) -> list[dict[str, Any]]:
        """Retorna lista resumida das personas disponíveis.

        Returns:
            Lista de dicts com cluster_id, nome, tamanho, percentual.
        """
        return [
            {
                "cluster_id": p.cluster_id,
                "nome": p.nome,
                "tamanho": p.tamanho,
                "percentual": p.percentual,
            }
            for p in self.personas.values()
        ]

    def consultar_persona(
        self, cluster_id: int, pergunta: str,
        historico: list[dict[str, str]] | None = None,
    ) -> dict[str, str]:
        """Consulta uma única persona.

        Args:
            cluster_id: ID do cluster/persona.
            pergunta: Pergunta do stakeholder.
            historico: Histórico de conversa (opcional).

        Returns:
            Dict com "nome" e "resposta".

        Raises:
            KeyError: Se cluster_id não existir.
        """
        if cluster_id not in self.personas:
            raise KeyError(f"Persona {cluster_id} não encontrada. "
                         f"Disponíveis: {list(self.personas.keys())}")

        agente: PersonaAgent = self.personas[cluster_id]

        if historico:
            resposta: str = agente.responder_com_historico(pergunta, historico)
        else:
            resposta = agente.responder(pergunta)

        return {"nome": agente.nome, "resposta": resposta}

    def consultar_personas(
        self, cluster_ids: list[int], pergunta: str,
        historicos: dict[int, list[dict[str, str]]] | None = None,
    ) -> list[dict[str, str]]:
        """Consulta múltiplas personas com a mesma pergunta.

        Implementa o padrão supervisor: despacha para cada persona selecionada
        e coleta as respostas.

        Args:
            cluster_ids: Lista de IDs das personas a consultar.
            pergunta: Pergunta do stakeholder.
            historicos: Dict de históricos por cluster_id (opcional).

        Returns:
            Lista de dicts com "nome" e "resposta" para cada persona.
        """
        respostas: list[dict[str, str]] = []

        for cid in cluster_ids:
            historico = historicos.get(cid) if historicos else None
            resultado: dict[str, str] = self.consultar_persona(
                cid, pergunta, historico
            )
            respostas.append(resultado)

        return respostas

    def consultar_todas(
        self, pergunta: str,
        historicos: dict[int, list[dict[str, str]]] | None = None,
    ) -> list[dict[str, str]]:
        """Consulta TODAS as personas simultaneamente.

        Args:
            pergunta: Pergunta do stakeholder.
            historicos: Dict de históricos por cluster_id (opcional).

        Returns:
            Lista de respostas de todas as personas.
        """
        return self.consultar_personas(
            list(self.personas.keys()), pergunta, historicos
        )
