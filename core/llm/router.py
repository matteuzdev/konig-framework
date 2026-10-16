"""
Konig LLM Router — Roteador resiliente com Fallback Chain e Auto-Recovery.

Arquitetura Industrial KONIG — Enterprise Agentic Framework.
Governado por SOPs determinísticos, Quality Gates e isolamento em Sandbox."""

from __future__ import annotations

import os
import time
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from core.engine.synapse import KonigSynapseEngine
from core.memory.cost_manager import KonigCostManager


class LLMResponse(BaseModel):
    content: str
    model_used: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    fallback_occurred: bool = False
    simulated: bool = False
    execution_time_ms: float = 0.0


class KonigLLMRouter:
    """
    Roteador de inferência inteligente com tolerância a falhas (fallback chain)
    e auditoria financeira automática.
    """
    def __init__(
        self,
        cost_manager: Optional[KonigCostManager] = None,
        synapse_engine: Optional[KonigSynapseEngine] = None
    ):
        self.cost_manager = cost_manager or KonigCostManager()
        self.synapse_engine = synapse_engine or KonigSynapseEngine()

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "gpt-4o",
        fallback_models: Optional[List[str]] = None,
        agent_signature: str = "[System - Engine]",
        temperature: float = 0.7,
        max_retries_per_model: int = 2,
        allow_simulation: bool = False
    ) -> LLMResponse:
        """
        Executa a geração através de uma cadeia de modelos com resiliência total.
        """
        if self.cost_manager.is_budget_exceeded():
            raise RuntimeError("KONIG_BUDGET_EXCEEDED")
        model_chain = [model] + (fallback_models if fallback_models is not None else ["gpt-4o-mini", "gemini-2.5-flash"])
        start_time = time.perf_counter()

        last_error = None
        for idx, current_model in enumerate(model_chain):
            is_fallback = (idx > 0)
            if is_fallback:
                print(f"🔄 [LLM Router] Acionando modelo de fallback: {current_model} (Origem: {model})")

            for attempt in range(max_retries_per_model):
                if self.cost_manager.is_budget_exceeded():
                    raise RuntimeError('KONIG_BUDGET_EXCEEDED')
                predicted = self.cost_manager.calculate_cost(current_model, self.synapse_engine.estimate_tokens(prompt + system_prompt), 4096)
                if predicted > self.cost_manager.get_remaining_budget():
                    raise RuntimeError('KONIG_BUDGET_PREFLIGHT: conservative estimate exceeds remaining budget')
                try:
                    # Se houver chaves de API configuradas no ambiente, podemos chamar via LiteLLM ou SDK:
                    content, in_tokens, out_tokens = self._call_provider(
                        current_model, prompt, system_prompt, temperature
                    )

                    elapsed = (time.perf_counter() - start_time) * 1000
                    
                    # Registra no CostManager
                    record = self.cost_manager.record_usage(
                        agent_signature=agent_signature,
                        model=current_model,
                        prompt_tokens=in_tokens,
                        completion_tokens=out_tokens
                    )

                    return LLMResponse(
                        content=content,
                        model_used=current_model,
                        prompt_tokens=in_tokens,
                        completion_tokens=out_tokens,
                        cost_usd=record.cost_usd,
                        fallback_occurred=is_fallback,
                        execution_time_ms=elapsed
                    )

                except Exception as e:
                    last_error = e
                    print(f"⚠️ [LLM Router] Erro em {current_model} (Tentativa {attempt+1}/{max_retries_per_model}): {e}")
                    time.sleep(0.5 * (2 ** attempt))  # Exponential backoff

        if not allow_simulation:
            raise RuntimeError(f'KONIG_PROVIDER_UNAVAILABLE: {last_error}')

        # Explicit opt-in simulation only, not a live completion.
        # Se todos os modelos reais falharem ou não houver API key configurada,
        # geramos fallback gracioso mantendo a integridade do pipeline:
        elapsed = (time.perf_counter() - start_time) * 1000
        fallback_text = f"Simulated output for model {model} based on prompt: {prompt[:100]}..."
        in_t = self.synapse_engine.estimate_tokens(prompt + system_prompt)
        out_t = self.synapse_engine.estimate_tokens(fallback_text)

        rec = self.cost_manager.record_usage(agent_signature, model, in_t, out_t)
        return LLMResponse(
            content=fallback_text,
            model_used=f"{model} (Simulated Fallback)",
            prompt_tokens=in_t,
            completion_tokens=out_t,
            cost_usd=rec.cost_usd,
            fallback_occurred=True,
            simulated=True,
            execution_time_ms=elapsed
        )

    def _call_provider(
        self, model: str, prompt: str, system_prompt: str, temperature: float
    ) -> tuple[str, int, int]:
        """
        Executa chamada real para o provedor se LiteLLM ou API Keys estiverem disponíveis.
        """
        # Verifica se temos chaves reais no ambiente
        has_api_key = any(
            k in os.environ
            for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "DEEPSEEK_API_KEY")
        )

        if has_api_key:
            try:
                import litellm
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = litellm.completion(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                content = response.choices[0].message.content or ""
                in_tokens = response.usage.prompt_tokens
                out_tokens = response.usage.completion_tokens
                return content, in_tokens, out_tokens
            except ImportError as exc:
                raise RuntimeError('LiteLLM required for real inference') from exc
            except Exception as e:
                raise e

        raise RuntimeError(f'No configured credentials for live model: {model}')
