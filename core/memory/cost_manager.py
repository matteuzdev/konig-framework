"""
Konig CostManager — Governança financeira e rastreamento de custos de LLM em tempo real.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ModelPricing(BaseModel):
    input_cost_per_1m: float
    output_cost_per_1m: float


# Tabela oficial de preços de referência da indústria (USD por 1M tokens)
PRICING_TABLE: Dict[str, ModelPricing] = {
    # OpenAI
    "gpt-4o": ModelPricing(input_cost_per_1m=2.50, output_cost_per_1m=10.00),
    "gpt-4o-mini": ModelPricing(input_cost_per_1m=0.15, output_cost_per_1m=0.60),
    # Anthropic
    "claude-3-7-sonnet": ModelPricing(input_cost_per_1m=3.00, output_cost_per_1m=15.00),
    "claude-3-5-haiku": ModelPricing(input_cost_per_1m=0.80, output_cost_per_1m=4.00),
    # Google Gemini
    "gemini-2.5-pro": ModelPricing(input_cost_per_1m=1.25, output_cost_per_1m=5.00),
    "gemini-2.5-flash": ModelPricing(input_cost_per_1m=0.075, output_cost_per_1m=0.30),
    # DeepSeek
    "deepseek-chat": ModelPricing(input_cost_per_1m=0.14, output_cost_per_1m=0.28),
    "deepseek-reasoner": ModelPricing(input_cost_per_1m=0.55, output_cost_per_1m=2.19),
}

DEFAULT_PRICING = ModelPricing(input_cost_per_1m=1.00, output_cost_per_1m=3.00)


class CostRecord(BaseModel):
    agent_signature: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float


class KonigCostManager:
    """
    Rastreia e audita cada centavo gasto pelas LLMs durante a execução de squads e workflows.
    """
    def __init__(self, max_workflow_budget_usd: float = 25.0):
        self.max_workflow_budget_usd = max_workflow_budget_usd
        self.records: List[CostRecord] = []
        self.total_spent_usd: float = 0.0
        self.total_tokens_used: int = 0

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calcula o valor em dólares de uma chamada LLM."""
        pricing = PRICING_TABLE.get(model.lower(), DEFAULT_PRICING)
        cost_in = (prompt_tokens / 1_000_000) * pricing.input_cost_per_1m
        cost_out = (completion_tokens / 1_000_000) * pricing.output_cost_per_1m
        return round(cost_in + cost_out, 6)

    def record_usage(
        self, agent_signature: str, model: str, prompt_tokens: int, completion_tokens: int
    ) -> CostRecord:
        """Registra uma transação de tokens e atualiza os totais."""
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        total_tokens = prompt_tokens + completion_tokens

        record = CostRecord(
            agent_signature=agent_signature,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost
        )
        self.records.append(record)
        self.total_spent_usd += cost
        self.total_tokens_used += total_tokens

        return record

    def get_remaining_budget(self) -> float:
        """Retorna o saldo restante do orçamento em dólares."""
        return max(0.0, round(self.max_workflow_budget_usd - self.total_spent_usd, 4))

    def is_budget_exceeded(self) -> bool:
        """Verifica se o limite orçamentário foi atingido."""
        return self.total_spent_usd >= self.max_workflow_budget_usd

    def get_summary_by_agent(self) -> Dict[str, Dict[str, Any]]:
        """Gera resumo de custos agrupado por agente."""
        summary: Dict[str, Dict[str, Any]] = {}
        for r in self.records:
            if r.agent_signature not in summary:
                summary[r.agent_signature] = {"tokens": 0, "cost_usd": 0.0, "calls": 0}
            summary[r.agent_signature]["tokens"] += r.total_tokens
            summary[r.agent_signature]["cost_usd"] = round(summary[r.agent_signature]["cost_usd"] + r.cost_usd, 6)
            summary[r.agent_signature]["calls"] += 1
        return summary
