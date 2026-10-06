"""
Konig Sandbox Runtime — Execução segura e isolada de código para agentes.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

Funcionalidades:
1. Analisador estático AST para detecção de payloads maliciosos ou destrutivos.
2. Isolamento de processo em subprocess com timeout rígido configurável.
3. Diretório de trabalho isolado em sandbox temporário (workspace seguro).
4. Captura precisa de stdout, stderr, código de saída e tempo de execução.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SecurityViolation(BaseModel):
    rule: str
    description: str
    line_number: Optional[int] = None


class SandboxResult(BaseModel):
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time_ms: float
    security_violations: List[SecurityViolation] = Field(default_factory=list)
    timed_out: bool = False


class ASTSecurityAnalyzer(ast.NodeVisitor):
    """
    Analisa a árvore sintática abstrata (AST) do código Python
    para detectar operações proibidas antes da execução.
    """
    FORBIDDEN_CALLS = {
        "eval", "exec", "__import__", "compile"
    }
    FORBIDDEN_MODULES = {
        "ctypes", "winreg", "_winapi", "pty", "subprocess"
    }

    def __init__(self):
        self.violations: List[SecurityViolation] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name in self.FORBIDDEN_MODULES:
                self.violations.append(
                    SecurityViolation(
                        rule="FORBIDDEN_IMPORT",
                        description=f"Tentativa de importar módulo de baixo nível restrito: '{alias.name}'",
                        line_number=node.lineno
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module in self.FORBIDDEN_MODULES:
            self.violations.append(
                SecurityViolation(
                    rule="FORBIDDEN_IMPORT",
                    description=f"Tentativa de importar de módulo restrito: '{node.module}'",
                    line_number=node.lineno
                )
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_CALLS:
                self.violations.append(
                    SecurityViolation(
                        rule="FORBIDDEN_BUILTIN_CALL",
                        description=f"Chamada de função dinâmica perigosa não permitida: '{node.func.id}()'",
                        line_number=node.lineno
                    )
                )
        # Detecção de os.system, subprocess ou chamadas destrutivas
        elif isinstance(node.func, ast.Attribute):
            dangerous_attrs = (
                "system", "popen", "spawn", "Popen", "run", "call",
                "check_output", "check_call", "fork", "kill", "exit", "_exit"
            )
            if node.func.attr in dangerous_attrs:
                self.violations.append(
                    SecurityViolation(
                        rule="DANGEROUS_SYSTEM_CALL",
                        description=f"Chamada de sistema operacional não autorizada: '.{node.func.attr}()'",
                        line_number=node.lineno
                    )
                )
        self.generic_visit(node)


class KonigSandbox:
    """
    Runtime seguro de execução de scripts de desenvolvimento e testes.
    """
    def __init__(
        self,
        base_work_dir: Optional[str] = None,
        default_timeout_sec: float = 15.0,
        enable_ast_security: bool = True
    ):
        self.base_work_dir = Path(base_work_dir) if base_work_dir else Path("./scratch/sandbox")
        self.default_timeout_sec = default_timeout_sec
        self.enable_ast_security = enable_ast_security
        self.base_work_dir.mkdir(parents=True, exist_ok=True)

    def check_security(self, python_code: str) -> List[SecurityViolation]:
        """Executa a verificação de segurança estática."""
        if not self.enable_ast_security:
            return []

        try:
            tree = ast.parse(python_code)
            analyzer = ASTSecurityAnalyzer()
            analyzer.visit(tree)
            return analyzer.violations
        except SyntaxError as e:
            return [
                SecurityViolation(
                    rule="SYNTAX_ERROR",
                    description=f"Erro de sintaxe no código a ser executado: {e}",
                    line_number=e.lineno
                )
            ]

    def execute_code(self, code: str, **kwargs) -> SandboxResult:
        """Alias ergonômico para execute_python."""
        return self.execute_python(code, **kwargs)

    def execute_python(
        self,
        code: str,
        timeout_sec: Optional[float] = None,
        custom_env: Optional[Dict[str, str]] = None
    ) -> SandboxResult:
        """
        Executa código Python isolado em processo temporário seguro.
        """
        timeout = timeout_sec or self.default_timeout_sec
        start_time = time.perf_counter()

        # 1. Auditoria de Segurança Estática
        violations = self.check_security(code)
        critical_violations = [v for v in violations if v.rule != "SYNTAX_ERROR"]
        if critical_violations:
            elapsed = (time.perf_counter() - start_time) * 1000
            issues = "; ".join([f"[{v.rule} L{v.line_number}]: {v.description}" for v in critical_violations])
            return SandboxResult(
                success=False,
                exit_code=126,
                stdout="",
                stderr=f"❌ BLOQUEADO PELO SANDBOX SECURITY GUARDIAN: {issues}",
                execution_time_ms=elapsed,
                security_violations=violations
            )

        # 2. Cria arquivo temporário isolado no diretório de sandbox
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", dir=self.base_work_dir, delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file.write(code)
            temp_path = Path(temp_file.name)

        # 3. Execução em subprocesso isolado
        env = os.environ.copy()
        if custom_env:
            env.update(custom_env)
        # Garante UTF-8 no Python filho
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            proc = subprocess.run(
                [sys.executable, str(temp_path.name)],
                cwd=str(self.base_work_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                encoding="utf-8",
                errors="replace"
            )
            elapsed = (time.perf_counter() - start_time) * 1000
            return SandboxResult(
                success=(proc.returncode == 0),
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                execution_time_ms=elapsed,
                security_violations=violations
            )
        except subprocess.TimeoutExpired:
            elapsed = (time.perf_counter() - start_time) * 1000
            return SandboxResult(
                success=False,
                exit_code=124,
                stdout="",
                stderr=f"⏱️ TIMEOUT: Execução excedeu o limite máximo de {timeout} segundos.",
                execution_time_ms=elapsed,
                timed_out=True
            )
        finally:
            # Limpeza cirúrgica do arquivo temporário
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except Exception:
                pass
