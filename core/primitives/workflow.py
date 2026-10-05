"""
KonigWorkflow — DAG de execução com condições de transição entre tasks.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

Um Workflow no KONIG:
1. Define uma coleção de Tasks com suas dependências (DAG)
2. Resolve a ordem de execução via topological sort
3. Aplica gates entre cada transição
4. Suporta execução sequencial e paralela (tasks independentes rodam juntas)
5. Registra todo o histórico de handoffs para auditoria
"""

from __future__ import annotations

import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from core.primitives.handoff import KonigHandoff
from core.primitives.task import KonigTask, TaskStatus


class WorkflowStatus(str, Enum):
    """Status global do workflow."""
    DRAFT = "draft"                # Definido mas não iniciado
    RUNNING = "running"            # Em execução
    PAUSED = "paused"              # Pausado (human-in-the-loop)
    COMPLETED = "completed"        # Todas as tasks concluídas
    FAILED = "failed"              # Task crítica falhou
    CANCELLED = "cancelled"


class KonigWorkflow(BaseModel):
    """
    DAG de execução que orquestra Tasks, aplica Gates e registra Handoffs.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(description="Nome do workflow (ex: 'greenfield_fullstack')")
    description: str = Field(default="")
    
    # --- Tasks (o grafo) ---
    tasks: Dict[str, KonigTask] = Field(default_factory=dict, description="Mapa de task_id → KonigTask")
    
    # --- Histórico ---
    handoff_history: List[KonigHandoff] = Field(default_factory=list, description="Log completo de handoffs")
    
    # --- Status ---
    status: WorkflowStatus = Field(default=WorkflowStatus.DRAFT)
    
    # --- Timestamps ---
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    # --- Métricas ---
    total_tokens_used: int = Field(default=0)
    total_cost_usd: float = Field(default=0.0)

    def add_task(self, task: KonigTask) -> None:
        """Adiciona uma task ao workflow."""
        self.tasks[task.id] = task

    def get_ready_tasks(self) -> List[KonigTask]:
        """
        Retorna todas as tasks cujas dependências foram satisfeitas.
        Isso permite execução paralela de tasks independentes.
        """
        completed_ids = {
            tid for tid, t in self.tasks.items()
            if t.status == TaskStatus.COMPLETED
        }
        return [
            task for task in self.tasks.values()
            if task.status in (TaskStatus.BACKLOG, TaskStatus.READY)
            and task.is_ready(completed_ids)
        ]

    def resolve_execution_order(self) -> List[List[str]]:
        """
        Resolve a ordem de execução via topological sort (Kahn's algorithm).
        Retorna listas de task_ids agrupadas por "wave" (tasks na mesma wave podem rodar em paralelo).
        
        Exemplo: [[task_a], [task_b, task_c], [task_d]]
        → task_a roda primeiro, depois b e c em paralelo, depois d.
        """
        in_degree: Dict[str, int] = defaultdict(int)
        adjacency: Dict[str, List[str]] = defaultdict(list)
        
        for tid, task in self.tasks.items():
            if tid not in in_degree:
                in_degree[tid] = 0
            for dep in task.depends_on:
                adjacency[dep].append(tid)
                in_degree[tid] += 1
        
        # Kahn's algorithm com agrupamento por waves
        queue = deque([tid for tid, deg in in_degree.items() if deg == 0])
        waves: List[List[str]] = []
        
        while queue:
            current_wave = list(queue)
            waves.append(current_wave)
            queue.clear()
            
            for tid in current_wave:
                for neighbor in adjacency[tid]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        # Validação: detecta ciclos
        total_resolved = sum(len(w) for w in waves)
        if total_resolved != len(self.tasks):
            raise ValueError(
                f"Ciclo detectado no workflow! {len(self.tasks)} tasks, "
                f"mas apenas {total_resolved} foram resolvidas."
            )
        
        return waves

    def record_handoff(self, handoff: KonigHandoff) -> None:
        """Registra um handoff no histórico para auditoria."""
        self.handoff_history.append(handoff)

    def start(self) -> None:
        """Inicia o workflow."""
        self.status = WorkflowStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)

    def check_completion(self) -> bool:
        """Verifica se todas as tasks foram concluídas."""
        all_done = all(
            t.status == TaskStatus.COMPLETED
            for t in self.tasks.values()
        )
        if all_done:
            self.status = WorkflowStatus.COMPLETED
            self.completed_at = datetime.now(timezone.utc)
        return all_done

    def get_summary(self) -> Dict[str, Any]:
        """Retorna um resumo do estado do workflow."""
        status_counts = defaultdict(int)
        for task in self.tasks.values():
            status_counts[task.status.value] += 1
        
        return {
            "workflow": self.name,
            "status": self.status.value,
            "tasks": dict(status_counts),
            "total_tasks": len(self.tasks),
            "handoffs": len(self.handoff_history),
            "tokens_used": self.total_tokens_used,
            "cost_usd": self.total_cost_usd,
        }

    def __str__(self) -> str:
        return f"[Workflow: {self.name} | Status: {self.status.value} | Tasks: {len(self.tasks)}]"
