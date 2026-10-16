"""
KONIG Hyper-Engine — SYNAPSE Context Builder
Constrói pacotes cirúrgicos de contexto de alta densidade sem inchar a janela de tokens.
Substitui o 'context stuffing' ingênuo por fatiamento de AST e extração seletiva do grafo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional, Set

from core.hyper_engine.indexer import ASTIndexer, Symbol, SymbolKind


@dataclass
class ContextPacket:
    target_file: str
    target_symbol: Optional[str] = None
    target_range: Optional[tuple[int, int]] = None
    prompt_context: str = ""
    estimated_tokens: int = 0
    symbols_included: List[str] = field(default_factory=list)
    dependencies_included: List[str] = field(default_factory=list)


class ContextBuilder:
    """
    Construtor cirúrgico de contexto baseado no grafo de símbolos do ASTIndexer.
    Garante que o modelo receba apenas o estritamente necessário para editar com precisão.
    """

    def __init__(self, indexer: ASTIndexer, max_tokens: int = 3000):
        self.indexer = indexer
        self.max_tokens = max_tokens

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def build_for_file_symbol(
        self, rel_path: str, symbol_name: str, include_callers: bool = True
    ) -> ContextPacket:
        """
        Gera um pacote de contexto focado em um símbolo específico de um arquivo.
        """
        norm_path = rel_path.replace("\\", "/")
        full_path = os.path.join(self.indexer.root_dir, norm_path)

        if not os.path.exists(full_path):
            return ContextPacket(target_file=norm_path, prompt_context=f"Arquivo não encontrado: {norm_path}")

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        file_outline = self.indexer.get_file_outline(norm_path)
        target_sym: Optional[Symbol] = None

        for sym in file_outline:
            if sym.name == symbol_name:
                target_sym = sym
                break

        if not target_sym:
            # Fallback para busca global se não achou no arquivo indicado
            target_sym = self.indexer.find_symbol(symbol_name)

        context_parts: List[str] = []
        symbols_included: List[str] = []
        dependencies_included: List[str] = []

        context_parts.append(f"### [ARQUIVO ALVO: {norm_path}]")

        # 1. Imports do arquivo alvo (topo)
        file_idx = self.indexer.files_index.get(norm_path)
        if file_idx and file_idx.imports:
            imports_snippet = "\n".join(file_idx.imports[:15])
            context_parts.append(f"```python\n# Imports Relevantes:\n{imports_snippet}\n```\n")

        # 2. Código-fonte do Símbolo Alvo
        target_range = None
        if target_sym:
            s_line = max(1, target_sym.start_line)
            e_line = min(len(lines), target_sym.end_line)
            target_range = (s_line, e_line)
            symbol_code = "".join(lines[s_line - 1 : e_line])
            context_parts.append(f"#### Definição de `{target_sym.name}` (Linhas {s_line}-{e_line}):")
            context_parts.append(f"```python\n{symbol_code}\n```\n")
            symbols_included.append(target_sym.name)

            # 3. Dependências diretas (Callees): funções/classes chamadas internamente
            callees = self.indexer.get_callees(target_sym.name)
            if callees:
                context_parts.append("#### Dependências Diretas Invocadas (Assinaturas):")
                callee_signatures = []
                for c in callees[:8]:
                    sig = c.signature or c.name
                    doc = f"  # {c.docstring[:80]}..." if c.docstring else ""
                    callee_signatures.append(f"- `{sig}` em `{c.file_path}`{doc}")
                    dependencies_included.append(c.name)
                context_parts.append("\n".join(callee_signatures) + "\n")

            # 4. Invocadores (Callers): quem chama este símbolo no projeto
            if include_callers:
                callers = self.indexer.get_callers(target_sym.name)
                if callers:
                    context_parts.append("#### Onde este símbolo é invocado (Call Hierarchy):")
                    caller_notes = [f"- Chamado por `{c.name}` em `{c.file_path}:{c.start_line}`" for c in callers[:6]]
                    context_parts.append("\n".join(caller_notes) + "\n")

        else:
            # Se não especificou símbolo, envia outline do arquivo
            outline_str = "\n".join([f"- `{s.kind.value}` {s.signature or s.name} (L{s.start_line}-L{s.end_line})" for s in file_outline])
            context_parts.append(f"#### Outline de Estrutura do Arquivo:\n{outline_str}\n")

        full_text = "\n".join(context_parts)
        est_tokens = self._estimate_tokens(full_text)

        return ContextPacket(
            target_file=norm_path,
            target_symbol=symbol_name if target_sym else None,
            target_range=target_range,
            prompt_context=full_text,
            estimated_tokens=est_tokens,
            symbols_included=symbols_included,
            dependencies_included=dependencies_included,
        )

    def build_for_query(self, query: str, limit: int = 5) -> ContextPacket:
        """
        Gera um pacote de contexto respondendo a uma pergunta em linguagem natural sobre o `@codebase`.
        """
        symbols = self.indexer.search_symbols(query, limit=limit)
        context_parts: List[str] = [f"### [RESULTADOS DO GRAFO SEMÂNTICO PARA: '{query}']"]
        symbols_included: List[str] = []

        for sym in symbols:
            symbols_included.append(sym.name)
            doc = f"\n  Docstring: {sym.docstring}" if sym.docstring else ""
            calls_str = f"\n  Invoca: {', '.join(sym.calls[:5])}" if sym.calls else ""
            context_parts.append(
                f"- **`{sym.name}`** ({sym.kind.value})\n"
                f"  Arquivo: `{sym.file_path}:{sym.start_line}-{sym.end_line}`\n"
                f"  Assinatura: `{sym.signature}`"
                f"{doc}{calls_str}"
            )

        full_text = "\n\n".join(context_parts)
        return ContextPacket(
            target_file="multiple",
            prompt_context=full_text,
            estimated_tokens=self._estimate_tokens(full_text),
            symbols_included=symbols_included,
        )
