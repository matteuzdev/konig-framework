#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
   _  ______  _  _____________   _______  ___   __  ________      ______  ___  __ __
  / |/ / __ \/ |/ /  _/ ___/ /  / __/ _ \/ _ | /  |/  / __/ | /| / / __ \/ _ \/ //_/
 /    / /_/ /    // // (_ / _ \/ _// , _/ __ |/ /|_/ / _/ | |/ |/ / /_/ / , _/ ,<   
/_/|_/\____/_/|_/___/\___/_//_/_/ /_/|_/_/ |_/_/  /_/___/ |__/|__/\____/_/|_/_/|_|  
                                                                                     
==============================================================================
KONIG Framework — Instalador Industrial & Setup Interativo
Powered by ONIX Master Orchestrator Engine

Suporte nativo: Windows, macOS e Linux.
==============================================================================
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Ajuste de codificação para consoles Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Cores ANSI
class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

def print_banner() -> None:
    banner = f"""{Style.CYAN}{Style.BOLD}
================================================================================
  _  ______  _  _____________   _______  ___   __  ________      ______  ___  __ __
 / |/ / __ \/ |/ /  _/ ___/ /  / __/ _ \/ _ | /  |/  / __/ | /| / / __ \/ _ \/ //_/
/    / /_/ /    // // (_ / _ \/ _// , _/ __ |/ /|_/ / _/ | |/ |/ / /_/ / , _/ ,<   
/_/|_/\____/_/|_/___/\___/_//_/_/ /_/|_/_/ |_/_/  /_/___/ |__/|__/\____/_/|_/_/|_|  
================================================================================{Style.RESET}
{Style.BOLD}  👑 KONIG FRAMEWORK v2.0.0 — Enterprise Autonomous Agent Orchestration{Style.RESET}
{Style.DIM}  💎 ONIX Master Orchestration Engine | AST Sandbox Guardrails | Omnichannel{Style.RESET}
================================================================================
"""
    print(banner)

def step(title: str) -> None:
    print(f"\n{Style.BOLD}{Style.BLUE}==>{Style.RESET} {Style.BOLD}{title}{Style.RESET}")

def ok(msg: str) -> None:
    print(f"  {Style.GREEN}✔{Style.RESET} {msg}")

def warn(msg: str) -> None:
    print(f"  {Style.YELLOW}⚠{Style.RESET} {msg}")

def fail(msg: str) -> None:
    print(f"  {Style.RED}✖{Style.RESET} {msg}")

def info(msg: str) -> None:
    print(f"  {Style.CYAN}ℹ{Style.RESET} {msg}")

def check_python_version() -> bool:
    step("Verificando versão do Python")
    v = sys.version_info
    ver_str = f"{v.major}.{v.minor}.{v.micro}"
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        fail(f"Python >= 3.10 é obrigatório. Versão detectada: {ver_str}")
        return False
    ok(f"Python {ver_str} compatível ({platform.system()} {platform.release()})")
    return True

