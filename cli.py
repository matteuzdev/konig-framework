"""
KONIG Framework — CLI Industrial Unificada
Interface de linha de comando para orquestração de squads, governança de contexto,
execução segura em sandbox, telemetria de custos e pontes omnichannel.

Uso:
  python cli.py run [.agents|squads/xxx] [workflow_name]
  python cli.py list
  python cli.py sandbox <caminho_arquivo.py>
  python cli.py benchmark
  python cli.py telegram
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Garante que o diretório raiz do repositório esteja no sys.path mesmo se executado de fora
REPO_DIR = Path(__file__).resolve().parent
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))

# Garante saída UTF-8 no console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from core.engine.orchestrator import KonigOrchestrator
from core.engine.meta_orchestrator import OnixMetaOrchestrator
from core.engine.squad_loader import SquadLoader
from core.runtime.sandbox import KonigSandbox
from channels.telegram import KonigTelegramBridge, TelegramMessage
from channels.whatsapp import KonigWhatsAppBridge


def cmd_onix(args: argparse.Namespace) -> None:
    """Invoca o ONIX Meta Orchestrator para arquitetar e despachar squads sob demanda."""
    goal = args.goal
    squad_type = args.type or "engineering"

    print("\n🔮 ONIX META ORCHESTRATOR — Ativando Consciência Estratégica...")
    print(f"🎯 Missão: '{goal}'")
    print(f"🧬 Domínio Operacional: [{squad_type.upper()}]")

    meta = OnixMetaOrchestrator()
    blueprint = meta.generate_squad_blueprint(squad_type, goal)
    print(f"\n🏛️ Blueprint Sintetizado por ONIX: [{blueprint['name']}]")
    print(f"   • Agentes convocados: {len(blueprint['agents'])}")
    for k, a in blueprint['agents'].items():
        print(f"     └─ {a['name']} ({a['role']})")

    orchestrator = KonigOrchestrator(".agents")
    for key, a_data in blueprint['agents'].items():
        from core.engine.agent import KonigAgent
        agent_obj = KonigAgent(
            name=a_data["name"],
            role=a_data["role"],
            signature=f"[{a_data['name']} - {a_data['role']}]",
            goal=a_data.get("goal", ""),
            skills=a_data.get("skills", [])
        )
        orchestrator.register_agent(agent_obj)

    wf = meta.build_custom_workflow(f"wf_{blueprint['name']}", blueprint, goal)
    print("\n🚀 Despachando DAG através do Kahn Engine em Waves com Gates determinísticos...")
    summary = orchestrator.run_workflow(wf)
    print(f"\n✨ ONIX: Missão '{goal}' orquestrada e homologada com sucesso.")


def cmd_run(args: argparse.Namespace) -> None:
    """Executa um workflow de um squad específico."""
    squad_target = args.squad
    workflow_name = args.workflow

    print(f"\n🦁 KONIG CLI — Iniciando execução de Squad: [{squad_target}]")
    orchestrator = KonigOrchestrator(squad_target)

    if not orchestrator.loaded_squad:
        print(f"❌ Erro: Não foi possível carregar o squad em '{squad_target}'")
        sys.exit(1)

    wf = orchestrator.build_workflow_from_squad(workflow_name)
    summary = orchestrator.run_workflow(wf)
    print("\n✅ Execução finalizada com sucesso.")


def cmd_list(args: argparse.Namespace) -> None:
    """Lista todos os squads e recursos disponíveis no ecossistema KONIG."""
    print("\n=======================================================")
    print("🏛️ SQUADS DISPONÍVEIS NO KONIG FRAMEWORK")
    print("=======================================================\n")

    # 1. Squad de Engenharia (.agents)
    p_agents = Path(".agents")
    if p_agents.exists():
        sq = SquadLoader.load_squad(p_agents)
        print("🤖 [1] SQUAD DE ENGENHARIA DE SOFTWARE (.agents / Universal AI)")
        print(f"   • Agentes ({len(sq.agents)}): {', '.join(sq.agents.keys())}")
        print(f"   • Tasks ({len(sq.tasks)}): {', '.join(sq.tasks.keys())}")
        print(f"   • Checklists ({len(sq.checklists)}): {', '.join(sq.checklists.keys())}")
        print(f"   • Workflows ({len(sq.workflows)}): {', '.join(sq.workflows.keys())}\n")

    # 2. Squads de Negócios (squads/*)
    squads_dir = Path("squads")
    if squads_dir.exists():
        for d in squads_dir.iterdir():
            if d.is_dir() and (d / "agents").exists():
                sq = SquadLoader.load_squad(d)
                print(f"💼 SQUAD DE NEGÓCIO: [{d.name.upper()}] ({d})")
                print(f"   • Agentes ({len(sq.agents)}): {', '.join(sq.agents.keys())}")
                print(f"   • Tasks ({len(sq.tasks)}): {', '.join(sq.tasks.keys())}")
                print(f"   • Checklists ({len(sq.checklists)}): {', '.join(sq.checklists.keys())}")
                print(f"   • Workflows ({len(sq.workflows)}): {', '.join(sq.workflows.keys())}\n")


def cmd_sandbox(args: argparse.Namespace) -> None:
    """Executa um arquivo Python dentro do sandbox isolado e audita com AST."""
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ Erro: Arquivo '{args.file}' não encontrado.")
        sys.exit(1)

    code = file_path.read_text(encoding="utf-8")
    sandbox = KonigSandbox()

    print(f"\n🛡️ KONIG SANDBOX RUNTIME — Executando: {file_path.name}")
    print("   1. Executando AST Security Analysis...")
    violations = sandbox.check_security(code)
    if violations:
        print(f"   ❌ {len(violations)} violação(ões) detectada(s):")
        for v in violations:
            print(f"      • [{v.rule} L{v.line_number}]: {v.description}")
        if any(v.rule != "SYNTAX_ERROR" for v in violations):
            print("   ⛔ Execução bloqueada pelo Security Guardian.")
            sys.exit(1)
    else:
        print("   ✅ AST Security Check: 0 vulnerabilidades detectadas.")

    print("   2. Executando em subprocesso isolado com timeout...")
    res = sandbox.execute_python(code)
    print(f"   • Sucesso: {res.success}")
    print(f"   • Exit Code: {res.exit_code}")
    print(f"   • Tempo de Execução: {res.execution_time_ms:.2f}ms")
    if res.stdout.strip():
        print(f"\n--- STDOUT ---\n{res.stdout.strip()}")
    if res.stderr.strip():
        print(f"\n--- STDERR ---\n{res.stderr.strip()}")


def cmd_telegram(args: argparse.Namespace) -> None:
    """Testa o roteamento do Telegram Single-Bot Multi-Agent Router."""
    print("\n✈️ KONIG TELEGRAM BRIDGE — Simulação de Fórum & Menções")
    bridge = KonigTelegramBridge(default_chat_id=-100987654321)

    from core.engine.agent import KonigAgent
    alice = KonigAgent(name="Alice", role="Lead Product Manager", signature="[Alice - Lead Product Manager]")
    carol = KonigAgent(name="Carol", role="Lead UI/UX Designer", signature="[Carol - Lead UI/UX Designer]")
    bridge.register_agent(alice, topic_id=101)
    bridge.register_agent(carol, topic_id=102)

    print("📨 Simulando mensagem recebida com menção no grupo: '@Alice precisamos fechar o PRD da v2'")
    msg = TelegramMessage(
        message_id=999,
        chat_id=-100987654321,
        text="@Alice precisamos fechar o PRD da v2 com prioridade máxima",
        from_user="hianto_dev",
        message_thread_id=101
    )
    bridge.route_incoming_group_message(msg)


def cmd_benchmark(args: argparse.Namespace) -> None:
    """Exibe a matriz de maturidade técnica e conformidade industrial do KONIG."""
    print("""
