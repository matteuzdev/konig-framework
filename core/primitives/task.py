"""
KonigTask — Unidade atômica de trabalho com status, dependências e output tipado.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

Uma Task no KONIG:
1. Tem um agente assignado (ou é delegável)
2. Pode depender de outras tasks (DAG)
3. Tem status com lifecycle completo
4. Produz um output tipado que alimenta o próximo
5. Pode ter gates obrigatórios antes de ser dada como concluída
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Lifecycle completo de uma task."""
    BACKLOG = "backlog"              # Criada, não iniciada
    READY = "ready"                  # Dependências satisfeitas, pronta para execução
    IN_PROGRESS = "in_progress"      # Agente executando
    GATE_REVIEW = "gate_review"      # Saída aguardando validação do gate
    REWORK = "rework"                # Gate reprovou, agente deve refazer
    COMPLETED = "completed"          # Gate aprovou, saída aceita
    FAILED = "failed"                # Falha irrecuperável
    BLOCKED = "blocked"              # Dependência bloqueada


class TaskPriority(str, Enum):
    """Prioridade para ordenação no workflow."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskOutput(BaseModel):
    """
    Saída estruturada de uma task.
    Inspirado no KONIG ActionOutput e KONIG task artifacts.
    """
    content: str = Field(description="Conteúdo principal da saída")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Artefatos gerados (ex: {'prd': '...', 'code': '...'})")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Métricas da execução (tokens usados, tempo, etc)")


class KonigTask(BaseModel):
    """
    Unidade atômica de trabalho no framework KONIG.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # --- Definição ---
    name: str = Field(description="Nome da task (ex: 'create_prd')")
    description: str = Field(description="Instrução detalhada do que o agente deve fazer")
    expected_output: str = Field(description="Descrição do output esperado (ex: 'PRD completo em markdown')")
    
    # --- Atribuição ---
    assigned_agent: Optional[str] = Field(default=None, description="Assinatura KONIG do agente responsável")
    
    # --- Dependências (DAG) ---
    depends_on: List[str] = Field(default_factory=list, description="IDs de tasks que devem ser concluídas antes")
    
    # --- Gates obrigatórios ---
    required_gates: List[str] = Field(default_factory=list, description="Nomes dos gates que devem aprovar a saída")
    
    # --- Skills necessárias ---
    required_skills: List[str] = Field(default_factory=list, description="Skills que o agente precisa ter para executar")
    
    # --- Lifecycle ---
    status: TaskStatus = Field(default=TaskStatus.BACKLOG)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    retry_count: int = Field(default=0, description="Quantas vezes o gate reprovou e mandou refazer")
    max_retries: int = Field(default=3)
    
    # --- Output ---
    output: Optional[TaskOutput] = Field(default=None)
    
    # --- Timestamps ---
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    def start(self) -> None:
        """Marca a task como em progresso."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc)

    def submit_for_review(self, output: TaskOutput) -> None:
        """Submete a saída para revisão do gate."""
        self.output = output
        self.status = TaskStatus.GATE_REVIEW

    def approve(self) -> None:
        """Gate aprovou a saída."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

    def reject(self) -> None:
        """Gate reprovou. Incrementa retry e manda para rework."""
        self.retry_count += 1
        if self.retry_count >= self.max_retries:
            self.status = TaskStatus.FAILED
        else:
            self.status = TaskStatus.REWORK

    def is_ready(self, completed_task_ids: set) -> bool:
        """Verifica se todas as dependências foram satisfeitas."""
        if not self.depends_on:
            return True
        return all(dep_id in completed_task_ids for dep_id in self.depends_on)

    def __str__(self) -> str:
        agent = self.assigned_agent or "Não atribuída"
        return f"[Task: {self.name} | Status: {self.status.value} | Agent: {agent}]"
