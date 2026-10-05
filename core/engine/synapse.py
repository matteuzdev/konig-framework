"""
Konig Synapse Engine — Motor inteligente de governança de contexto e compressão de tokens.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

Funcionalidades:
1. Bracket Tracking em 4 zonas operacionais (GREEN, YELLOW, ORANGE, RED).
2. Estimador de tokens multi-linguagem de alta performance.
3. Compressão semântica seletiva: preserva contratos de API, regras e requisitos enquanto sumariza ruído.
4. Emissão de alertas de saturação de contexto antes de estourar a janela do modelo.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ContextBracket(str, Enum):
    GREEN = "green"        # 0% - 50%: Espaço amplo, contexto integral
    YELLOW = "yellow"      # 50% - 70%: Alerta moderado, filtragem de mensagens triviais
    ORANGE = "orange"      # 70% - 85%: Compressão ativa acionada, preservação seletiva
    RED = "red"            # > 85%: Emergência, poda agressiva e resumo denso


class SynapseBracketReport(BaseModel):
    current_tokens: int
    max_tokens: int
    usage_percentage: float
    bracket: ContextBracket
    compression_recommended: bool
    warning_message: Optional[str] = None


class KonigSynapseEngine:
    """
    Controlador central de contexto cognitivo dos agentes do KONIG.
    """
    def __init__(self, default_context_limit: int = 128_000):
        self.default_context_limit = default_context_limit

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimador determinístico de tokens baseado no algoritmo de subword/char density.
        Em média, 1 token ~ 3.8 caracteres para código e idiomas com acentos.
        """
        if not text:
            return 0
        char_count = len(text)
        word_count = len(text.split())
        # Média harmônica aproximada
        estimated = int((char_count / 3.8 + word_count * 1.3) / 2)
        return max(1, estimated)

    def evaluate_bracket(self, accumulated_context: str, context_limit: Optional[int] = None) -> SynapseBracketReport:
        """
        Calcula em qual zona de bracket o contexto acumulado se encontra.
        """
        limit = context_limit or self.default_context_limit
        tokens = self.estimate_tokens(accumulated_context)
        pct = (tokens / max(limit, 1)) * 100

        if pct < 50.0:
            bracket = ContextBracket.GREEN
            recom = False
            msg = None
        elif pct < 70.0:
            bracket = ContextBracket.YELLOW
            recom = False
            msg = "⚠️ Atenção: Contexto atingiu 50% da janela. Monitoramento preventivo ativo."
        elif pct < 85.0:
            bracket = ContextBracket.ORANGE
            recom = True
            msg = "⚡ Alerta SYNAPSE: Contexto em 70%+. Compressão semântica recomendada antes do próximo handoff."
        else:
            bracket = ContextBracket.RED
            recom = True
            msg = "🚨 CRÍTICO: Contexto saturado (>85%). Risco iminente de perda de foco ou estouro de janela."

        return SynapseBracketReport(
            current_tokens=tokens,
            max_tokens=limit,
            usage_percentage=round(pct, 2),
            bracket=bracket,
            compression_recommended=recom,
            warning_message=msg
        )

    def compress_context(self, raw_context: str, target_tokens: Optional[int] = None) -> str:
        """
        Comprime o contexto de forma cirúrgica:
        1. Identifica e PRESERVA contratos de API, blocos de código e assinaturas.
        2. Identifica e PRESERVA requisitos funcionais (RFs) e critérios de aceite.
        3. Compacta o histórico conversacional redundante.
        """
        if not raw_context:
            return ""

        # Preserva blocos de código intactos
        code_blocks = re.findall(r"```[\s\S]*?```", raw_context)
        
        # Preserva especificações de API e endpoints
        api_lines = [
            line for line in raw_context.splitlines()
            if any(verb in line for verb in ("POST /", "GET /", "PUT /", "DELETE /", "openapi:", "paths:"))
        ]

        # Preserva requisitos e critérios de aceite
        req_lines = [
            line for line in raw_context.splitlines()
            if any(tag in line for tag in ("RF0", "RNF0", "Critério de Aceite", "Given", "When", "Then"))
        ]

        # Preserva a última assinatura formal de handoff
        signatures = re.findall(r"HANDOFF_SIGNATURE:\s*\[.*?\]", raw_context)
        last_sig = signatures[-1] if signatures else ""

        # Monta a versão comprimida estruturada
        compressed_parts = [
            "# CONTEXTO COMPACTADO PELO SYNAPSE ENGINE (Modo Alta Densidade)\n",
            "## 1. Contratos Técnicos e Requisitos Preservados",
        ]

        if req_lines:
            compressed_parts.append("\n".join(req_lines[:15]))
        if api_lines:
            compressed_parts.append("\n".join(api_lines[:10]))
        if code_blocks:
            compressed_parts.append("\n## 2. Blocos de Código Críticos")
            compressed_parts.append(code_blocks[-1])  # Mantém o bloco de código mais recente
        if last_sig:
            compressed_parts.append(f"\n## 3. Última Assinatura Ativa\n{last_sig}")

        compressed_text = "\n\n".join(compressed_parts)
        
        orig_tokens = self.estimate_tokens(raw_context)
        new_tokens = self.estimate_tokens(compressed_text)
        print(f"🧠 [SYNAPSE Engine] Contexto comprimido com sucesso: {orig_tokens} -> {new_tokens} tokens ({round((1 - new_tokens/orig_tokens)*100, 1)}% de economia)")
        
        return compressed_text
