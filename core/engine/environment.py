"""
KonigEnvironment — Message bus (pub/sub) para comunicação entre agentes.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

O Environment é o "escritório virtual" onde os agentes trabalham.
Ele gerencia:
1. O registro de agentes ativos
2. O barramento de mensagens (pub/sub)
3. O histórico global de comunicação
4. O estado compartilhado da sessão
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from core.engine.agent import KonigAgent
from core.primitives.message import KonigMessage, MessageType


class KonigEnvironment(BaseModel):
    """
    Ambiente de execução que conecta agentes via message bus.
    """
    # --- Agentes registrados ---
    agents: Dict[str, KonigAgent] = Field(default_factory=dict, description="Mapa de assinatura → agente")
    
    # --- Message Bus ---
    message_queue: List[KonigMessage] = Field(default_factory=list, description="Fila de mensagens pendentes")
    message_history: List[KonigMessage] = Field(default_factory=list, description="Histórico completo")
    
    # --- Subscriptions (inspirado KONIG message bus watch) ---
    subscriptions: Dict[str, Set[str]] = Field(
        default_factory=lambda: defaultdict(set),
        description="Mapa de message_type → set de assinaturas de agentes inscritos"
    )
    
    # --- Estado global ---
    shared_state: Dict[str, Any] = Field(default_factory=dict, description="Estado compartilhado entre agentes")

    def register_agent(self, agent: KonigAgent) -> None:
        """Registra um agente no ambiente e configura suas subscriptions."""
        self.agents[agent.signature] = agent
        
        # Registra watches do agente
        for watch_type in agent.watches:
            self.subscriptions[watch_type].add(agent.signature)

    def remove_agent(self, signature: str) -> None:
        """Remove um agente do ambiente."""
        if signature in self.agents:
            del self.agents[signature]
            # Limpa subscriptions
            for subs in self.subscriptions.values():
                subs.discard(signature)

    def publish_message(self, message: KonigMessage) -> None:
        """
        Publica uma mensagem no barramento.
        Mensagens direcionadas vão para o agente específico.
        Broadcasts vão para todos os inscritos no tipo.
        """
        self.message_history.append(message)
        
        if message.to_agent:
            # Mensagem direcionada
            self.message_queue.append(message)
        else:
            # Broadcast: cria cópia para cada inscrito
            subscribers = self.subscriptions.get(message.message_type.value, set())
            for sub_signature in subscribers:
                if sub_signature != message.from_agent:  # Não envia para si mesmo
                    directed = message.model_copy(update={"to_agent": sub_signature})
                    self.message_queue.append(directed)

    def get_messages_for(self, agent_signature: str) -> List[KonigMessage]:
        """
        Retira da fila todas as mensagens destinadas a um agente específico.
        Marca como consumidas.
        """
        agent_messages = []
        remaining = []
        
        for msg in self.message_queue:
            if msg.to_agent == agent_signature:
                msg.mark_consumed()
                agent_messages.append(msg)
            else:
                remaining.append(msg)
        
        self.message_queue = remaining
        return agent_messages

    @property
    def is_idle(self) -> bool:
        """
        Verifica se não há mais mensagens pendentes (inspirado KONIG env.is_idle).
        """
        return len(self.message_queue) == 0

    def get_agent(self, signature: str) -> Optional[KonigAgent]:
        """Busca um agente pela assinatura."""
        return self.agents.get(signature)

    def get_agent_by_name(self, name: str) -> Optional[KonigAgent]:
        """Busca um agente pelo nome."""
        for agent in self.agents.values():
            if agent.name == name:
                return agent
        return None

    def get_context_for_agent(self, agent_signature: str, max_messages: int = 20) -> str:
        """
        Monta o contexto relevante para um agente baseado no histórico de mensagens.
        Inspirado no KONIG SYNAPSE context tracking.
        """
        relevant = [
            msg for msg in self.message_history[-max_messages:]
            if msg.to_agent == agent_signature or msg.to_agent is None
        ]
        
        context_parts = []
        for msg in relevant:
            context_parts.append(f"--- {msg.from_agent} ({msg.message_type.value}) ---\n{msg.content}\n")
        
        return "\n".join(context_parts)

    def __str__(self) -> str:
        return (
            f"[Environment | Agents: {len(self.agents)} | "
            f"Pending Messages: {len(self.message_queue)} | "
            f"History: {len(self.message_history)}]"
        )
