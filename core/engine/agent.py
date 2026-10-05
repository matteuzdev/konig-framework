"""
KonigAgent — O agente refundado com todas as primitivas integradas.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

Um KonigAgent:
1. Tem identidade (nome + papel + assinatura KONIG)
2. Tem skills (ferramentas registradas)
3. Tem SOPs (procedimentos padrão que guiam seu comportamento)
4. Pode observar mensagens de outros agentes (_watch)
5. Pode executar tasks e submeter para gates
6. Mantém memória de sessão
7. Rastreia custos (budget)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from core.primitives.gate import GateResult
from core.primitives.handoff import KonigHandoff
from core.primitives.message import KonigMessage, MessageType
from core.primitives.skill import KonigSkill
from core.primitives.task import KonigTask, TaskOutput


class KonigAgent(BaseModel):
    """
    O agente central do framework KONIG.
    Combina o melhor de cada referência em uma abstração unificada.
    """
    # --- Identidade (inspirado KONIG assinatura + KONIG PREFIX_TEMPLATE) ---
    name: str = Field(description="Nome do agente (ex: 'Alice')")
    role: str = Field(description="Papel do agente (ex: 'Lead Product Manager')")
    goal: str = Field(description="Objetivo principal e KPIs")
    backstory: str = Field(default="", description="SOP/instruções detalhadas (inspirado KONIG/KONIG)")
    constraints: str = Field(default="", description="Restrições e regras de conduta (inspirado KONIG)")
    
    # --- Skills/Tools disponíveis ---
    skills: List[str] = Field(default_factory=list, description="Nomes das skills registradas que este agente pode usar")
    
    # --- Observação (inspirado KONIG message bus watch) ---
    watches: Set[str] = Field(default_factory=set, description="Tipos de mensagem/ações que este agente observa")
    
    # --- Memória (inspirado KONIG session state) ---
    memory: List[Dict[str, Any]] = Field(default_factory=list, description="Histórico de interações")
    session_state: Dict[str, Any] = Field(default_factory=dict, description="Estado persistente da sessão")
    
    # --- LLM Config ---
    model: str = Field(default="gpt-4o", description="Modelo padrão (roteado via LiteLLM)")
    fallback_models: List[str] = Field(default_factory=list, description="Modelos de fallback (inspirado KONIG)")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    
    # --- Budget (inspirado KONIG CostManager) ---
    max_budget_usd: float = Field(default=10.0, description="Budget máximo em USD")
    spent_usd: float = Field(default=0.0)
    tokens_used: int = Field(default=0)

    @property
    def signature(self) -> str:
        """
        Assinatura visual KONIG para handoffs e logs.
        Ex: '[Alice - Lead Product Manager]'
        """
        return f"[{self.name} - {self.role}]"

    @property
    def system_prompt(self) -> str:
        """
        Monta o system prompt completo do agente.
        Inspirado no KONIG PREFIX_TEMPLATE + CONSTRAINT_TEMPLATE.
        """
        parts = [
            f"Você é {self.name}, um(a) {self.role}.",
            f"Seu objetivo principal: {self.goal}",
        ]
        
        if self.backstory:
            parts.append(f"\n## Procedimentos Operacionais Padrão (SOPs)\n{self.backstory}")
        
        if self.constraints:
            parts.append(f"\n## Restrições\n{self.constraints}")
        
        if self.skills:
            parts.append(f"\n## Ferramentas Disponíveis\n{', '.join(self.skills)}")
        
        parts.append(
            f"\n## Regra de Assinatura\n"
            f"Ao finalizar QUALQUER entrega, você DEVE assinar com:\n"
            f"'HANDOFF_SIGNATURE: {self.signature}'"
        )
        
        return "\n".join(parts)

    def add_to_memory(self, role: str, content: str) -> None:
        """Adiciona uma interação à memória do agente."""
        self.memory.append({"role": role, "content": content})

    def check_budget(self) -> bool:
        """Verifica se o agente ainda tem budget disponível."""
        return self.spent_usd < self.max_budget_usd

    def record_cost(self, tokens: int, cost_usd: float) -> None:
        """Registra gasto de tokens e dólares."""
        self.tokens_used += tokens
        self.spent_usd += cost_usd

    def can_execute(self, task: KonigTask) -> bool:
        """Verifica se o agente tem as skills necessárias para a task."""
        if not task.required_skills:
            return True
        return all(skill in self.skills for skill in task.required_skills)

    def create_handoff(self, to_agent: str, context: str, task: KonigTask = None, 
                       condition: str = "task_completed") -> KonigHandoff:
        """
        Cria um handoff estruturado para o próximo agente.
        """
        return KonigHandoff(
            from_agent=self.signature,
            to_agent=to_agent,
            context=context,
            condition=condition,
            task_id=task.id if task else None,
            artifacts=task.output.artifacts if task and task.output else {},
        )

    def __str__(self) -> str:
        return f"{self.signature} | Skills: {len(self.skills)} | Budget: ${self.max_budget_usd - self.spent_usd:.2f} remaining"
