"""Colisseum regression tests for LLM provider and budget guardrails."""
import pytest
from core.llm.router import KonigLLMRouter
from core.memory.cost_manager import KonigCostManager


def test_no_credentials_must_fail_closed(monkeypatch):
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "DEEPSEEK_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    router = KonigLLMRouter()
    with pytest.raises(RuntimeError, match="KONIG_PROVIDER_UNAVAILABLE"):
        router.generate("test", fallback_models=[], max_retries_per_model=1)


def test_provider_failure_must_not_return_fake_success(monkeypatch):
    router = KonigLLMRouter()
    def failed(*args, **kwargs):
        raise ConnectionError("provider disconnected")
    monkeypatch.setattr(router, "_call_provider", failed)
    with pytest.raises(RuntimeError, match="KONIG_PROVIDER_UNAVAILABLE"):
        router.generate("test", fallback_models=[], max_retries_per_model=1)


def test_explicit_simulation_is_labeled(monkeypatch):
    router = KonigLLMRouter()
    def failed(*args, **kwargs):
        raise ConnectionError("offline")
    monkeypatch.setattr(router, "_call_provider", failed)
    output = router.generate("test", fallback_models=[], max_retries_per_model=1, allow_simulation=True)
    assert output.simulated is True
    assert "Simulated" in output.model_used


def test_exhausted_budget_must_not_call_provider(monkeypatch):
    budget = KonigCostManager(max_workflow_budget_usd=0.0)
    router = KonigLLMRouter(cost_manager=budget)
    def forbidden(*args, **kwargs):
        raise AssertionError("provider should never be called")
    monkeypatch.setattr(router, "_call_provider", forbidden)
    with pytest.raises(RuntimeError, match="KONIG_BUDGET_EXCEEDED"):
        router.generate("hello")


def test_preflight_blocks_estimated_over_budget(monkeypatch):
    budget = KonigCostManager(max_workflow_budget_usd=0.000001)
    router = KonigLLMRouter(cost_manager=budget)
    def forbidden(*args, **kwargs):
        raise AssertionError("provider should never be called")
    monkeypatch.setattr(router, "_call_provider", forbidden)
    with pytest.raises(RuntimeError, match="KONIG_BUDGET_PREFLIGHT"):
        router.generate("hello", fallback_models=[])
