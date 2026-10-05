"""
KonigHandoff — Transferência estruturada de contexto entre agentes.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

O Handoff é o DNA rastreável do KONIG. Cada vez que um agente passa a bola,
o handoff registra: quem passou, para quem, sob qual condição, e o contexto completo.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HandoffStatus(str, Enum):
    """Estado do handoff no ciclo de vida."""
    PENDING = "pending"          # Criado, aguardando consumo
    CONSUMED = "consumed"        # Agente destino recebeu e processou
    REJECTED = "rejected"       # Gate reprovou, handoff devolvido
    EXPIRED = "expired"          # Timeout expirado sem consumo


class KonigHandoff(BaseModel):
    """
    Registro de transferência de contexto entre agentes.
    
    Cada handoff carrega a assinatura KONIG do remetente e destinatário,
    o contexto acumulado, a condição de transição, e o status de consumo.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # --- Assinaturas KONIG ---
    from_agent: str = Field(description="Assinatura KONIG: '[Nome - Papel]'")
    to_agent: str = Field(description="Assinatura KONIG do próximo agente")
    
    # --- Contexto ---
    context: str = Field(description="Saída completa do agente anterior")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Artefatos produzidos (PRD, código, etc)")
    
    # --- Condição de Transição (inspirado KONIG: next_command, condition) ---
    condition: str = Field(
        default="task_completed",
        description="Condição que ativou este handoff (ex: 'prd_approved', 'code_review_passed')"
    )
    next_command: Optional[str] = Field(
        default=None,
        description="Comando sugerido para o próximo agente (ex: 'create_architecture', 'write_tests')"
    )
    
    # --- Rastreabilidade ---
    task_id: Optional[str] = Field(default=None, description="Task que originou o handoff")
    gate_results: List[str] = Field(default_factory=list, description="IDs dos gates que aprovaram este handoff")
    
    # --- Status ---
    status: HandoffStatus = Field(default=HandoffStatus.PENDING)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    consumed_at: Optional[datetime] = Field(default=None)

    def consume(self) -> None:
        """Marca o handoff como consumido pelo agente destino."""
        self.status = HandoffStatus.CONSUMED
        self.consumed_at = datetime.now(timezone.utc)

    def reject(self, reason: str = "") -> None:
        """Gate reprovou a saída. Handoff é devolvido ao remetente."""
        self.status = HandoffStatus.REJECTED
        self.artifacts["rejection_reason"] = reason

    @property
    def signature_line(self) -> str:
        """
        Gera a linha de assinatura visual para logs e outputs.
        Inspirado diretamente no padrão KONIG:
        'HANDOFF: [Alice - Lead PM] → [Bob - System Architect]'
        """
        return f"HANDOFF: {self.from_agent} → {self.to_agent} | Condição: {self.condition}"

    def __str__(self) -> str:
        return self.signature_line
