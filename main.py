"""
KONIG Framework — Execução Principal e Demonstração do Ecossistema Refundado.
Demonstra:
1. Execução de Workflow DAG com ordenação topológica e paralelismo por waves.
2. Gates de Qualidade rígidos (PRD, Architecture, UI/UX Pro-Max, Code Quality, QA Engineer).
3. Handoffs com assinatura visual no padrão KONIG.
4. Meta-Orquestrador gerando squads dinâmicos de Marketing/Vendas.
5. Integração Omnichannel (WhatsApp notification bridge).
"""

import sys
from pathlib import Path

# Garante compatibilidade de UTF-8 no Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from core.engine.orchestrator import KonigOrchestrator
from core.engine.meta_orchestrator import KonigMetaOrchestrator
from core.primitives.task import KonigTask, TaskPriority
from core.primitives.workflow import KonigWorkflow
from channels.whatsapp import KonigWhatsAppBridge
from channels.telegram import KonigTelegramBridge, TelegramMessage



def main():
    print("=================================================================")
    print("🦁 KONIG AGENTIC FRAMEWORK — ENTERPRISE ENGINE 2.0")
    print("=================================================================\n")

    # 1. Carrega o Time de Desenvolvimento de IA a partir de '.agents' (Padrão KONIG / Universal AI)
    orchestrator = KonigOrchestrator(".agents")

    print(f"✅ Agentes carregados no Time de Engenharia (.agents): {len(orchestrator.agents)}")
    for signature, ag in orchestrator.environment.agents.items():
        print(f"   • {ag.signature} — Skills: {ag.skills}")


    # 2. Compila o Workflow DAG diretamente a partir dos arquivos reais do Squad (padrão KONIG)
    # Lê workflows/greenfield-delivery.yaml, tasks/*.md, checklists/*.md e templates/*.md
    print("📋 Compilando Workflow declarativo a partir de 'workflows/greenfield-delivery.yaml'...")
    workflow = orchestrator.build_workflow_from_squad("greenfield-delivery")
    print(f"   • Workflow: {workflow.name} | Tasks compiladas: {len(workflow.tasks)}")

    # 3. Executa o Workflow no Orchestrator com validação de Gates em markdown
    summary = orchestrator.run_workflow(workflow)

    print("\n📊 RESUMO DA EXECUÇÃO DO WORKFLOW:")
    for k, v in summary.items():
        print(f"   • {k}: {v}")

    # 4. Demonstração de Carregamento de Outros Squads Modulares (Marketing & Sales)
    print("\n" + "="*65)
    print("🏛️ DEMONSTRAÇÃO: CARREGANDO SQUADS MODULARES DE NEGÓCIO")
    print("=================================================================")
    from core.engine.squad_loader import SquadLoader
    mkt_squad = SquadLoader.load_squad("squads/marketing")
    print(f"✨ Squad Marketing pronto: {len(mkt_squad.agents)} Agentes | {len(mkt_squad.tasks)} Tasks | {len(mkt_squad.checklists)} Checklists")

    sales_squad = SquadLoader.load_squad("squads/sales")
    print(f"✨ Squad Sales pronto: {len(sales_squad.agents)} Agentes | {len(sales_squad.tasks)} Tasks | {len(sales_squad.checklists)} Checklists")


    # 5. Demonstração Omnichannel — Envio de Alerta de Handoff para WhatsApp
    print("\n" + "="*65)
    print("📱 DEMONSTRAÇÃO: DISPATCH OMNICHANNEL VIA WHATSAPP BRIDGE")
    print("=================================================================")
    wa_bridge = KonigWhatsAppBridge()
    last_handoff = workflow.handoff_history[-1] if workflow.handoff_history else None
    
    if last_handoff:
        wa_text = wa_bridge.format_handoff_notification(
            from_agent=last_handoff.from_agent,
            task_name="Homologação Final de Release (QA)",
            summary="Bateria de testes concluída com 94% de cobertura. Produto pronto para deploy."
        )
        wa_bridge.send_message(recipient_phone="+5511999999999", text=wa_text)

    # 6. Demonstração Omnichannel — Telegram Single-Bot Multi-Agent Router com Fóruns & Menções
    print("\n" + "="*65)
    print("✈️ DEMONSTRAÇÃO: TELEGRAM SINGLE-BOT MULTI-AGENT ROUTER")
    print("=================================================================")
    tg_bridge = KonigTelegramBridge(default_chat_id=-100987654321)

    # Registra agentes e associa a tópicos no supergrupo
    for ag in orchestrator.environment.agents.values():
        tg_bridge.register_agent(ag)

    tg_bridge.bind_forum_topic("[Carol - Lead UI/UX Pro-Max Designer]", thread_id=102)
    tg_bridge.bind_forum_topic("[Elena - Staff QA & Test Automation Engineer]", thread_id=103)

    if last_handoff:
        print("📨 [1] Notificando Handoff no Tópico do Fórum com Botões de Aprovação:")
        tg_bridge.notify_handoff(last_handoff, require_human_gate=True)

    print("👥 [2] Simulação de Humano chamando agente por menção em grupo:")
    incoming = TelegramMessage(
        message_id=501,
        chat_id=-100987654321,
        text="@Carol você pode revisar os contrastes de cor no dark mode?",
        from_user="hianto_dev",
        message_thread_id=102
    )
    tg_bridge.route_incoming_group_message(incoming)



if __name__ == "__main__":
    main()
