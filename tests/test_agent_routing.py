"""Forja regression tests: never hand a task to an unauthorized agent."""
from types import SimpleNamespace

from core.engine.orchestrator import KonigOrchestrator


def _router():
    authorized = SimpleNamespace(
        name="Alice", role="architect", signature="[Alice - architect]",
        skills=["system_design"]
    )
    unauthorized = SimpleNamespace(
        name="Bob", role="marketing", signature="[Bob - marketing]",
        skills=["copywriting"]
    )
    return SimpleNamespace(
        environment=SimpleNamespace(agents={"architect": authorized, "marketing": unauthorized}),
        agents={"architect": authorized, "marketing": unauthorized},
    )


def test_explicit_unknown_owner_fails_closed():
    task = SimpleNamespace(assigned_agent="[Missing - engineer]", required_skills=[])
    assert KonigOrchestrator.find_agent_for_task(_router(), task) is None


def test_unavailable_required_skills_fail_closed():
    task = SimpleNamespace(assigned_agent=None, required_skills=["production_database_admin"])
    assert KonigOrchestrator.find_agent_for_task(_router(), task) is None


def test_explicit_owner_uses_only_that_agent():
    task = SimpleNamespace(assigned_agent="[Alice - architect]", required_skills=[])
    agent = KonigOrchestrator.find_agent_for_task(_router(), task)
    assert agent.signature == "[Alice - architect]"


def test_eligible_skill_routes_to_authorized_agent():
    task = SimpleNamespace(assigned_agent=None, required_skills=["system_design"])
    agent = KonigOrchestrator.find_agent_for_task(_router(), task)
    assert agent.name == "Alice"
