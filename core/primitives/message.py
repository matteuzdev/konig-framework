"""
KonigMessage — Schema de comunicação entre agentes.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

Cada mensagem carrega:
- De quem veio (assinatura KONIG)
- Para quem vai
- O conteúdo (texto, JSON, artefato)
- Metadados de rastreabilidade (task_id, timestamp, status)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Tipos de mensagem suportados no barramento."""
    TASK_OUTPUT = "task_output"        # Resultado de uma task
    HANDOFF = "handoff"                # Transferência entre agentes
    GATE_RESULT = "gate_result"        # Resultado de um gate (aprovado/reprovado)
    SYSTEM = "system"                  # Mensagem de sistema (logs, erros)
    USER_INPUT = "user_input"          # Input do usuário externo
    BROADCAST = "broadcast"            # Mensagem para todos os agentes


class MessagePriority(str, Enum):
    """Prioridade da mensagem no barramento."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class KonigMessage(BaseModel):
    """
    Unidade atômica de comunicação entre agentes no framework KONIG.
    
    Inspiração direta:
    - KONIG: Message com cause_by para rastrear qual Action gerou a mensagem
    - KONIG: Handoff com from_agent, next_agent, consumed flag
    - KONIG: RunContext com session tracking
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único da mensagem")
    
    # --- Roteamento ---
    from_agent: str = Field(description="Assinatura KONIG do agente remetente (ex: '[Alice - Lead PM]')")
    to_agent: Optional[str] = Field(default=None, description="Assinatura do destinatário. None = broadcast")
    
    # --- Conteúdo ---
    content: str = Field(description="Corpo da mensagem (texto, markdown, JSON)")
    message_type: MessageType = Field(default=MessageType.TASK_OUTPUT)
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    
    # --- Rastreabilidade ---
    task_id: Optional[str] = Field(default=None, description="ID da task que originou esta mensagem")
    caused_by: Optional[str] = Field(default=None, description="Qual ação/skill gerou esta mensagem (inspirado KONIG caused_by)")
    
    # --- Metadados ---
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Dados extras (artefatos, métricas, etc)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    consumed: bool = Field(default=False, description="Flag de consumo (inspirado KONIG handoff.consumed)")

    def mark_consumed(self) -> None:
        """Marca a mensagem como consumida pelo destinatário."""
        self.consumed = True

    def __str__(self) -> str:
        return f"[MSG {self.message_type.value}] {self.from_agent} → {self.to_agent or 'ALL'}: {self.content[:80]}..."
