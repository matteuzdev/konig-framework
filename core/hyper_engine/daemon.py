"""
KONIG Hyper-Engine — Local Daemon & File Watcher Bridge
Servidor local de altíssima velocidade (FastAPI / Uvicorn) que mantém o grafo de código
sempre aquecido em memória via watcher incremental de arquivos e expõe endpoints RPC
para extensões de IDE e ferramentas de linha de comando.
"""

from __future__ import annotations

import os
import sys
import threading
import time
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from core.hyper_engine.indexer import ASTIndexer, IndexStats
from core.hyper_engine.context_builder import ContextBuilder
from core.hyper_engine.diff_streamer import DiffStreamer
from core.hyper_engine.edit_engine import HyperEditEngine


class EditRequest(BaseModel):
    file: str = Field(..., description="Caminho relativo do arquivo no repositório")
    instruction: str = Field(..., description="Instrução do que deve ser alterado")
    symbol: Optional[str] = Field(None, description="Nome do símbolo específico")
    auto_apply: bool = Field(False, description="Se True, grava alteração em disco com backup .undo")
    dry_run: bool = Field(False, description="Se True, apenas calcula o diff sem aplicar")


class UndoRequest(BaseModel):
    file: str = Field(..., description="Caminho do arquivo a ser revertido")


class SaveRequest(BaseModel):
    file: str = Field(..., description="Caminho relativo do arquivo no repositório")
    content: str = Field(..., description="Novo conteúdo a ser salvo no arquivo")


class FileWatcher:
    """
    Watcher de arquivos portátil e de baixo consumo de recursos (Zero Dependências Externas).
    Escaneia timestamps de modificação em background a cada 1.0s.
    """

    def __init__(self, indexer: ASTIndexer, poll_interval: float = 1.0):
        self.indexer = indexer
        self.poll_interval = poll_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._mtimes: Dict[str, float] = {}

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _watch_loop(self) -> None:
        while self._running:
            time.sleep(self.poll_interval)
            try:
                changed = False
                for rel_path, file_idx in list(self.indexer.files_index.items()):
                    full_path = os.path.join(self.indexer.root_dir, rel_path)
                    if not os.path.exists(full_path):
                        changed = True
                        break
                    mtime = os.path.getmtime(full_path)
                    if rel_path in self._mtimes and mtime > self._mtimes[rel_path]:
                        changed = True
                        self._mtimes[rel_path] = mtime
                    elif rel_path not in self._mtimes:
                        self._mtimes[rel_path] = mtime

                if changed:
                    self.indexer.index_repository(force_reindex=False)
            except Exception:
                pass


