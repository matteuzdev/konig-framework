"""
KonigMetaOrchestrator — O arquiteto supremo que gera novos Squads, SOPs e Workflows.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from core.engine.agent import KonigAgent
from core.primitives.task import KonigTask, TaskPriority
from core.primitives.workflow import KonigWorkflow


class KonigMetaOrchestrator:
    """
    Agente/Motor capaz de desenhar, instanciar e configurar squads autônomos
    para qualquer frente: Tecnologia, Estratégia, Marketing, Vendas ou Operações.
    """
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path(__file__).resolve().parent.parent.parent

    def generate_squad_blueprint(self, squad_type: str, domain_goal: str) -> Dict[str, Any]:
        """
        Gera a estrutura completa de um Squad especializado.
        """
        squad_type = squad_type.lower()

        if "market" in squad_type or "growth" in squad_type:
            return {
                "name": f"squad_marketing_{domain_goal.replace(' ', '_').lower()[:15]}",
                "domain": "Growth & Marketing",
                "agents": {
                    "cmo": {
                        "name": "Marcus",
                        "role": "Chief Marketing Officer (CMO)",
                        "goal": "Maximizar ROAS, construir posicionamento de marca premium e coordenar funis de aquisição.",
                        "backstory": "Estrategista sênior de marketing digital, com foco em AARRR e autoridade inquestionável.",
                        "skills": ["analytics", "campaign_strategy", "brand_positioning"],
                    },
                    "copywriter": {
                        "name": "Helena",
                        "role": "Direct Response Copywriter",
                        "goal": "Redigir copies de alta conversão, headlines magnéticas e VSLs persuasivas.",
                        "backstory": "Especialista em gatilhos mentais, storytelling e psicologia de vendas.",
                        "skills": ["copywriting", "sales_pages", "email_marketing"],
                    },
                    "growth_hacker": {
                        "name": "Leo",
                        "role": "Performance & Traffic Specialist",
                        "goal": "Desenhar campanhas pagas (Google/Meta), otimização de conversão (CRO) e métricas.",
                        "backstory": "Especialista em tráfego pago, testes A/B e escala previsível de aquisição.",
                        "skills": ["paid_traffic", "cro_optimization", "ab_testing"],
                    }
                }
            }
        elif "sale" in squad_type or "venda" in squad_type:
            return {
                "name": f"squad_sales_{domain_goal.replace(' ', '_').lower()[:15]}",
                "domain": "Sales & Revenue",
                "agents": {
                    "sdr": {
                        "name": "Lucas",
                        "role": "Sales Development Representative (SDR)",
                        "goal": "Qualificar leads, conduzir abordagens ativas e agendar reuniões com decisores.",
                        "backstory": "Mestre em abordagem consultiva, cold outreach e nutrição de pipeline.",
                        "skills": ["lead_qualification", "cold_outreach", "crm_management"],
                    },
                    "closer": {
                        "name": "Sophia",
                        "role": "Enterprise Account Executive (Closer)",
                        "goal": "Fechar contratos de alto valor, quebrar objeções e negociar termos comerciais.",
                        "backstory": "Negociadora de fechamento com taxa de conversão superior a 35% em tickets altos.",
                        "skills": ["objection_handling", "contract_negotiation", "deal_closing"],
                    },
                    "cs_manager": {
                        "name": "Bernardo",
                        "role": "Customer Success & Retention Lead",
                        "goal": "Garantir onboarding sem atrito, retenção de clientes e expansão de receita (upsell).",
                        "backstory": "Focado em LTV, NPS e satisfação absoluta do cliente desde o dia zero.",
                        "skills": ["customer_onboarding", "retention_strategy", "upselling"],
                    }
                }
            }
        elif "strat" in squad_type or "negoc" in squad_type or "ceo" in squad_type:
            return {
                "name": f"squad_strategy_{domain_goal.replace(' ', '_').lower()[:15]}",
                "domain": "Executive Strategy",
                "agents": {
                    "ceo_advisor": {
                        "name": "Arthur",
                        "role": "Executive Strategy Advisor",
                        "goal": "Definir visão corporativa, modelo de monetização e vantagens competitivas sustentáveis.",
                        "backstory": "Ex-consultor de topo de mercado focado em governança e escala empresarial.",
                        "skills": ["business_modeling", "competitive_analysis", "m_and_a"],
                    },
                    "financial_controller": {
                        "name": "Beatriz",
                        "role": "Head of Finance & Unit Economics",
                        "goal": "Garantir margens operacionais saudáveis, runway e controle rígido de CAC vs LTV.",
                        "backstory": "Controladora financeira focada em eficiência de capital e rentabilidade máxima.",
                        "skills": ["unit_economics", "cashflow_planning", "pricing_models"],
                    }
                }
            }
        else: # Default: Engenharia & Produto
            return {
                "name": f"squad_engineering_{domain_goal.replace(' ', '_').lower()[:15]}",
                "domain": "Product & Engineering",
                "agents": {
                    "pm": {
                        "name": "Alice",
                        "role": "Lead Product Manager & Brand Topology Architect",
                        "goal": "Definir requisitos claros, DNA de marca, arquétipo comercial e PRD detalhado.",
                        "skills": ["brand_topology", "prd_writing", "scope_definition"],
                    },
                    "architect": {
                        "name": "Bob",
                        "role": "System Architect",
                        "goal": "Desenhar arquitetura distribuída, segura e com baixo acoplamento.",
                        "skills": ["system_design", "api_design"],
                    },
                    "designer": {
                        "name": "Carol",
                        "role": "Lead UI/UX Adaptive Designer",
                        "goal": "Criar sistemas visuais camaleônicos subordinados ao branding do cliente e sem dogmatismo de nicho único.",
                        "skills": ["brand_adaptation", "design_systems", "semantic_tokens", "wcag_accessibility"],
                    },
                    "engineer": {
                        "name": "Dan",
                        "role": "Senior Fullstack Software Engineer",
                        "goal": "Implementar código limpo, testável, de alta performance e com autonomia de contestação técnica (Challenge Loop).",
                        "skills": ["python", "typescript", "fastapi", "clean_code", "spec_challenge"],
                    },
                    "qa": {
                        "name": "Elena",
                        "role": "Staff QA & Homologation Engineer",
                        "goal": "Blindar o sistema contra falhas, testar edge cases e validar conformidade contratual com o PRD.",
                        "skills": ["e2e_testing", "pytest", "security_audit", "contract_challenge"],
                    }
                }
            }

    def scaffold_squad_files(self, squad_type: str, domain_goal: str) -> Path:
        """
        Cria a pasta e o squad.yaml no diretório de squads do workspace.
        """
        blueprint = self.generate_squad_blueprint(squad_type, domain_goal)
        folder_name = squad_type.lower()
        target_dir = self.workspace_root / "squads" / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        squad_yaml_path = target_dir / "squad.yaml"
        with open(squad_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(blueprint, f, allow_unicode=True, sort_keys=False)

        print(f"📦 Squad [{blueprint['name']}] scaffolded em: {squad_yaml_path}")
        return squad_yaml_path

    def build_custom_workflow(self, name: str, squad_blueprint: Dict[str, Any], goal_instruction: str) -> KonigWorkflow:
        """
        Constrói automaticamente um KonigWorkflow encadeando as tasks dos agentes do squad.
        """
        wf = KonigWorkflow(name=name, description=f"Workflow autônomo gerado para: {goal_instruction}")
        agents = squad_blueprint.get("agents", {})
        
        last_task_id = None
        for key, agent_info in agents.items():
            task_id = f"task_{key}_{name}"
            req_gates = []
            
            role_l = agent_info["role"].lower()
            if "pm" in role_l or "product" in role_l:
                req_gates.append("prd_gate")
            elif "architect" in role_l:
                req_gates.append("architecture_gate")
            elif "ui" in role_l or "ux" in role_l or "designer" in role_l:
                req_gates.append("ui_ux_gate")
            elif "qa" in role_l or "test" in role_l:
                req_gates.append("qa_gate")
            elif "engineer" in role_l or "dev" in role_l:
                req_gates.append("code_quality_gate")

            task = KonigTask(
                id=task_id,
                name=f"Execução de {agent_info['role']}",
                description=f"Atuar na sua especialidade para entregar: {goal_instruction}",
                expected_output=f"Entrega aprovada de {agent_info['role']} para o objetivo do projeto.",
                assigned_agent=f"[{agent_info['name']} - {agent_info['role']}]",
                depends_on=[last_task_id] if last_task_id else [],
                required_gates=req_gates,
                priority=TaskPriority.HIGH
            )
            wf.add_task(task)
            last_task_id = task_id

        return wf


# ==============================================================================
# ALIASES OFICIAIS: ONIX MASTER ORCHESTRATOR
# ==============================================================================
OnixMetaOrchestrator = KonigMetaOrchestrator
OnixOrchestrator = KonigMetaOrchestrator
