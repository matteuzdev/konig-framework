"""
Konig Builtin Gates — Validadores de qualidade rígidos para o pipeline.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from pydantic import Field

from core.primitives.gate import KonigGate, GateResult, GateVerdict


class PRDGate(KonigGate):
    name: str = "prd_gate"
    description: str = "Valida a completude e clareza do Documento de Requisitos de Produto (PRD)"
    min_score: float = 0.75
    checklist: List[str] = [
        "objetivo",
        "marca",
        "requisitos funcionais",
        "requisitos não funcionais",
        "critérios de aceite",
        "escopo",
    ]

    def validate(self, agent_output: str, context: Dict[str, Any] = None) -> GateResult:
        missing = self.run_checklist(agent_output)
        score = 1.0 - (len(missing) / max(len(self.checklist), 1))
        
        issues = [f"Item obrigatório ausente: {item}" for item in missing]
        
        # Validação adicional de profundidade
        if len(agent_output.split()) < 120:
            score -= 0.2
            issues.append("PRD muito superficial (menos de 120 palavras).")

        verdict = GateVerdict.APPROVED if score >= self.min_score else GateVerdict.REJECTED
        feedback = "PRD aprovado com especificações completas e alinhamento de marca." if verdict == GateVerdict.APPROVED else (
            f"PRD reprovado. Ajuste os seguintes pontos: {', '.join(issues)}"
        )

        return GateResult(
            gate_id=self.id,
            gate_name=self.name,
            verdict=verdict,
            score=max(0.0, min(1.0, score)),
            feedback=feedback,
            issues=issues,
        )


class ArchitectureGate(KonigGate):
    name: str = "architecture_gate"
    description: str = "Valida especificações arquiteturais, APIs, dados e segurança"
    min_score: float = 0.75
    checklist: List[str] = [
        "componentes",
        "api",
        "banco de dados",
        "segurança",
        "fluxo de dados",
    ]

    def validate(self, agent_output: str, context: Dict[str, Any] = None) -> GateResult:
        missing = self.run_checklist(agent_output)
        score = 1.0 - (len(missing) / max(len(self.checklist), 1))
        issues = [f"Item arquitetural faltante: {item}" for item in missing]

        verdict = GateVerdict.APPROVED if score >= self.min_score else GateVerdict.REJECTED
        feedback = "Arquitetura validada com sucesso." if verdict == GateVerdict.APPROVED else (
            f"Arquitetura reprovada. Faltam definições críticas: {', '.join(issues)}"
        )

        return GateResult(
            gate_id=self.id,
            gate_name=self.name,
            verdict=verdict,
            score=max(0.0, min(1.0, score)),
            feedback=feedback,
            issues=issues,
        )


class UIUXGate(KonigGate):
    """
    O Gate de Interface Adaptativa e Anti-Genérico.
    Reprova designs amadores, sem hierarquia, sem alinhamento de marca ou sem tokens semânticos definidos.
    """
    name: str = "ui_ux_gate"
    description: str = "Garante padrão visual adaptado ao branding, anti-default, acessível e com micro-interações intencionais"
    min_score: float = 0.80
    checklist: List[str] = [
        "tipografia",
        "paleta",
        "hierarquia",
        "responsiv",
        "interação",
    ]

    def validate(self, agent_output: str, context: Dict[str, Any] = None) -> GateResult:
        missing = self.run_checklist(agent_output)
        score = 1.0 - (len(missing) / max(len(self.checklist), 1))
        issues = [f"Requisito visual pendente: {item}" for item in missing]

        output_lower = agent_output.lower()
        
        # Penaliza termos genéricos de baixa qualidade / MVP tosco
        if "layout simples" in output_lower or "design básico" in output_lower:
            score -= 0.3
            issues.append("Reprovado por mediocridade visual: layout declarado como básico/simples.")

        # Bonifica design tokens ricos, identidade de marca, acessibilidade e micro-interações
        bonus_signals = [
            "branding", "arquétipo", "tokens", "semântic", "acessibilidade", 
            "wcag", "dark mode", "hover", "transition", "animação", "curated", 
            "hsl", "superfície", "contraste"
        ]
        bonus_count = sum(1 for signal in bonus_signals if signal in output_lower)
        score += min(0.2, bonus_count * 0.04)

        verdict = GateVerdict.APPROVED if score >= self.min_score else GateVerdict.REJECTED
        feedback = (
            "Design aprovado no padrão visual de elite, alinhado ao branding e com alto refinamento de UI/UX."
            if verdict == GateVerdict.APPROVED
            else f"Design reprovado pelo Gate de Interface. O produto não pode parecer um MVP genérico: {', '.join(issues)}"
        )

        return GateResult(
            gate_id=self.id,
            gate_name=self.name,
            verdict=verdict,
            score=max(0.0, min(1.0, score)),
            feedback=feedback,
            issues=issues,
        )


class CodeQualityGate(KonigGate):
    name: str = "code_quality_gate"
    description: str = "Valida robustez do código, ausência de placeholders vazios e tratamento de exceção"
    min_score: float = 0.75
    checklist: List[str] = [
        "def ",
        "return",
    ]

    def validate(self, agent_output: str, context: Dict[str, Any] = None) -> GateResult:
        missing = self.run_checklist(agent_output)
        score = 1.0 - (len(missing) / max(len(self.checklist), 1))
        issues = [f"Estrutura básica faltante: {item}" for item in missing]

        output_lower = agent_output.lower()
        if "pass" in output_lower and "TODO" in agent_output:
            score -= 0.25
            issues.append("Código contém placeholders inacabados (TODO/pass).")

        verdict = GateVerdict.APPROVED if score >= self.min_score else GateVerdict.REJECTED
        feedback = "Código validado pelo Quality Gate." if verdict == GateVerdict.APPROVED else (
            f"Código rejeitado na revisão técnica: {', '.join(issues)}"
        )

        return GateResult(
            gate_id=self.id,
            gate_name=self.name,
            verdict=verdict,
            score=max(0.0, min(1.0, score)),
            feedback=feedback,
            issues=issues,
        )


class QAGate(KonigGate):
    """
    Gate de Engenharia de QA e Testes.
    Inspirado no KONIG Staff QA e KONIG konig-qa-generate-tests.
    """
    name: str = "qa_gate"
    description: str = "Valida cobertura de testes, edge cases, assertions e cenário de homologação"
    min_score: float = 0.80
    checklist: List[str] = [
        "test",
        "assert",
        "edge case",
        "validação",
    ]

    def validate(self, agent_output: str, context: Dict[str, Any] = None) -> GateResult:
        missing = self.run_checklist(agent_output)
        score = 1.0 - (len(missing) / max(len(self.checklist), 1))
        issues = [f"Requisito de QA faltante: {item}" for item in missing]

        output_lower = agent_output.lower()
        if "assert" not in output_lower and "expect" not in output_lower:
            score -= 0.3
            issues.append("Nenhuma asserção de teste identificada.")

        verdict = GateVerdict.APPROVED if score >= self.min_score else GateVerdict.REJECTED
        feedback = "QA homologado com cobertura e validações consistentes." if verdict == GateVerdict.APPROVED else (
            f"Reprovado pelo QA Engineer. Testes ou critérios insuficientes: {', '.join(issues)}"
        )

        return GateResult(
            gate_id=self.id,
            gate_name=self.name,
            verdict=verdict,
            score=max(0.0, min(1.0, score)),
            feedback=feedback,
            issues=issues,
        )


# Registry Global de Gates
GATE_REGISTRY: Dict[str, KonigGate] = {
    "prd_gate": PRDGate(),
    "architecture_gate": ArchitectureGate(),
    "ui_ux_gate": UIUXGate(),
    "code_quality_gate": CodeQualityGate(),
    "qa_gate": QAGate(),
}

def get_gate(gate_name: str) -> Optional[KonigGate]:
    return GATE_REGISTRY.get(gate_name.lower())
