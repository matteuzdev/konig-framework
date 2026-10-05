"""
KonigSkill — Módulo plugável (tool/ferramenta) com input/output tipados.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

Uma Skill no KONIG é um módulo atômico que:
1. Tem input/output tipados (Pydantic)
2. Pode ser registrada no skill registry global
3. Pode ser atribuída a agentes específicos
4. Tem custo estimado (tokens) para budget tracking
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field


class SkillTier(int, Enum):
    """
    Tiers de skill inspirados no KONIG tool registry.
    Tier 1 = sempre carregada, Tier 3 = sob demanda.
    """
    ALWAYS_LOADED = 1
    FREQUENTLY_USED = 2
    DEFERRED = 3


class SkillCategory(str, Enum):
    """Categorias para organização e filtragem de skills."""
    FILE_SYSTEM = "file_system"
    CODE_EXECUTION = "code_execution"
    WEB_RESEARCH = "web_research"
    DATA_ANALYSIS = "data_analysis"
    COMMUNICATION = "communication"
    DESIGN = "design"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    CUSTOM = "custom"


class SkillInput(BaseModel):
    """Schema base para input de uma skill. Subclasses tipam os campos."""
    pass


class SkillOutput(BaseModel):
    """Schema base para output de uma skill."""
    success: bool = Field(default=True)
    result: Any = Field(default=None)
    error: Optional[str] = Field(default=None)


class KonigSkill(ABC, BaseModel):
    """
    Classe base abstrata para todas as skills/tools do KONIG.
    
    Toda skill deve:
    1. Definir name, description, category e tier
    2. Implementar execute() que recebe SkillInput e retorna SkillOutput
    3. Opcionalmente definir estimated_token_cost para budget tracking
    """
    name: str = Field(description="Nome único da skill (ex: 'web_search')")
    description: str = Field(description="O que esta skill faz")
    category: SkillCategory = Field(default=SkillCategory.CUSTOM)
    tier: SkillTier = Field(default=SkillTier.DEFERRED)
    estimated_token_cost: int = Field(default=0, description="Custo estimado em tokens (inspirado KONIG token cost)")
    
    # Schema de input/output (para validação estrita)
    input_schema: Optional[Type[SkillInput]] = Field(default=None, exclude=True)
    output_schema: Optional[Type[SkillOutput]] = Field(default=None, exclude=True)

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> SkillOutput:
        """
        Executa a skill com os dados de entrada fornecidos.
        
        Subclasses DEVEM implementar este método.
        """
        ...

    def validate_input(self, input_data: Dict[str, Any]) -> SkillInput:
        """Valida o input contra o schema definido."""
        if self.input_schema:
            return self.input_schema(**input_data)
        return SkillInput(**input_data)

    def to_tool_description(self) -> str:
        """
        Gera a descrição da skill para injeção no prompt do LLM.
        Formato compatível com function calling.
        """
        return f"Tool: {self.name}\nDescrição: {self.description}\nCategoria: {self.category.value}"

    def __str__(self) -> str:
        return f"[Skill: {self.name} | Tier {self.tier.value} | {self.category.value}]"
