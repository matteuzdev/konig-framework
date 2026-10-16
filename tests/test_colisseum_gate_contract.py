"""Colisseum E2E gate contract regression checks."""
from pathlib import Path

def test_required_gate_fails_closed():
    source = Path("core/engine/orchestrator.py").read_text(encoding="utf-8")
    assert "Required gate unavailable; fail closed" in source
    assert "COLISSEUM_EVIDENCE_REQUIRED" in source

def test_code_qa_require_successful_executed_evidence():
    source = Path("core/engine/orchestrator.py").read_text(encoding="utf-8")
    assert 'if not sandbox_result or not sandbox_result.success:' in source

def test_global_engineering_workflow_is_preserved():
    source = Path(".agents/workflows/greenfield-delivery.yaml").read_text(encoding="utf-8")
    for stage in ("create-prd", "design-architecture", "design-ui-ux-pro-max", "implement-fullstack-core", "run-qa-homologation"):
        assert stage in source
