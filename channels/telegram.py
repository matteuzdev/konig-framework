"""
Konig Telegram Bridge — Single-Bot Multi-Agent Router para Grupos e Fóruns.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox.

Permite que UM ÚNICO BOT do Telegram represente todo o Squad, roteando mensagens
por tópicos de fórum ou menções (@Alice, @Bob, @Carol, @Elena, @Dan) sem precisar
criar múltiplos bots no @BotFather.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from core.engine.agent import KonigAgent
from core.primitives.handoff import KonigHandoff
from core.primitives.gate import GateVerdict


class TelegramMessage(BaseModel):
    message_id: int
    chat_id: int
    text: str
    from_user: str
    message_thread_id: Optional[int] = None
    is_topic_message: bool = False


class KonigTelegramBridge:
    """
    Roteador inteligente de mensagens para Telegram.
    Gerencia tópicos por agente/squad e interações interativas no grupo.
    """
    def __init__(self, bot_token: Optional[str] = None, default_chat_id: Optional[int] = None):
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}" if bot_token else None
        
        # Mapeamento de Tópicos do Telegram: agent_signature/role -> thread_id
        self.topic_map: Dict[str, int] = {}
        
        # Agentes registrados no roteador do bot
        self.agents: Dict[str, KonigAgent] = {}

    def register_agent(self, agent: KonigAgent, topic_id: Optional[int] = None) -> None:
        """Registra um agente no bridge com seu respectivo tópico opcional no fórum."""
        self.agents[agent.name.lower()] = agent
        self.agents[agent.role.lower()] = agent
        if topic_id:
            self.topic_map[agent.signature] = topic_id

    def bind_forum_topic(self, agent_signature: str, thread_id: int) -> None:
        """Associa a assinatura de um agente ao ID de um tópico no fórum do supergrupo."""
        self.topic_map[agent_signature] = thread_id

    def send_message(
        self,
        text: str,
        chat_id: Optional[int] = None,
        thread_id: Optional[int] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
        parse_mode: str = "HTML"
    ) -> Dict[str, Any]:
        """
        Dispara uma mensagem para o Telegram.
        Se bot_token estiver configurado, faz chamada HTTP real; caso contrário, simula em log estruturado.
        """
        target_chat = chat_id or self.default_chat_id
        if not target_chat:
            target_chat = -100123456789  # Placeholder de demonstração

        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": parse_mode
        }
        if thread_id:
            payload["message_thread_id"] = thread_id
        if reply_markup:
            payload["reply_markup"] = reply_markup

        if self.base_url:
            try:
                req_data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.base_url}/sendMessage",
                    data=req_data,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode("utf-8"))
            except Exception as e:
                print(f"⚠️ [Telegram API Error] Falha no envio HTTP real: {e}")

        # Modo Local/Dev simulado
        topic_info = f" [Tópico #{thread_id}]" if thread_id else ""
        print(f"✈️ [Telegram Dispatch -> Chat {target_chat}{topic_info}]:\n{text}\n")
        if reply_markup:
            buttons = [b["text"] for row in reply_markup.get("inline_keyboard", []) for b in row]
            print(f"   🔘 Botões Interativos: {' | '.join(buttons)}")

        return {"ok": True, "result": {"message_id": 999, "simulated": True}}

    def notify_handoff(
        self,
        handoff: KonigHandoff,
        chat_id: Optional[int] = None,
        require_human_gate: bool = False
    ) -> Dict[str, Any]:
        """
        Publica um Handoff visual estruturado no grupo do Telegram, com opção de aprovação interativa.
        """
        thread_id = self.topic_map.get(handoff.from_agent)

        msg_lines = [
            f"🔄 <b>KONIG HANDOFF PROTOCOL</b>",
            f"━━━━━━━━━━━━━━━━━━━━━━━",
            f"👤 <b>De:</b> <code>{handoff.from_agent}</code>",
            f"🎯 <b>Para:</b> <code>{handoff.to_agent}</code>",
            f"📌 <b>Condição:</b> <i>{handoff.condition}</i>",
            f"",
            f"📝 <b>Contexto / Resumo:</b>",
            f"{handoff.context}",
        ]

        if handoff.artifacts:
            msg_lines.append(f"\n📦 <b>Artefatos Gerados:</b> {', '.join(handoff.artifacts.keys())}")

        markup = None
        if require_human_gate:
            msg_lines.append(f"\n⚠️ <b>Aprovação Humana Requerida para liberar o próximo agente!</b>")
            markup = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Aprovar Gate", "callback_data": f"approve:{handoff.task_id}"},
                        {"text": "❌ Reprovar / Ajustar", "callback_data": f"reject:{handoff.task_id}"}
                    ]
                ]
            }

        text = "\n".join(msg_lines)
        return self.send_message(text=text, chat_id=chat_id, thread_id=thread_id, reply_markup=markup)

    def route_incoming_group_message(self, message: TelegramMessage) -> Optional[str]:
        """
        Recebe uma mensagem de um grupo ou tópico e roteia para o agente correspondente.
        Identifica menções como '@Alice', '@Carol', etc., ou assume o agente do tópico.
        """
        text_lower = message.text.lower()
        matched_agent = None

        # 1. Procura menção direta no texto (@nome)
        for name, agent in self.agents.items():
            if f"@{name}" in text_lower or f"@{agent.name.lower()}" in text_lower:
                matched_agent = agent
                break

        # 2. Se estiver em um tópico de fórum específico, busca o dono do tópico
        if not matched_agent and message.message_thread_id:
            for sig, t_id in self.topic_map.items():
                if t_id == message.message_thread_id:
                    matched_agent = next((ag for ag in self.agents.values() if ag.signature == sig), None)
                    break

        if matched_agent:
            print(f"📥 [Telegram Router] Mensagem direcionada para o agente: {matched_agent.signature}")
            # Emite resposta assinada pela persona do agente
            response = (
                f"<b>{matched_agent.signature}</b>:\n"
                f"Olá @{message.from_user}! Recebi sua mensagem: <i>\"{message.text}\"</i>.\n"
                f"Estou executando conforme meu SOP ({matched_agent.role})."
            )
            self.send_message(
                text=response,
                chat_id=message.chat_id,
                thread_id=message.message_thread_id
            )
            return response

        return None
