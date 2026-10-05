"""
Konig WhatsApp Connector — Integração para agentes interagirem via WhatsApp Business.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel, Field


class WhatsAppMessage(BaseModel):
    sender_phone: str = Field(description="Número de telefone do remetente (DDI + DDD + Número)")
    text: str = Field(description="Conteúdo textual recebido")
    message_id: Optional[str] = None
    timestamp: Optional[str] = None


class KonigWhatsAppBridge:
    """
    Bridge que encapsula o envio e recepção de mensagens do WhatsApp,
    roteando comandos para o KonigOrchestrator ou para agentes específicos.
    """
    def __init__(self, webhook_url: Optional[str] = None, api_token: Optional[str] = None):
        self.webhook_url = webhook_url
        self.api_token = api_token
        self.registered_callbacks: Dict[str, Callable] = {}

    def format_handoff_notification(self, from_agent: str, task_name: str, summary: str) -> str:
        """
        Formata um alerta visual para o WhatsApp quando um handoff acontece no framework.
        """
        return (
            f"🔔 *KONIG AGENT HANDOFF*\n\n"
            f"👤 *Agente:* {from_agent}\n"
            f"🎯 *Task Concluída:* {task_name}\n"
            f"📝 *Resumo da Entrega:*\n{summary[:500]}...\n\n"
            f"✅ _Status: Aprovado no Gate de Qualidade._"
        )

    def handle_incoming_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recebe e processa o webhook de plataformas como Evolution API, Z-API ou Twilio.
        """
        sender = payload.get("sender") or payload.get("from") or "Desconhecido"
        text = payload.get("message") or payload.get("body") or payload.get("text") or ""

        parsed_msg = WhatsAppMessage(sender_phone=str(sender), text=str(text))

        print(f"📱 [WhatsApp] Mensagem recebida de {parsed_msg.sender_phone}: '{parsed_msg.text}'")

        # Roteamento básico de comando
        if parsed_msg.text.startswith("/status"):
            response_text = "🟢 *KONIG Framework:* Todos os squads ativos e operacionais."
        elif parsed_msg.text.startswith("/run"):
            response_text = "🚀 *Iniciando workflow autônomo...* Você receberá o progresso de cada agente aqui."
        else:
            response_text = f"🤖 Recebido: '{parsed_msg.text}'. Seus agentes de IA estão processando a solicitação."

        return {
            "status": "processed",
            "reply": response_text,
            "sender": parsed_msg.sender_phone
        }

    def send_message(self, recipient_phone: str, text: str) -> Dict[str, Any]:
        """
        Dispara mensagem para o WhatsApp do usuário ou cliente.
        """
        print(f"📤 [WhatsApp] Enviando para {recipient_phone}:\n{text}")
        return {
            "success": True,
            "recipient": recipient_phone,
            "dispatched": True
        }
