"""
KonigGate — Validador de qualidade que aprova/reprova saídas antes do handoff.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

Um Gate no KONIG é um checkpoint obrigatório que:
1. Recebe a saída de um agente
2. Executa validações (pode ser regra estática OU chamada LLM)
3. Retorna APPROVED ou REJECTED com justificativa
4. Se rejeitado, o handoff é devolvido ao agente anterior para correção
5. Tem um número máximo de retries (inspirado KONIG max_retries)
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GateVerdict(str, Enum):
    """Resultado da validação do gate."""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"   # Precisa de revisão humana (human-in-the-loop)


class GateResult(BaseModel):
    """Resultado estruturado de uma execução de gate."""
    gate_id: str = Field(description="ID do gate que executou a validação")
    gate_name: str = Field(description="Nome do gate")
    verdict: GateVerdict = Field(description="Aprovado, Reprovado ou Precisa Revisão")
    score: float = Field(default=1.0, ge=0.0, le=1.0, description="Score de qualidade (0.0 a 1.0)")
    feedback: str = Field(default="", description="Justificativa da decisão")
    issues: List[str] = Field(default_factory=list, description="Lista de problemas encontrados")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.verdict == GateVerdict.APPROVED


class KonigGate(ABC, BaseModel):
    """
    Classe base abstrata para todos os gates de qualidade do KONIG.
    
    Toda gate deve:
    1. Definir name, description e min_score (threshold de aprovação)
    2. Implementar validate() que recebe o output do agente e retorna GateResult
    3. Opcionalmente definir max_retries para loop de correção
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(description="Nome do gate (ex: 'code_quality_gate')")
    description: str = Field(description="O que este gate valida")
    min_score: float = Field(default=0.7, ge=0.0, le=1.0, description="Score mínimo para aprovação")
    max_retries: int = Field(default=3, description="Tentativas máximas de correção (inspirado KONIG max_retries)")
    
    # Checklist de itens que devem estar presentes (inspirado KONIG checklists)
    checklist: List[str] = Field(default_factory=list, description="Itens que DEVEM estar presentes na saída")

    @abstractmethod
    def validate(self, agent_output: str, context: Dict[str, Any] = None) -> GateResult:
        """
        Executa a validação sobre a saída do agente.
        
        Subclasses DEVEM implementar este método.
        Pode ser uma validação estática (regex, checklist) ou dinâmica (chamada LLM).
        """
        ...

    def run_checklist(self, agent_output: str) -> List[str]:
        """
        Verifica se todos os itens do checklist estão presentes na saída.
        Retorna lista de itens faltantes.
        """
        missing = []
        output_lower = agent_output.lower()
        for item in self.checklist:
            if item.lower() not in output_lower:
                missing.append(item)
        return missing

    def __str__(self) -> str:
        return f"[Gate: {self.name} | Min Score: {self.min_score} | Max Retries: {self.max_retries}]"