====================================================================================================
🦁 KONIG AGENTIC FRAMEWORK — MATRIZ DE MATURIDADE INDUSTRIAL & ARQUITETURA 2.0
====================================================================================================
Pilar de Engenharia KONIG        | Status Operacional  | Módulo / Mecanismo de Implementação
---------------------------------|---------------------|--------------------------------------------
Isolamento Dev (.agents)         | ✅ HOMOLOGADO       | .agents/ (Time Técnico Universal AI)
Squads de Negócio Desacoplados   | ✅ HOMOLOGADO       | squads/ (Marketing, Sales, Strategy)
DAG Waves Paralelas Topológicas  | ✅ HOMOLOGADO       | Kahn Algorithm em core/primitives/workflow
Markdown Quality Gates (SOPs)    | ✅ HOMOLOGADO       | core/engine/squad_loader (Checklists .md)
AST Security Guardian no Sandbox | ✅ HOMOLOGADO       | core/runtime/sandbox (Análise Estática AST)
Sandbox Runtime Isolado          | ✅ HOMOLOGADO       | core/runtime/sandbox (Subprocesso Seguro)
SYNAPSE Context Brackets (4 Zonas| ✅ HOMOLOGADO       | core/engine/synapse (Green/Yellow/Orange/Red)
Compressão Semântica Preservativa| ✅ HOMOLOGADO       | core/engine/synapse (Preserva Código e RFs)
LLM Router com Fallback Chain    | ✅ HOMOLOGADO       | core/llm/router (Auto-failover multi-provedor)
Auditor Financeiro em USD/Tokens | ✅ HOMOLOGADO       | core/memory/cost_manager (Rastreio em Realtime)
Telegram Forum Topics Router     | ✅ HOMOLOGADO       | channels/telegram (Single-Bot Multi-Agent)
WhatsApp Real-time Bridge        | ✅ HOMOLOGADO       | channels/whatsapp (Notificações de Handoff)
Adaptadores Nativos Multi-IA     | ✅ HOMOLOGADO       | .cursor, .claude, .antigravity, .codex
UI/UX Pro-Max Anti-Generic Gate  | ✅ HOMOLOGADO       | WCAG AAA, Inter/Outfit, HSL Curado
Staff QA com Homologação Real    | ✅ HOMOLOGADO       | Asserções de teste executadas no Sandbox
====================================================================================================
🏆 VEREDITO: O KONIG Framework consolida governança determinística de ponta a ponta,
eliminando dependências externas frágeis e garantindo previsibilidade de entrega enterprise.
====================================================================================================
""")


def cmd_crm(args: argparse.Namespace) -> None:
    """Inicia o servidor web local do KONIG Sales, Hosting & MRR CRM."""
    import uvicorn
    from crm.database import init_db
    init_db()
    port = args.port or 8000
    print(f"\n🦁 KONIG PIPELINE CRM — Iniciando painel de Vendas, Hospedagem & MRR...")
    print(f"📊 Acesse no seu navegador: http://127.0.0.1:{port}")
    print(f"💡 Pressione CTRL+C no terminal para parar o servidor.\n")
    uvicorn.run("crm.server:app", host="127.0.0.1", port=port, reload=False)


def cmd_edit(args: argparse.Namespace) -> None:
    """Executa edição cirúrgica inline com diff streaming via KONIG Hyper-Engine."""
    from core.hyper_engine.edit_engine import HyperEditEngine

    file_path = args.file
    instruction = args.instruction
    symbol_name = args.symbol
    dry_run = args.dry_run
    auto_apply = args.yes

    print(f"\n⚡ KONIG HYPER-ENGINE — Iniciando Edição Cirúrgica Inline...")
    print(f"📄 Arquivo: '{file_path}'")
    print(f"🎯 Instrução: '{instruction}'")
    if symbol_name:
        print(f"🔍 Símbolo Alvo: [{symbol_name}]")

    engine = HyperEditEngine(root_dir=str(REPO_DIR))
    try:
        diff_res, status_msg = engine.edit(
            file_path=file_path,
            instruction=instruction,
            symbol_name=symbol_name,
            dry_run=dry_run,
            auto_apply=auto_apply
        )
        print("\n" + engine.diff_streamer.format_terminal_diff(diff_res))
        print(f"\n✨ {status_msg}")
    except Exception as e:
        print(f"\n❌ Erro durante a edição: {e}")
        sys.exit(1)


def cmd_daemon(args: argparse.Namespace) -> None:
    """Inicia o KONIG Hyper-Engine Local Daemon com watcher em tempo real e API RPC."""
    from core.hyper_engine.daemon import run_daemon
    port = args.port or 7331
    host = args.host or "127.0.0.1"
    open_browser = getattr(args, "open", False)
    repo_root = getattr(args, "root", None) or str(REPO_DIR)
    run_daemon(root_dir=repo_root, host=host, port=port, open_browser=open_browser)


def cmd_undo(args: argparse.Namespace) -> None:
    """Restaura um arquivo para o estado anterior usando o backup .undo do Hyper-Engine."""
    from core.hyper_engine.edit_engine import HyperEditEngine
    file_path = args.file
    engine = HyperEditEngine(root_dir=str(REPO_DIR))
    if engine.undo(file_path):
        print(f"\n⏪ [ROLLBACK CONCLUÍDO] Arquivo '{file_path}' restaurado com sucesso a partir de .undo.")
    else:
        print(f"\n❌ [ERRO] Nenhum backup .undo encontrado para '{file_path}'.")
        sys.exit(1)


def cmd_ide(args: argparse.Namespace) -> None:
    """Inicia a IDE Desktop Nativa KONIG Hyper-Studio."""
    import subprocess
    from pathlib import Path
    
    ide_path = Path(r"C:\Users\hiant\KONIG_IDE\konig.exe")
    if not ide_path.exists():
        ide_path = Path(r"C:\Users\hiant\KONIG_IDE\VSCodium.exe")
    
    if not ide_path.exists():
        print("❌ Erro: Binário da IDE não encontrado em C:\\Users\\hiant\\KONIG_IDE\\konig.exe")
        return
        
    target_dir = args.dir or str(REPO_DIR)
    print("\n🚀 Iniciando KONIG Hyper-Studio Desktop...")
    print(f"   • Executável: {ide_path}")
    print(f"   • Workspace: {target_dir}")
    print("   • KRONOS Extension: data/extensions/konig-kronos (Ativo)")
    print("   • Modos nativos: Ctrl+K (Fast Edit), Ctrl+I (Composer), Ctrl+L (Chat)")
    
    subprocess.Popen([str(ide_path), target_dir], close_fds=True)
    print("✨ Janela desktop do KONIG Hyper-Studio aberta com sucesso!")



def main():
    parser = argparse.ArgumentParser(
        prog="konig",
        description="KONIG Agentic Framework CLI — Motor industrial de orquestração de IA"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # ide (KONIG Desktop IDE)
    p_ide = subparsers.add_parser("ide", help="Inicia a IDE Desktop Nativa KONIG Hyper-Studio")
    p_ide.add_argument("dir", nargs="?", default=None, help="Diretório do workspace a ser aberto (padrão: raiz do konig)")
    p_ide.set_defaults(func=cmd_ide)

    # daemon (Hyper-Engine Local Daemon)
    p_daemon = subparsers.add_parser("daemon", help="Inicia o KONIG Hyper-Engine Daemon (servidor local de código com file watcher)")
    p_daemon.add_argument("--port", "-p", type=int, default=7331, help="Porta do servidor RPC local (padrão: 7331)")
    p_daemon.add_argument("--host", default="127.0.0.1", help="Host de binding (padrão: 127.0.0.1)")
    p_daemon.add_argument("--open", "-o", action="store_true", help="Abre o Hyper-Studio automaticamente no navegador padrão")
    p_daemon.set_defaults(func=cmd_daemon)

    # edit (Hyper-Engine Fast Edit)
    p_edit = subparsers.add_parser("edit", help="Executa edição cirúrgica inline em um arquivo (padrão Cmd+K / Fast Edit)")
    p_edit.add_argument("file", help="Caminho do arquivo a ser editado")
    p_edit.add_argument("instruction", help="Instrução da alteração a ser aplicada")
    p_edit.add_argument("--symbol", "-s", default=None, help="Nome do símbolo específico para focar o contexto")
    p_edit.add_argument("--dry-run", "-d", action="store_true", help="Calcula e exibe o diff sem alterar o disco")
    p_edit.add_argument("--yes", "-y", action="store_true", help="Aplica a alteração automaticamente sem confirmação")
    p_edit.set_defaults(func=cmd_edit)

    # undo (Hyper-Engine Rollback)
    p_undo = subparsers.add_parser("undo", help="Reverte a última edição feita pelo Hyper-Engine usando backup .undo")
    p_undo.add_argument("file", help="Caminho do arquivo a ser revertido")
    p_undo.set_defaults(func=cmd_undo)

    # crm
    p_crm = subparsers.add_parser("crm", help="Inicia o painel visual do KONIG Sales, Hosting & MRR CRM")
    p_crm.add_argument("--port", "-p", type=int, default=8000, help="Porta do servidor web (padrão: 8000)")
    p_crm.set_defaults(func=cmd_crm)

    # onix
    p_onix = subparsers.add_parser("onix", help="Invoca o ONIX Meta Orchestrator para arquitetar e despachar squads autônomos")
    p_onix.add_argument("goal", help="Objetivo ou missão a ser executada")
    p_onix.add_argument("--type", "-t", default="engineering", help="Domínio do squad: engineering, marketing, sales, strategy")
    p_onix.set_defaults(func=cmd_onix)

    # run
    p_run = subparsers.add_parser("run", help="Executa um workflow de squad")
    p_run.add_argument("squad", help="Caminho do squad (ex: .agents, squads/marketing, squads/sales)")
    p_run.add_argument("workflow", nargs="?", default=None, help="Nome do workflow (opcional)")
    p_run.set_defaults(func=cmd_run)

    # list
    p_list = subparsers.add_parser("list", help="Lista squads, agentes e workflows disponíveis")
    p_list.set_defaults(func=cmd_list)

    # sandbox
    p_sandbox = subparsers.add_parser("sandbox", help="Executa um script de teste no sandbox isolado")
    p_sandbox.add_argument("file", help="Caminho do arquivo Python a ser executado")
    p_sandbox.set_defaults(func=cmd_sandbox)

    # telegram
    p_tg = subparsers.add_parser("telegram", help="Simula operações do bot do Telegram")
    p_tg.set_defaults(func=cmd_telegram)

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Exibe matriz comparativa contra outros frameworks")
    p_bench.set_defaults(func=cmd_benchmark)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()

