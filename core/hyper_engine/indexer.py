"""
KONIG Hyper-Engine — AST Indexer & Semantic Symbol Graph
Mapeia cirurgicamente qualquer repositório em um grafo semântico de símbolos (funções,
classes, métodos, tipos e dependências) usando AST incremental e hashes de Merkle Tree.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class SymbolKind(str, Enum):
    FUNCTION = "function"
    ASYNC_FUNCTION = "async_function"
    CLASS = "class"
    METHOD = "method"
    INTERFACE = "interface"
    TYPE_ALIAS = "type_alias"
    CONSTANT = "constant"
    MODULE = "module"


@dataclass
class Symbol:
    name: str
    kind: SymbolKind
    file_path: str
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    signature: Optional[str] = None
    parent_class: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # símbolos chamados internamente
    calls: List[str] = field(default_factory=list)         # nomes de chamadas identificadas
    content_hash: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["kind"] = self.kind.value
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Symbol:
        data_copy = data.copy()
        data_copy["kind"] = SymbolKind(data_copy["kind"])
        return cls(**data_copy)


@dataclass
class FileIndex:
    file_path: str
    content_hash: str
    symbols: List[Symbol] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    lines_count: int = 0
    size_bytes: int = 0
    last_indexed_ts: float = 0.0

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "symbols": [s.to_dict() for s in self.symbols],
            "imports": self.imports,
            "lines_count": self.lines_count,
            "size_bytes": self.size_bytes,
            "last_indexed_ts": self.last_indexed_ts,
        }

    @classmethod
    def from_dict(cls, data: dict) -> FileIndex:
        symbols = [Symbol.from_dict(s) for s in data.get("symbols", [])]
        return cls(
            file_path=data["file_path"],
            content_hash=data["content_hash"],
            symbols=symbols,
            imports=data.get("imports", []),
            lines_count=data.get("lines_count", 0),
            size_bytes=data.get("size_bytes", 0),
            last_indexed_ts=data.get("last_indexed_ts", 0.0),
        )


@dataclass
class IndexStats:
    total_files: int = 0
    total_symbols: int = 0
    total_lines: int = 0
    indexing_duration_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0


class ASTIndexer:
    """
    Motor industrial de indexação de repositório e grafo de símbolos.
    Suporta cache persistente, hash Merkle de arquivos e busca ranqueada de alta velocidade.
    """

    DEFAULT_IGNORE_DIRS = {
        ".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache",
        "dist", "build", ".next", ".vercel", ".coder", ".gemini", "coverage",
        "htmlcov", "scratch"
    }

    DEFAULT_EXTENSIONS = {
        ".py", ".ts", ".tsx", ".js", ".jsx", ".sql", ".yaml", ".yml", ".json"
    }

    def __init__(self, root_dir: str, cache_file: Optional[str] = None):
        self.root_dir = os.path.abspath(root_dir)
        self.cache_file = cache_file or os.path.join(self.root_dir, ".konig", "hyper_index.json")
        self.files_index: Dict[str, FileIndex] = {}
        self.symbol_lookup: Dict[str, List[Symbol]] = {}  # symbol_name -> List[Symbol]
        self.call_graph: Dict[str, Set[str]] = {}         # caller_name -> {callee_names}
        self.reverse_call_graph: Dict[str, Set[str]] = {} # callee_name -> {caller_names}
        self._load_cache()

    def _compute_sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _load_cache(self) -> None:
        """Carrega índice pré-compilado de disco se disponível."""
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for file_path, file_data in data.get("files", {}).items():
                    file_idx = FileIndex.from_dict(file_data)
                    self.files_index[file_path] = file_idx
            self._rebuild_lookup_tables()
        except Exception:
            # Em caso de cache corrompido, inicia vazio e reindexa limpo
            self.files_index.clear()

    def save_cache(self) -> None:
        """Persiste o índice em JSON compactado para inicialização instantânea."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        data = {
            "version": "2.0.0",
            "root_dir": self.root_dir,
            "saved_at": time.time(),
            "files": {p: f.to_dict() for p, f in self.files_index.items()}
        }
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _rebuild_lookup_tables(self) -> None:
        """Reconstrói tabelas hash de busca rápida e grafos de chamadas reversas."""
        self.symbol_lookup.clear()
        self.call_graph.clear()
        self.reverse_call_graph.clear()

        for file_idx in self.files_index.values():
            for sym in file_idx.symbols:
                self.symbol_lookup.setdefault(sym.name, []).append(sym)
                
                # Popula grafo de chamadas
                if sym.calls:
                    self.call_graph[sym.name] = set(sym.calls)
                    for callee in sym.calls:
                        self.reverse_call_graph.setdefault(callee, set()).add(sym.name)

    def index_repository(self, force_reindex: bool = False) -> IndexStats:
        """
        Escaneia recursivamente o repositório, parseando apenas arquivos novos ou alterados (Merkle Hash).
        """
        start_time = time.perf_counter()
        stats = IndexStats()

        current_files: Set[str] = set()

        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in self.DEFAULT_IGNORE_DIRS]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in self.DEFAULT_EXTENSIONS:
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")
                current_files.add(rel_path)

                try:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except Exception:
                    continue

                content_hash = self._compute_sha256(content)
                lines_count = content.count("\n") + 1
                size_bytes = len(content.encode("utf-8"))

                # Verifica se arquivo já está em cache e não mudou
                if not force_reindex and rel_path in self.files_index:
                    if self.files_index[rel_path].content_hash == content_hash:
                        stats.cache_hits += 1
                        stats.total_lines += self.files_index[rel_path].lines_count
                        stats.total_symbols += len(self.files_index[rel_path].symbols)
                        continue

                # Arquivo novo ou modificado -> Parseia AST
                stats.cache_misses += 1
                symbols, imports = self._parse_file(rel_path, content, ext)

                file_idx = FileIndex(
                    file_path=rel_path,
                    content_hash=content_hash,
                    symbols=symbols,
                    imports=imports,
                    lines_count=lines_count,
                    size_bytes=size_bytes,
                    last_indexed_ts=time.time(),
                )
                self.files_index[rel_path] = file_idx
                stats.total_lines += lines_count
                stats.total_symbols += len(symbols)

        # Remove do índice arquivos deletados do disco
        deleted_files = set(self.files_index.keys()) - current_files
        for df in deleted_files:
            del self.files_index[df]

        self._rebuild_lookup_tables()
        self.save_cache()

        stats.total_files = len(self.files_index)
        stats.indexing_duration_ms = (time.perf_counter() - start_time) * 1000.0
        return stats

    def _parse_file(self, rel_path: str, content: str, ext: str) -> Tuple[List[Symbol], List[str]]:
        """Direciona o parsing estático de acordo com a extensão do arquivo."""
        if ext == ".py":
            return self._parse_python_ast(rel_path, content)
        elif ext in {".ts", ".tsx", ".js", ".jsx"}:
            return self._parse_js_ts(rel_path, content)
        return [], []

    def _parse_python_ast(self, rel_path: str, content: str) -> Tuple[List[Symbol], List[str]]:
        """Parse profundo da árvore sintática abstrata nativa do Python."""
        symbols: List[Symbol] = []
        imports: List[str] = []

        try:
            tree = ast.parse(content, filename=rel_path)
        except SyntaxError:
            # Em caso de erro de sintaxe, faz fallback heurístico por regex
            return self._parse_python_regex_fallback(rel_path, content)

        for node in ast.iter_child_nodes(tree):
            # 1. Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for alias in node.names:
                    imports.append(f"{mod}.{alias.name}")

            # 2. Funções síncronas de nível de módulo
            elif isinstance(node, ast.FunctionDef):
                symbols.append(self._build_py_function_symbol(node, rel_path, is_async=False))

            # 3. Funções assíncronas de nível de módulo
            elif isinstance(node, ast.AsyncFunctionDef):
                symbols.append(self._build_py_function_symbol(node, rel_path, is_async=True))

            # 4. Classes e seus métodos internos
            elif isinstance(node, ast.ClassDef):
                class_sym = self._build_py_class_symbol(node, rel_path)
                symbols.append(class_sym)

                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_sym = self._build_py_function_symbol(
                            item, rel_path, is_async=isinstance(item, ast.AsyncFunctionDef), parent_class=node.name
                        )
                        symbols.append(method_sym)

        return symbols, imports

    def _build_py_function_symbol(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, rel_path: str, is_async: bool = False, parent_class: Optional[str] = None
    ) -> Symbol:
        docstring = ast.get_docstring(node)
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)

        # Extrai decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(f"{ast.unparse(dec.value)}.{dec.attr}")
            elif hasattr(ast, "unparse"):
                decorators.append(ast.unparse(dec))

        # Extrai assinatura tipada
        args_str = ""
        returns_str = ""
        if hasattr(ast, "unparse"):
            args_list = []
            for a in node.args.args:
                arg_repr = a.arg
                if a.annotation:
                    arg_repr += f": {ast.unparse(a.annotation)}"
                args_list.append(arg_repr)
            args_str = ", ".join(args_list)
            if node.returns:
                returns_str = f" -> {ast.unparse(node.returns)}"

        prefix = "async def " if is_async else "def "
        signature = f"{prefix}{node.name}({args_str}){returns_str}"

        # Detecta chamadas de funções invocadas no corpo
        calls = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                if isinstance(sub.func, ast.Name):
                    calls.add(sub.func.id)
                elif isinstance(sub.func, ast.Attribute):
                    calls.add(sub.func.attr)

        kind = SymbolKind.METHOD if parent_class else (SymbolKind.ASYNC_FUNCTION if is_async else SymbolKind.FUNCTION)

        return Symbol(
            name=node.name,
            kind=kind,
            file_path=rel_path,
            start_line=start_line,
            end_line=end_line,
            docstring=docstring,
            signature=signature,
            parent_class=parent_class,
            decorators=decorators,
            calls=sorted(list(calls)),
        )

    def _build_py_class_symbol(self, node: ast.ClassDef, rel_path: str) -> Symbol:
        docstring = ast.get_docstring(node)
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)

        bases = []
        if hasattr(ast, "unparse"):
            bases = [ast.unparse(b) for b in node.bases]
        bases_str = f"({', '.join(bases)})" if bases else ""
        signature = f"class {node.name}{bases_str}"

        return Symbol(
            name=node.name,
            kind=SymbolKind.CLASS,
            file_path=rel_path,
            start_line=start_line,
            end_line=end_line,
            docstring=docstring,
            signature=signature,
        )

    def _parse_python_regex_fallback(self, rel_path: str, content: str) -> Tuple[List[Symbol], List[str]]:
        """Fallback leve via regex quando o arquivo contém erro de sintaxe temporário."""
        symbols: List[Symbol] = []
        imports: List[str] = []
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            fn_match = re.match(r"^\s*(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", line)
            if fn_match:
                name = fn_match.group(1)
                is_async = "async " in line
                symbols.append(Symbol(
                    name=name,
                    kind=SymbolKind.ASYNC_FUNCTION if is_async else SymbolKind.FUNCTION,
                    file_path=rel_path,
                    start_line=idx,
                    end_line=idx,
                    signature=line.strip()
                ))
            cls_match = re.match(r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
            if cls_match:
                name = cls_match.group(1)
                symbols.append(Symbol(
                    name=name,
                    kind=SymbolKind.CLASS,
                    file_path=rel_path,
                    start_line=idx,
                    end_line=idx,
                    signature=line.strip()
                ))
            imp_match = re.match(r"^\s*(?:from\s+([a-zA-Z0-9_.]+)\s+)?import\s+([a-zA-Z0-9_., ]+)", line)
            if imp_match:
                imports.append(line.strip())

        return symbols, imports

    def _parse_js_ts(self, rel_path: str, content: str) -> Tuple[List[Symbol], List[str]]:
        """Parser estático heurístico de TypeScript / JavaScript."""
        symbols: List[Symbol] = []
        imports: List[str] = []
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            # Imports
            if re.match(r"^\s*import\s+", line):
                imports.append(line.strip())
                continue

            # Funções exportadas
            fn_match = re.match(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", line)
            if fn_match:
                name = fn_match.group(1)
                is_async = "async " in line
                symbols.append(Symbol(
                    name=name,
                    kind=SymbolKind.ASYNC_FUNCTION if is_async else SymbolKind.FUNCTION,
                    file_path=rel_path,
                    start_line=idx,
                    end_line=idx,
                    signature=line.strip().rstrip("{").strip()
                ))
                continue

            # Classes
            cls_match = re.match(r"^\s*(?:export\s+)?class\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
            if cls_match:
                name = cls_match.group(1)
                symbols.append(Symbol(
                    name=name,
                    kind=SymbolKind.CLASS,
                    file_path=rel_path,
                    start_line=idx,
                    end_line=idx,
                    signature=line.strip().rstrip("{").strip()
                ))
                continue

            # Interfaces (TS)
            int_match = re.match(r"^\s*(?:export\s+)?interface\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
            if int_match:
                name = int_match.group(1)
                symbols.append(Symbol(
                    name=name,
                    kind=SymbolKind.INTERFACE,
                    file_path=rel_path,
                    start_line=idx,
                    end_line=idx,
                    signature=line.strip().rstrip("{").strip()
                ))
                continue

            # Const arrow functions
            arrow_match = re.match(r"^\s*(?:export\s+)?const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", line)
            if arrow_match:
                name = arrow_match.group(1)
                symbols.append(Symbol(
                    name=name,
                    kind=SymbolKind.FUNCTION,
                    file_path=rel_path,
                    start_line=idx,
                    end_line=idx,
                    signature=line.strip().rstrip("{").strip()
                ))

        return symbols, imports

    # =========================================================================
    # APIs de Consulta Rápida (Sub-milissegundo para o Context Builder)
    # =========================================================================

    def search_symbols(self, query: str, limit: int = 10) -> List[Symbol]:
        """
        Busca ranqueada de símbolos por exatidão, prefixo, substring e relevância.
        """
        q = query.strip().lower()
        if not q:
            return []

        scored_results: List[Tuple[float, Symbol]] = []

        for name, sym_list in self.symbol_lookup.items():
            name_lower = name.lower()
            for sym in sym_list:
                score = 0.0

                if name_lower == q:
                    score = 100.0  # Match exato
                elif name_lower.startswith(q):
                    score = 75.0   # Prefixo direto
                elif q in name_lower:
                    score = 50.0   # Substring no nome
                elif sym.docstring and q in sym.docstring.lower():
                    score = 25.0   # Encontrado no docstring
                
                # Bonus para símbolos com mais chamadas no grafo
                if score > 0:
                    score += min(len(sym.calls), 10)
                    scored_results.append((score, sym))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [sym for _, sym in scored_results[:limit]]

    def find_symbol(self, name: str) -> Optional[Symbol]:
        """Retorna a primeira definição canônica encontrada para um símbolo."""
        candidates = self.symbol_lookup.get(name, [])
        return candidates[0] if candidates else None

    def get_file_outline(self, rel_path: str) -> List[Symbol]:
        """Retorna a lista estruturada de símbolos contidos em um arquivo."""
        norm_path = rel_path.replace("\\", "/")
        file_idx = self.files_index.get(norm_path)
        return file_idx.symbols if file_idx else []

    def get_callers(self, symbol_name: str) -> List[Symbol]:
        """Retorna quais símbolos chamam a função/classe consultada (Grafo Reverso)."""
        caller_names = self.reverse_call_graph.get(symbol_name, set())
        results = []
        for cname in caller_names:
            sym = self.find_symbol(cname)
            if sym:
                results.append(sym)
        return results

    def get_callees(self, symbol_name: str) -> List[Symbol]:
        """Retorna quais símbolos são invocados internamente pela função/classe consultada."""
        callee_names = self.call_graph.get(symbol_name, set())
        results = []
        for cname in callee_names:
            sym = self.find_symbol(cname)
            if sym:
                results.append(sym)
        return results
