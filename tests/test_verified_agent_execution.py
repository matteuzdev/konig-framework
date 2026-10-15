import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from core.engine.orchestrator import KonigOrchestrator


class VerifiedAgentExecutionTests(unittest.TestCase):
    def test_live_path_requests_strict_provider(self):
        orchestrator = KonigOrchestrator()
        orchestrator.llm_router.generate = Mock(return_value=SimpleNamespace(verified_provider_call=True, content="real"))
        agent = SimpleNamespace(name="Dan", role="Engineer", signature="[Dan - Engineer]")
        task = SimpleNamespace(name="Implement", description="Build feature", expected_output="Code")
        result = orchestrator.execute_agent_step_verified(agent, task)
        self.assertEqual(result.content, "real")
        self.assertTrue(orchestrator.llm_router.generate.call_args.kwargs["require_real_provider"])

    def test_live_path_rejects_unverified_output(self):
        orchestrator = KonigOrchestrator()
        orchestrator.llm_router.generate = Mock(return_value=SimpleNamespace(verified_provider_call=False))
        agent = SimpleNamespace(name="Dan", role="Engineer", signature="[Dan - Engineer]")
        task = SimpleNamespace(name="Implement", description="Build feature", expected_output="Code")
        with self.assertRaises(RuntimeError):
            orchestrator.execute_agent_step_verified(agent, task)


if __name__ == "__main__":
    unittest.main()