def create_hyper_engine_app(root_dir: str = ".") -> FastAPI:
    """Cria e configura a aplicação FastAPI do Hyper-Engine Daemon."""
    app = FastAPI(
        title="KONIG Hyper-Engine Local Daemon",
        description="Servidor local de inteligência de código e orquestração de diffs",
        version="2.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    abs_root = os.path.abspath(root_dir)
    indexer = ASTIndexer(abs_root)
    # Primeira indexação na inicialização
    stats = indexer.index_repository()
    context_builder = ContextBuilder(indexer, max_tokens=3000)
    diff_streamer = DiffStreamer(abs_root)
    edit_engine = HyperEditEngine(abs_root)

    watcher = FileWatcher(indexer, poll_interval=1.0)
    watcher.start()

    @app.on_event("shutdown")
    def on_shutdown():
        watcher.stop()

    @app.get("/", response_class=HTMLResponse)
    @app.get("/workbench", response_class=HTMLResponse)
    def get_workbench():
        """Retorna a interface visual do KONIG Hyper-Studio."""
        workbench_file = os.path.join(os.path.dirname(__file__), "workbench.html")
        if os.path.exists(workbench_file):
            with open(workbench_file, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>KONIG Hyper-Studio</h1>"

    @app.get("/api/status")
    def get_status():
        """Retorna telemetria em tempo real do repositório indexado."""
        return {
            "status": "online",
            "root_dir": abs_root,
            "total_files": len(indexer.files_index),
            "total_symbols": len(indexer.symbol_lookup),
            "total_calls_mapped": len(indexer.call_graph),
            "last_indexed_ts": time.time(),
        }

    @app.get("/api/search")
    def search_symbols(q: str = Query(..., description="Termo de busca"), limit: int = 10):
        """Busca ranqueada de funções, classes e métodos no grafo de código."""
        results = indexer.search_symbols(q, limit=limit)
        return {
            "query": q,
            "total": len(results),
            "symbols": [s.to_dict() for s in results],
        }

    @app.get("/api/outline")
    def get_outline(file: str = Query(..., description="Caminho relativo do arquivo")):
        """Retorna o outline de símbolos de um arquivo."""
        symbols = indexer.get_file_outline(file)
        return {
            "file": file,
            "total_symbols": len(symbols),
            "outline": [s.to_dict() for s in symbols],
        }

    @app.get("/api/context")
    def get_context(file: str, symbol: Optional[str] = None):
        """Gera um pacote cirúrgico de contexto SYNAPSE para o arquivo/símbolo alvo."""
        packet = context_builder.build_for_file_symbol(file, symbol or "")
        return {
            "target_file": packet.target_file,
            "target_symbol": packet.target_symbol,
            "target_range": packet.target_range,
            "estimated_tokens": packet.estimated_tokens,
            "symbols_included": packet.symbols_included,
            "dependencies_included": packet.dependencies_included,
            "prompt_context": packet.prompt_context,
        }

    @app.post("/api/edit")
    def apply_edit(req: EditRequest):
        """Executa ou simula edição cirúrgica com streaming de diff."""
        try:
            diff_res, status_msg = edit_engine.edit(
                file_path=req.file,
                instruction=req.instruction,
                symbol_name=req.symbol,
                dry_run=req.dry_run,
                auto_apply=req.auto_apply,
            )
            return {
                "success": True,
                "file": req.file,
                "status_message": status_msg,
                "lines_added": diff_res.lines_added,
                "lines_removed": diff_res.lines_removed,
                "is_empty": diff_res.is_empty,
                "unified_diff": diff_res.unified_diff,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/undo")
    def rollback_file(req: UndoRequest):
        """Reverte a alteração do arquivo usando o backup .undo."""
        success = edit_engine.undo(req.file)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum backup .undo encontrado para '{req.file}'.",
            )
        return {"success": True, "file": req.file, "message": "Rollback concluído com sucesso."}

    @app.get("/api/tree")
    def get_tree():
        """Retorna lista de todos os arquivos indexados no repositório."""
        files = list(indexer.files_index.keys())
        return {"files": sorted(files), "total": len(files)}

    @app.get("/api/file")
    def get_file_content(path: str = Query(..., description="Caminho relativo do arquivo")):
        """Lê o conteúdo real de um arquivo do repositório."""
        clean_path = path.replace("\\", "/").lstrip("/")
        full_path = os.path.normpath(os.path.join(abs_root, clean_path))
        if not full_path.startswith(abs_root):
            raise HTTPException(status_code=403, detail="Acesso negado fora da raiz do projeto.")
        if not os.path.isfile(full_path):
            raise HTTPException(status_code=404, detail=f"Arquivo '{clean_path}' não encontrado.")
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            ext = os.path.splitext(full_path)[1].lower()
            lang_map = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".html": "html",
                ".css": "css",
                ".json": "json",
                ".md": "markdown",
                ".yaml": "yaml",
                ".yml": "yaml",
                ".sh": "shell",
            }
            return {
                "path": clean_path,
                "content": content,
                "language": lang_map.get(ext, "plaintext"),
                "size_bytes": len(content.encode("utf-8")),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/save")
    def save_file_content(req: SaveRequest):
        """Salva o conteúdo no arquivo com backup .undo automático."""
        clean_path = req.file.replace("\\", "/").lstrip("/")
        full_path = os.path.normpath(os.path.join(abs_root, clean_path))
        if not full_path.startswith(abs_root):
            raise HTTPException(status_code=403, detail="Acesso negado fora da raiz do projeto.")
        try:
            if os.path.isfile(full_path):
                undo_path = full_path + ".undo"
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    old_content = f.read()
                with open(undo_path, "w", encoding="utf-8") as f:
                    f.write(old_content)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(req.content)

            indexer.index_repository(force_reindex=False)
            return {"success": True, "file": clean_path, "message": "Arquivo salvo com sucesso."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


def run_daemon(root_dir: str = ".", host: str = "127.0.0.1", port: int = 7331, open_browser: bool = False) -> None:
    """Inicia o Daemon local via Uvicorn e abre o Hyper-Studio no navegador."""
    import uvicorn
    import webbrowser

    url = f"http://{host}:{port}/"
    print("\n" + "=" * 70)
    print("⚡ KONIG HYPER-ENGINE DAEMON — Servidor Local de Inteligência de Código")
    print("=" * 70)
    print(f"📁 Diretório Raiz: {os.path.abspath(root_dir)}")
    print(f"🌐 Hyper-Studio URL: {url}")
    print(f"📡 API RPC Local: http://{host}:{port}/api/status")
    print(f"🔍 Endpoints RPC Disponíveis:")
    print(f"   • GET  /             -> Interface Web do Hyper-Studio (Workbench)")
    print(f"   • GET  /api/status   -> Telemetria e saúde do repositório")
    print(f"   • GET  /api/search   -> Busca ranqueada no grafo de símbolos")
    print(f"   • GET  /api/outline  -> Estrutura e AST de arquivos")
    print(f"   • GET  /api/context  -> Pacotes cirúrgicos SYNAPSE")
    print(f"   • POST /api/edit     -> Edição inline com diff streaming")
    print(f"   • POST /api/undo     -> Rollback atômico instantâneo")
    print(f"💡 Pressione CTRL+C no terminal para encerrar o daemon.\n")

    if open_browser:
        def _open():
            time.sleep(1.0)
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()

    app = create_hyper_engine_app(root_dir)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_daemon()
