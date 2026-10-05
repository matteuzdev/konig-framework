"""
Konig SquadLoader — Carregador de Squads padrão KONIG.

Faz o parsing de estruturas ricas de squads contendo:
- agents/*.md (com frontmatter YAML + instruções + comandos + handoff matrix)
- tasks/*.md (especificações procedurais de tasks executáveis)
- checklists/*.md (critérios formais de Quality Gates)
- templates/*.md (documentos base com placeholders e diretivas)
- workflows/*.yaml (DAG de execução amarrando tasks e gates)
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from core.engine.agent import KonigAgent
from core.primitives.gate import KonigGate, GateResult, GateVerdict
from core.primitives.task import KonigTask, TaskPriority, TaskStatus
from core.primitives.workflow import KonigWorkflow


import unicodedata

def normalize_text(text: str) -> str:
    """Remove acentos e pontuação para comparação robusta de termos."""
    text = text.replace("-", " ").replace("_", " ")
    nfkd = unicodedata.normalize("NFKD", text)
    clean = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return clean.lower()


class MarkdownGate(KonigGate):
    """Quality Gate que executa validação baseada em um arquivo de checklist markdown."""
    checklist_path: Path
    raw_checklist: str = ""

    def validate(self, agent_output: str, context: Dict[str, Any] = None) -> GateResult:
        stopwords = {"para", "com", "como", "pelo", "pela", "onde", "quando", "entre", "cada", "mais", "menos", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "por", "que", "se", "ou", "ao", "aos", "um", "uma"}
        missing = []
        normalized_output = normalize_text(agent_output)

        for item in self.checklist:
            norm_item = normalize_text(item)
            words = [re.sub(r"[^\w]", "", w) for w in norm_item.split()]
            keywords = [w for w in words if len(w) >= 4 and w not in stopwords]
            
            # Se pelo menos 35% das palavras conceituais estiverem presentes, considera atendido
            if keywords:
                matched = sum(1 for kw in keywords if kw in normalized_output)
                match_ratio = matched / len(keywords)
                if match_ratio < 0.35:
                    missing.append(item)
            else:
                if norm_item not in normalized_output:
                    missing.append(item)

        score = 1.0 - (len(missing) / max(len(self.checklist), 1))
        issues = [f"Item do checklist não atendido: {item}" for item in missing]

        verdict = GateVerdict.APPROVED if score >= self.min_score else GateVerdict.REJECTED
        feedback = (
            f"Gate [{self.name}] aprovado com base no checklist oficial."
            if verdict == GateVerdict.APPROVED
            else f"Gate [{self.name}] reprovado. Pendências: {', '.join(issues)}"
        )

        return GateResult(
            gate_id=self.id,
            gate_name=self.name,
            verdict=verdict,
            score=max(0.0, min(1.0, score)),
            feedback=feedback,
            issues=issues,
        )




class KonigLoadedSquad:
    """Representa um Squad completamente carregado do disco com todos os seus artefatos."""
    def __init__(self, squad_dir: Path):
        self.squad_dir = squad_dir
        self.manifest: Dict[str, Any] = {}
        self.agents: Dict[str, KonigAgent] = {}
        self.agent_docs: Dict[str, str] = {}
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.checklists: Dict[str, Dict[str, Any]] = {}
        self.templates: Dict[str, str] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}

    @property
    def name(self) -> str:
        return self.manifest.get("name") or self.squad_dir.name


class SquadLoader:
    """
    Carrega squads do sistema de arquivos seguindo o padrão KONIG e KONIG.
    """
    @staticmethod
    def parse_markdown_with_yaml_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
        """
        Extrai o bloco YAML delimitado por ```yaml ... ``` ou --- ... --- e o corpo do markdown.
        """
        frontmatter = {}
        body = content

        # Tenta bloco ```yaml ... ```
        yaml_match = re.search(r"```yaml\s*\n(.*?)\n```", content, re.DOTALL)
        if yaml_match:
            try:
                frontmatter = yaml.safe_load(yaml_match.group(1)) or {}
            except Exception as e:
                print(f"⚠️ Erro ao parsear YAML frontmatter: {e}")

        # Tenta formato standard Jekyll/KONIG frontmatter (--- ... ---)
        elif content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2].strip()
                except Exception as e:
                    print(f"⚠️ Erro ao parsear frontmatter '---': {e}")

        return frontmatter, body

    @classmethod
    def load_squad(cls, squad_path: str | Path) -> KonigLoadedSquad:
        path = Path(squad_path)
        if not path.exists():
            raise FileNotFoundError(f"Diretório do squad não encontrado: {path}")

        loaded = KonigLoadedSquad(path)

        # 1. Carrega manifesto squad.yaml se existir
        manifest_file = path / "squad.yaml"
        if manifest_file.exists():
            with open(manifest_file, "r", encoding="utf-8") as f:
                loaded.manifest = yaml.safe_load(f) or {}

        # 2. Carrega Agentes (agents/*.md)
        agents_dir = path / "agents"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.md"):
                content = agent_file.read_text(encoding="utf-8")
                frontmatter, body = cls.parse_markdown_with_yaml_frontmatter(content)
                agent_def = frontmatter.get("agent", {})
                persona_def = frontmatter.get("persona", {})

                name = agent_def.get("name") or agent_file.stem.capitalize()
                role = agent_def.get("title") or persona_def.get("role") or agent_file.stem
                goal = agent_def.get("whenToUse") or persona_def.get("focus") or "Executar atribuições especializadas."
                skills = frontmatter.get("commands", [])
                skill_names = [cmd.get("name") for cmd in skills if isinstance(cmd, dict)]

                agent = KonigAgent(
                    name=name,
                    role=role,
                    goal=goal.strip(),
                    backstory=body.strip(),
                    skills=skill_names
                )
                loaded.agents[agent_file.stem] = agent
                loaded.agent_docs[agent_file.stem] = content

        # 3. Carrega Tasks (tasks/*.md)
        tasks_dir = path / "tasks"
        if tasks_dir.exists():
            for task_file in tasks_dir.glob("*.md"):
                content = task_file.read_text(encoding="utf-8")
                frontmatter, body = cls.parse_markdown_with_yaml_frontmatter(content)
                loaded.tasks[task_file.stem] = {
                    "id": task_file.stem,
                    "metadata": frontmatter,
                    "instructions": body,
                    "path": task_file
                }

        # 4. Carrega Checklists / Quality Gates (checklists/*.md)
        checklists_dir = path / "checklists"
        if checklists_dir.exists():
            for chk_file in checklists_dir.glob("*.md"):
                content = chk_file.read_text(encoding="utf-8")
                # Extrai itens marcados com [ ] ou - do checklist
                items = re.findall(r"-\s*\[\s*\]\s*(.+)", content)
                if not items:
                    items = re.findall(r"-\s*(.+)", content)
                loaded.checklists[chk_file.stem] = {
                    "id": chk_file.stem,
                    "items": [item.strip() for item in items if item.strip()],
                    "raw_content": content,
                    "path": chk_file
                }

        # 5. Carrega Templates (templates/*.md ou *.yaml)
        templates_dir = path / "templates"
        if templates_dir.exists():
            for tmpl_file in templates_dir.glob("*.*"):
                loaded.templates[tmpl_file.name] = tmpl_file.read_text(encoding="utf-8")

        # 6. Carrega Workflows (workflows/*.yaml)
        workflows_dir = path / "workflows"
        if workflows_dir.exists():
            for wf_file in workflows_dir.glob("*.yaml"):
                with open(wf_file, "r", encoding="utf-8") as f:
                    loaded.workflows[wf_file.stem] = yaml.safe_load(f) or {}

        print(
            f"🏛️ Squad [{path.name}] Carregado: "
            f"{len(loaded.agents)} Agentes (.md) | "
            f"{len(loaded.tasks)} Tasks (.md) | "
            f"{len(loaded.checklists)} Checklists (.md) | "
            f"{len(loaded.templates)} Templates | "
            f"{len(loaded.workflows)} Workflows"
        )
        return loaded
