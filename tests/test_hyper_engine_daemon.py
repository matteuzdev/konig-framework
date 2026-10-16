"""
Testes de Integração e Homologação dos Endpoints RPC do KONIG Hyper-Engine Daemon (Fase 3).
"""

import asyncio
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import httpx
from core.hyper_engine.daemon import create_hyper_engine_app


async def run_daemon_async_tests():
    print("=" * 70)
    print("[KONIG HYPER-ENGINE] - TESTE DE BANCADA DAEMON & RPC (FASE 3)")
    print("=" * 70)

    app = create_hyper_engine_app(root_dir=repo_root)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Teste de /api/status
        res = await client.get("/api/status")
        assert res.status_code == 200, f"Status esperado 200, obteve {res.status_code}"
        data = res.json()
        print("\n[GET /api/status]")
        print(f"  - Status do Daemon: {data['status']}")
        print(f"  - Total de Arquivos: {data['total_files']}")
        print(f"  - Total de Simbolos: {data['total_symbols']}")
        assert data["total_files"] > 10
        assert data["total_symbols"] > 20

        # 2. Teste de /api/search
        res = await client.get("/api/search?q=KonigOrchestrator&limit=3")
        assert res.status_code == 200
        data = res.json()
        print("\n[GET /api/search?q=KonigOrchestrator]")
        print(f"  - Resultados Encontrados: {data['total']}")
        assert data["total"] > 0
        top_sym = data["symbols"][0]
        print(f"  - Top Simbolo: [{top_sym['kind']}] {top_sym['name']} em {top_sym['file_path']}")
        assert top_sym["name"] == "KonigOrchestrator"

        # 3. Teste de /api/outline
        res = await client.get("/api/outline?file=core/engine/orchestrator.py")
        assert res.status_code == 200
        data = res.json()
        print("\n[GET /api/outline?file=core/engine/orchestrator.py]")
        print(f"  - Simbolos no Arquivo: {data['total_symbols']}")
        assert data["total_symbols"] > 5

        # 4. Teste de /api/context (SYNAPSE Packet)
        res = await client.get("/api/context?file=core/engine/orchestrator.py&symbol=run_workflow")
        assert res.status_code == 200
        data = res.json()
        print("\n[GET /api/context?file=core/engine/orchestrator.py&symbol=run_workflow]")
        print(f"  - Alvo: {data['target_file']} -> {data['target_symbol']}")
        print(f"  - Tokens Estimados: {data['estimated_tokens']}")
        assert data["estimated_tokens"] > 0 and data["estimated_tokens"] < 4000

        # 5. Teste de POST /api/edit (Dry-Run)
        edit_payload = {
            "file": "core/hyper_engine/__init__.py",
            "instruction": "Adicionar docstring com metadados",
            "dry_run": True,
            "auto_apply": False,
        }
        res = await client.post("/api/edit", json=edit_payload)
        assert res.status_code == 200
        data = res.json()
        print("\n[POST /api/edit (Dry-Run)]")
        print(f"  - Sucesso: {data['success']}")
        print(f"  - Mensagem de Status: {data['status_message']}")
        print(f"  - Linhas Adicionadas: {data['lines_added']}")
        assert data["success"] is True

        print("\n" + "=" * 70)
        print("[OK] HOMOLOGACAO: TODOS OS ENDPOINTS DO HYPER-ENGINE DAEMON ESTAO ONLINE!")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_daemon_async_tests())