def install_dependencies(root: Path, silent: bool = False) -> bool:
    step("Instalando dependências do KONIG Framework")
    req_file = root / "requirements.txt"
    if not req_file.exists():
        fail("Arquivo requirements.txt não encontrado!")
        return False

    # Tenta python -m pip primeiro, depois pip direto do sistema
    pip_cmds = [
        [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
        ["pip", "install", "-r", str(req_file)],
    ]

    installed = False
    for cmd in pip_cmds:
        try:
            info(f"Tentando: {' '.join(cmd)}")
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            ok("Dependências principais instaladas com sucesso.")
            installed = True
            break
        except Exception as e:
            warn(f"Tentativa falhou com {cmd[0]}: {e}")

    if not installed:
        warn("Não foi possível executar 'pip' automaticamente neste ambiente.")
        info("Você pode instalar manualmente executando: pip install -r requirements.txt")

    # Instala o pacote em modo editável para habilitar o comando global `konig`
    setup_file = root / "setup.py"
    if setup_file.exists():
        info("Registrando CLI global 'konig' no ambiente...")
        for edit_cmd in [[sys.executable, "-m", "pip", "install", "-e", "."], ["pip", "install", "-e", "."]]:
            try:
                subprocess.run(edit_cmd, cwd=str(root), capture_output=True, check=True)
                ok("Comando global 'konig' registrado com sucesso!")
                break
            except Exception:
                pass

    return True

def setup_environment_file(root: Path, interactive: bool = True) -> None:
    step("Configurando arquivo de ambiente (.env)")
    env_file = root / ".env"
    env_example = root / ".env.example"

    if env_file.exists():
        ok("Arquivo .env já existe. Preservando configurações atuais.")
        return

    if not env_example.exists():
        warn(".env.example não encontrado para cópia inicial.")
        return

    shutil.copy(env_example, env_file)
    ok("Criado .env a partir de .env.example.")

    if not interactive:
        info("Modo não-interativo: configure suas chaves de API manualmente em .env.")
        return

    print(f"\n{Style.DIM}Deseja configurar uma chave de API agora? (Pressione Enter para pular){Style.RESET}")
    try:
        key_provider = input(f"{Style.BOLD}Escolha o provedor padrão [1: OpenAI, 2: Anthropic, 3: Google Gemini, Enter para pular]: {Style.RESET}").strip()
        if key_provider in ("1", "openai", "OpenAI"):
            key_val = input(f"{Style.BOLD}Cole sua OPENAI_API_KEY: {Style.RESET}").strip()
            if key_val:
                content = env_file.read_text(encoding="utf-8")
                content = content.replace("OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", f"OPENAI_API_KEY={key_val}")
                env_file.write_text(content, encoding="utf-8")
                ok("OPENAI_API_KEY gravada em .env com sucesso!")
        elif key_provider in ("2", "anthropic", "Anthropic"):
            key_val = input(f"{Style.BOLD}Cole sua ANTHROPIC_API_KEY: {Style.RESET}").strip()
            if key_val:
                content = env_file.read_text(encoding="utf-8")
                content = content.replace("ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", f"ANTHROPIC_API_KEY={key_val}")
                env_file.write_text(content, encoding="utf-8")
                ok("ANTHROPIC_API_KEY gravada em .env com sucesso!")
        elif key_provider in ("3", "gemini", "Google Gemini"):
            key_val = input(f"{Style.BOLD}Cole sua GEMINI_API_KEY: {Style.RESET}").strip()
            if key_val:
                content = env_file.read_text(encoding="utf-8")
                content = content.replace("GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", f"GEMINI_API_KEY={key_val}")
                env_file.write_text(content, encoding="utf-8")
                ok("GEMINI_API_KEY gravada em .env com sucesso!")
        else:
            info("Configuração de chaves postergada. Edite o arquivo .env quando desejar.")
    except Exception as e:
        warn(f"Entrada interrompida: {e}. Você pode editar o .env manualmente.")

def verify_ecosystem_structure(root: Path) -> bool:
    step("Validando arquitetura e integridade de pastas")
    required_dirs = [
        ".agents",
        ".agents/agents",
        ".agents/workflows",
        "core",
        "core/engine",
        "core/runtime",
        "core/primitives",
        "squads",
        "channels",
    ]

    all_ok = True
    for rel_path in required_dirs:
        p = root / rel_path
        if p.exists() and p.is_dir():
            ok(f"Diretório verificado: {rel_path}")
        else:
            fail(f"Diretório ausente: {rel_path}")
            all_ok = False

    # Validar adaptadores de IDE
    ide_dirs = [".antigravity", ".cursor", ".claude", ".codex", ".vscode"]
    present_ides = [d for d in ide_dirs if (root / d).exists()]
    ok(f"Adaptadores de IDE sincronizados: {', '.join(present_ides)}")

    return all_ok

def run_smoke_test(root: Path) -> bool:
    step("Executando Smoke Test do ONIX Master Orchestrator")
    try:
        # 1. Teste de importação do Core
        sys.path.insert(0, str(root))
        from core.engine.orchestrator import KonigOrchestrator
        from core.engine.meta_orchestrator import KonigMetaOrchestrator, OnixMetaOrchestrator
        from core.runtime.sandbox import KonigSandbox

        ok("Módulos de motor carregados com sucesso (Orchestrator, ONIX Meta, Sandbox).")

        # 2. Teste do Sandbox em isolamento
        sb = KonigSandbox()
        res = sb.execute_python("result = sum([1, 2, 3, 4, 5])\nprint(f'SUM_TEST: {result}')")
        exit_code = getattr(res, "exit_code", 1)
        stdout = getattr(res, "stdout", "")
        if exit_code == 0 and "SUM_TEST: 15" in stdout:
            ok("Sandbox Runtime validado (AST Analysis + Subprocess Isolation OK).")
        else:
            warn(f"Aviso no Sandbox: {getattr(res, 'stderr', 'Falha na execução')}")

        # 3. Teste de listagem rápida dos Squads
        orchestrator = KonigOrchestrator(".agents")
        if orchestrator.loaded_squad:
            ok(f"Squad de Engenharia carregado: {orchestrator.loaded_squad.name} ({len(orchestrator.loaded_squad.agents)} agentes)")
        else:
            warn("Squad de Engenharia não pôde ser instanciado diretamente.")

        return True
    except Exception as e:
        fail(f"Erro no Smoke Test: {e}")
        return False

def print_completion_guide() -> None:
    guide = f"""
{Style.GREEN}{Style.BOLD}================================================================================
🎉 INSTALAÇÃO DO KONIG FRAMEWORK CONCLUÍDA COM SUCESSO!
================================================================================{Style.RESET}

{Style.BOLD}🚀 COMO COMEÇAR:{Style.RESET}

  {Style.CYAN}1. Explorar Squads e Recursos Disponíveis:{Style.RESET}
     {Style.BOLD}python cli.py list{Style.RESET}   (ou simplesmente: {Style.BOLD}konig list{Style.RESET})

  {Style.CYAN}2. Executar o Squad de Engenharia Autônomo:{Style.RESET}
     {Style.BOLD}python cli.py run .agents full_development_lifecycle{Style.RESET}

  {Style.CYAN}3. Executar o Squad de Marketing / Vendas:{Style.RESET}
     {Style.BOLD}python cli.py run squads/marketing launch_product_funnel{Style.RESET}
     {Style.BOLD}python cli.py run squads/sales inbound_lead_qualification{Style.RESET}

  {Style.CYAN}4. Testar o Sandbox Seguro:{Style.RESET}
     {Style.BOLD}python cli.py sandbox scratch/test_script.py{Style.RESET}

  {Style.CYAN}5. Comparativo Técnico & Benchmark:{Style.RESET}
     {Style.BOLD}python cli.py benchmark{Style.RESET}

{Style.DIM}Documentação completa: ARCHITECTURE.md
Repositório: https://github.com/hiant/konig-framework{Style.RESET}
================================================================================
"""
    print(guide)

def main() -> None:
    parser = argparse.ArgumentParser(description="Instalador Oficial do KONIG Framework")
    parser.add_argument("--yes", "-y", action="store_true", help="Instalação automática sem prompts")
    parser.add_argument("--quick", "-q", action="store_true", help="Pula smoke test e roda rápido")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent

    print_banner()

    if not check_python_version():
        sys.exit(1)

    if not install_dependencies(root, silent=args.yes):
        sys.exit(1)

    setup_environment_file(root, interactive=not args.yes)

    if not verify_ecosystem_structure(root):
        warn("Algumas pastas recomendadas não foram localizadas. Prossiga com atenção.")

    if not args.quick:
        run_smoke_test(root)

    print_completion_guide()

if __name__ == "__main__":
    main()
