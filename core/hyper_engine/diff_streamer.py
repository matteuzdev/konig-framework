"""
KONIG Hyper-Engine — Inline Diff Streamer & Atomic Patch Engine
Gera diffs unificados precisos, formata preview colorido de linhas verdes/vermelhas,
e aplica patches atômicos em disco com suporte a rollback (.undo) instantâneo.
"""

from __future__ import annotations

import difflib
import os
import re
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class DiffHunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    header: str
    lines: List[str] = field(default_factory=list)


@dataclass
class DiffResult:
    file_path: str
    original_content: str
    modified_content: str
    unified_diff: str
    hunks: List[DiffHunk] = field(default_factory=list)
    lines_added: int = 0
    lines_removed: int = 0
    lines_unchanged: int = 0
    is_empty: bool = True


class DiffStreamer:
    """
    Motor de cálculo e aplicação cirúrgica de diffs.
    Garante que arquivos nunca sejam corrompidos em edições parciais.
    """

    # Códigos ANSI para colorização no terminal
    COLOR_GREEN = "\033[92m"   # Adições (+)
    COLOR_RED = "\033[91m"     # Remoções (-)
    COLOR_CYAN = "\033[96m"    # Hunk header (@@ -x,y +x,y @@)
    COLOR_GRAY = "\033[90m"    # Linhas de contexto neutro
    COLOR_BOLD = "\033[1m"
    COLOR_RESET = "\033[0m"

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.undo_dir = os.path.join(self.root_dir, ".konig", "undo_backups")
        os.makedirs(self.undo_dir, exist_ok=True)

    def _sanitize_path_for_backup(self, rel_path: str) -> str:
        return rel_path.replace("\\", "_").replace("/", "_")

    def compute_diff(self, original: str, modified: str, file_path: str = "") -> DiffResult:
        """
        Calcula o diff unificado entre o conteúdo original e o modificado.
        """
        orig_lines = original.splitlines(keepends=True)
        mod_lines = modified.splitlines(keepends=True)

        diff_gen = difflib.unified_diff(
            orig_lines,
            mod_lines,
            fromfile=f"a/{file_path or 'original'}",
            tofile=f"b/{file_path or 'modified'}",
            n=3,
        )

        diff_lines = list(diff_gen)
        unified_diff_str = "".join(diff_lines)

        if not diff_lines:
            return DiffResult(
                file_path=file_path,
                original_content=original,
                modified_content=modified,
                unified_diff="",
                is_empty=True,
            )

        hunks: List[DiffHunk] = []
        current_hunk: Optional[DiffHunk] = None
        lines_added = 0
        lines_removed = 0
        lines_unchanged = 0

        hunk_header_re = re.compile(r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@")

        for line in diff_lines:
            if line.startswith("---") or line.startswith("+++"):
                continue

            match = hunk_header_re.match(line)
            if match:
                old_start = int(match.group(1))
                old_count = int(match.group(2) or 1)
                new_start = int(match.group(3))
                new_count = int(match.group(4) or 1)

                current_hunk = DiffHunk(
                    old_start=old_start,
                    old_count=old_count,
                    new_start=new_start,
                    new_count=new_count,
                    header=line.strip(),
                )
                hunks.append(current_hunk)
                continue

            if current_hunk is not None:
                current_hunk.lines.append(line)

            if line.startswith("+"):
                lines_added += 1
            elif line.startswith("-"):
                lines_removed += 1
            else:
                lines_unchanged += 1

        return DiffResult(
            file_path=file_path,
            original_content=original,
            modified_content=modified,
            unified_diff=unified_diff_str,
            hunks=hunks,
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_unchanged=lines_unchanged,
            is_empty=False,
        )

    def format_terminal_diff(self, diff_res: DiffResult, colored: bool = True) -> str:
        """
        Formata o diff em visual verde/vermelho/ciano com sumário numérico.
        """
        if diff_res.is_empty:
            return f"[DIFF] Zero alterações detectadas em '{diff_res.file_path}'."

        out: List[str] = []
        banner = (
            f"=== DIFF CIRÚRGICO: {diff_res.file_path} "
            f"(+{diff_res.lines_added} / -{diff_res.lines_removed}) ==="
        )
        out.append(self.COLOR_BOLD + banner + self.COLOR_RESET if colored else banner)

        for hunk in diff_res.hunks:
            out.append(
                f"\n{self.COLOR_CYAN}{hunk.header}{self.COLOR_RESET}"
                if colored
                else f"\n{hunk.header}"
            )
            for l in hunk.lines:
                r_line = l.rstrip("\r\n")
                if l.startswith("+"):
                    out.append(f"{self.COLOR_GREEN}{r_line}{self.COLOR_RESET}" if colored else r_line)
                elif l.startswith("-"):
                    out.append(f"{self.COLOR_RED}{r_line}{self.COLOR_RESET}" if colored else r_line)
                else:
                    out.append(f"{self.COLOR_GRAY} {r_line.lstrip()}{self.COLOR_RESET}" if colored else r_line)

        return "\n".join(out)

    def apply_diff_atomically(
        self, file_path: str, new_content: str, make_backup: bool = True
    ) -> bool:
        """
        Grava o novo conteúdo em arquivo temporário e faz substituição atômica via os.replace.
        Cria backup .undo para permitir rollback imediato.
        """
        full_path = os.path.join(self.root_dir, file_path)
        if not os.path.exists(full_path):
            # Cria diretórios pais caso arquivo seja novo
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True

        # Cria backup .undo antes de modificar
        if make_backup:
            rel_name = os.path.relpath(full_path, self.root_dir)
            safe_name = self._sanitize_path_for_backup(rel_name)
            backup_path = os.path.join(self.undo_dir, f"{safe_name}.undo")
            shutil.copy2(full_path, backup_path)
            # Também cria <arquivo>.undo no mesmo diretório para acesso fácil
            shutil.copy2(full_path, f"{full_path}.undo")

        # Escrita atômica em arquivo temporário
        tmp_path = f"{full_path}.tmp_{int(time.time() * 1000)}"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            os.replace(tmp_path, full_path)
            return True
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise e

    def rollback(self, file_path: str) -> bool:
        """
        Restaura o arquivo a partir do backup .undo mais recente.
        """
        full_path = os.path.join(self.root_dir, file_path)
        rel_name = os.path.relpath(full_path, self.root_dir)
        safe_name = self._sanitize_path_for_backup(rel_name)
        backup_in_undo_dir = os.path.join(self.undo_dir, f"{safe_name}.undo")
        local_undo = f"{full_path}.undo"

        source_backup = None
        if os.path.exists(local_undo):
            source_backup = local_undo
        elif os.path.exists(backup_in_undo_dir):
            source_backup = backup_in_undo_dir

        if not source_backup:
            return False

        shutil.copy2(source_backup, full_path)
        return True
