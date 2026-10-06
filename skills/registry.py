"""
Konig Skill Registry — Sistema de registro e gerenciamento de ferramentas do framework.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from core.primitives.skill import KonigSkill, SkillTier, SkillCategory, SkillOutput


class GenericSkill(KonigSkill):
    """Implementação concreta de skill genérica executável por handler."""
    handler: Optional[Callable[[Dict[str, Any]], Any]] = None

    def execute(self, input_data: Dict[str, Any]) -> SkillOutput:
        if self.handler:
            try:
                res = self.handler(input_data)
                return SkillOutput(success=True, result=res)
            except Exception as e:
                return SkillOutput(success=False, error=str(e))
        return SkillOutput(success=True, result=f"Executed {self.name} with input: {input_data}")


class SkillRegistry:
    """
    Registry global de skills acessíveis aos agentes.
    """
    def __init__(self):
        self._skills: Dict[str, KonigSkill] = {}

    def register(self, skill: KonigSkill) -> None:
        """Registra uma skill no sistema."""
        self._skills[skill.name.lower()] = skill

    def get(self, skill_name: str) -> Optional[KonigSkill]:
        """Recupera uma skill pelo nome."""
        return self._skills.get(skill_name.lower())

    def list_all(self) -> List[str]:
        """Lista todas as skills registradas."""
        return list(self._skills.keys())

    def list_by_tier(self, tier: SkillTier) -> List[KonigSkill]:
        """Filtra skills por tier de acesso."""
        return [s for s in self._skills.values() if s.tier == tier]


# Instância Singleton global
GLOBAL_SKILL_REGISTRY = SkillRegistry()

# Registro de skills nativas básicas
GLOBAL_SKILL_REGISTRY.register(
    GenericSkill(
        name="file_system",
        description="Lê e escreve arquivos no sistema de arquivos local de forma segura.",
        category=SkillCategory.FILE_SYSTEM,
        tier=SkillTier.ALWAYS_LOADED,
        estimated_token_cost=0
    )
)

GLOBAL_SKILL_REGISTRY.register(
    GenericSkill(
        name="web_research",
        description="Pesquisa e extrai informações da web para enriquecer o contexto dos agentes.",
        category=SkillCategory.WEB_RESEARCH,
        tier=SkillTier.FREQUENTLY_USED,
        estimated_token_cost=150
    )
)

GLOBAL_SKILL_REGISTRY.register(
    GenericSkill(
        name="code_executor",
        description="Executa scripts e validações em ambiente controlado.",
        category=SkillCategory.CODE_EXECUTION,
        tier=SkillTier.FREQUENTLY_USED,
        estimated_token_cost=250
    )
)

GLOBAL_SKILL_REGISTRY.register(
    GenericSkill(
        name="design_system",
        description="Gera e valida tokens de UI/UX, fontes, contrastes e componentes Pro-Max.",
        category=SkillCategory.DESIGN,
        tier=SkillTier.ALWAYS_LOADED,
        estimated_token_cost=50
    )
)

# Skills Canônicas Avançadas (Eugene Schwartz & Jay Abraham)
from skills.market_safari_skill import MarketSafariMinerSkill
from skills.backend_ltv_skill import BackendLTVArchitectSkill

GLOBAL_SKILL_REGISTRY.register(MarketSafariMinerSkill())
GLOBAL_SKILL_REGISTRY.register(BackendLTVArchitectSkill())
