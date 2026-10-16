"""
KONIG Hyper-Engine — High-Performance Autonomous Code Intelligence Core.
Provides real-time AST parsing, codebase symbol graphs, speculative inline diffs,
and sub-50ms context building without token stuffing.
"""

from core.hyper_engine.indexer import ASTIndexer, Symbol, SymbolKind, FileIndex
from core.hyper_engine.context_builder import ContextBuilder, ContextPacket
from core.hyper_engine.diff_streamer import DiffStreamer, DiffResult, DiffHunk
from core.hyper_engine.edit_engine import HyperEditEngine

__all__ = [
    "ASTIndexer",
    "Symbol",
    "SymbolKind",
    "FileIndex",
    "ContextBuilder",
    "ContextPacket",
    "DiffStreamer",
    "DiffResult",
    "DiffHunk",
    "HyperEditEngine",
]
