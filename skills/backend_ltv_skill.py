"""
BackendLTVArchitectSkill — Arquitetura de LTV, Esteira de Ascensão e Ativos Ocultos (Jay Abraham).

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from core.primitives.skill import KonigSkill, SkillCategory, SkillTier, SkillInput, SkillOutput


class LTVInput(SkillInput):
    frontend_product: str = Field(description="Produto de entrada (ex: 'LP + Tool de Agendamento')")
    frontend_price: float = Field(default=699.0, description="Preço do front-end")
    clients_count: int = Field(default=20, description="Volume de clientes ativos")
    no_show_rate: float = Field(default=0.25, description="Taxa média de falta de clientes (no-show)")


class LTVResult(BaseModel):
    frontend_revenue: float
    immediate_upsell_name: str
    projected_mrr_upsell: float
    reactivation_deal_value: float
    total_projected_year_1: float
    ascension_pitch: str


class BackendLTVArchitectSkill(KonigSkill):
    name: str = "backend_ltv_architect"
    description: str = (
        "Calcula o valor vitalício (LTV), empacota o Próximo Problema Lógico "
        "e arquiteta ofertas de upsell e reativação de ativos ocultos (Jay Abraham)."
    )
    category: SkillCategory = SkillCategory.DATA_ANALYSIS
    tier: SkillTier = SkillTier.FREQUENTLY_USED
    estimated_token_cost: int = 150

    def execute(self, input_data: Dict[str, Any]) -> SkillOutput:
        try:
            fe_price = float(input_data.get("frontend_price", 699.0))
            clients = int(input_data.get("clients_count", 20))
            no_show = float(input_data.get("no_show_rate", 0.25))

            # Matemática de Abraham:
            fe_revenue = clients * fe_price
            
            # Upsell 1: Automação Anti-Falta (No-Show Killer) a R$ 197/mês (35% conversão da base)
            upsell_conversion = 0.35
            upsell_clients = int(clients * upsell_conversion)
            upsell_mrr = upsell_clients * 197.0

            # Deal de Contingência / Reativação de 300 contatos inativos (30% dos 10% reativados)
            reactivation_value_per_client = 300 * 0.10 * 70.0 * 0.30 # 30 clientes * R$ 70 ticket * 30% comissão = R$ 630 por cliente
            total_reactivation = clients * 0.40 * reactivation_value_per_client

            year_1 = fe_revenue + (upsell_mrr * 12) + total_reactivation

            pitch = (
                f"Amigo, analisamos seus dados: em média, {int(no_show*100)}% dos agendamentos viram falta ou no-show. "
                f"Isso custa mais de R$ 600 por mês de cadeira vazia. Desenvolvemos o módulo No-Show Killer com IA: "
                f"ele dispara lembrete 2h antes com confirmação no WhatsApp. Custa só R$ 197/mês e se paga no primeiro cliente "
                f"que deixar de faltar. Quer ativar agora?"
            )

            res = LTVResult(
                frontend_revenue=fe_revenue,
                immediate_upsell_name="No-Show Killer (Automação Anti-Falta)",
                projected_mrr_upsell=upsell_mrr,
                reactivation_deal_value=total_reactivation,
                total_projected_year_1=year_1,
                ascension_pitch=pitch
            )

            return SkillOutput(success=True, result=res.model_dump())
        except Exception as e:
            return SkillOutput(success=False, error=str(e))
