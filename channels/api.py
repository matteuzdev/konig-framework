"""
Konig API Server — Gateway RESTful para disparo e acompanhamento de Workflows.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowTriggerRequest(BaseModel):
    squad: str = Field(default="engineering", description="Nome do squad a ser executado")
    workflow_name: str = Field(default="greenfield", description="Nome do workflow")
    task_goal: str = Field(description="Objetivo principal a ser entregue pelos agentes")
    notify_whatsapp: Optional[str] = Field(default=None, description="Número de WhatsApp para receber alertas em tempo real")


class WorkflowTriggerResponse(BaseModel):
    status: str
    workflow_id: str
    message: str


class KonigAPIRouter:
    """
    Controlador de rotas para integração externa do KONIG Framework.
    """
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator

    def trigger_workflow(self, req: WorkflowTriggerRequest) -> WorkflowTriggerResponse:
        import uuid
        wf_id = str(uuid.uuid4())[:8]
        print(f"🌐 [API] Disparo de workflow recebido: Squad={req.squad} | Goal={req.task_goal}")
        
        return WorkflowTriggerResponse(
            status="started",
            workflow_id=wf_id,
            message=f"Workflow '{req.workflow_name}' no squad '{req.squad}' iniciado com sucesso."
        )

    def get_health(self) -> Dict[str, Any]:
        return {
            "status": "online",
            "framework": "KONIG Autonomous Multi-Agent Framework",
            "version": "2.0.0",
            "features": ["DAG Workflows", "Quality Gates", "KONIG Handoffs", "Omnichannel", "Meta-Orchestrator"]
        }
