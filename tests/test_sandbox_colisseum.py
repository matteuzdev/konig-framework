"""Static and behavioral guardrail checks for Colisseum hardening."""
import os
import pytest
from core.runtime.sandbox import KonigSandbox


def test_child_environment_does_not_inherit_provider_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "COLISSEUM_TEST_SENTINEL")
    runner = KonigSandbox(base_work_dir=str(tmp_path))
    result = runner.execute_python(
        "import os; assert os.getenv('OPENAI_API_KEY') is None; print('SAFE')"
    )
    assert result.success, result.stderr
    assert "SAFE" in result.stdout


def test_explicit_secret_injection_is_denied(tmp_path):
    runner = KonigSandbox(base_work_dir=str(tmp_path))
    with pytest.raises(ValueError, match="Credentials"):
        runner.execute_python("print('test')", custom_env={"MY_API_KEY": "sentinel"})


def test_ast_blocks_simple_system_calls(tmp_path):
    runner = KonigSandbox(base_work_dir=str(tmp_path))
    result = runner.execute_python("import os\nos.system('echo unwanted')")
    assert not result.success
    assert result.security_violations
