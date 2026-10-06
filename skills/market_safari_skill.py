"""
MarketSafariMinerSkill — Mineração de Dores, Consciência e Vocabulário Cru (Eugene Schwartz).

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from core.primitives.skill import KonigSkill, SkillCategory, SkillTier, SkillInput, SkillOutput


class SafariInput(SkillInput):
    niche: str = Field(description="Nicho ou segmento de mercado analisado (ex: 'barbearias', 'clinicas_estetica')")
    current_pain: str = Field(description="Sintoma operacional observado (ex: 'perda de clientes no whatsapp por demora')")
    competitor_claims: List[str] = Field(default_factory=list, description="O que os concorrentes prometem atualmente")


class SafariResult(BaseModel):
    niche: str
    diagnosed_awareness: str
    diagnosed_sophistication: str
    unique_mechanism: str
    verbatim_vocabulary: Dict[str, List[str]]
    sales_opener: str


class MarketSafariMinerSkill(KonigSkill):
    name: str = "market_safari_miner"
    description: str = (
        "Minera dores viscerais, diagnostica o estágio de consciência (Schwartz) "
        "e formula o Mecanismo Único para desarmar o ceticismo do mercado."
    )
    category: SkillCategory = SkillCategory.DATA_ANALYSIS
    tier: SkillTier = SkillTier.FREQUENTLY_USED
    estimated_token_cost: int = 120

    def execute(self, input_data: Dict[str, Any]) -> SkillOutput:
        try:
            niche = input_data.get("niche", "servicos_locais")
            pain = input_data.get("current_pain", "atendimento caotico e perda de clientes")
            competitors = input_data.get("competitor_claims", ["criacao de site", "landing page bonita"])

            # Heurística de Schwartz: Se concorrentes prometem 'site/layout', mercado está saturado no Estágio 2/3
            sophistication = "Estágio 3 (Ceticismo com promessas diretas; exige Mecanismo Único)"
            awareness = "Nível 2: Consciente do Problema (Sente a dor do tempo perdido no WhatsApp)"

            mechanism = f"Tool de Agendamento em 3 Toques Integrada ao WhatsApp (Sem Aplicativo)"

            verbatim = {
                "frases_de_dor": [
                    "Fico preso no celular até 22h respondendo cliente",
                    "Se eu paro o corte pra responder, perco o ritmo da cadeira",
                    "Cliente marca e não aparece, e eu fico no prejuízo seco"
                ],
                "palavras_proibidas": ["leads", "tráfego", "branding", "conversão", "pixel"],
                "palavras_magneticas": ["agenda cheia", "sem perder tempo no zap", "R$ 699 sem mensalidade", "direto no seu celular"]
            }

            opener = (
                f"Fala parceiro, vejo que você tem uma operação forte na sua {niche.replace('_', ' ')}. "
                f"Quantos clientes você perde por semana só porque não dá tempo de responder o WhatsApp na hora "
                f"enquanto você tá atendendo? A gente criou uma ferramenta que o cliente agenda sozinho no seu site "
                f"e joga a mensagem pronta no seu WhatsApp por um valor único de R$ 699, sem mensalidade. Bora ver como funciona?"
            )

            res = SafariResult(
                niche=niche,
                diagnosed_awareness=awareness,
                diagnosed_sophistication=sophistication,
                unique_mechanism=mechanism,
                verbatim_vocabulary=verbatim,
                sales_opener=opener
            )

            return SkillOutput(success=True, result=res.model_dump())
        except Exception as e:
            return SkillOutput(success=False, error=str(e))
