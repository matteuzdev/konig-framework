import unittest
from unittest.mock import patch

from core.llm.router import KonigLLMRouter


class RouterTruthfulnessTests(unittest.TestCase):
    def test_missing_provider_is_not_treated_as_real_generation(self):
        router = KonigLLMRouter()
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(RuntimeError):
                router._call_provider("gpt-4o", "hello", "", 0.7)

    def test_failed_providers_do_not_charge_for_simulation(self):
        router = KonigLLMRouter()
        with patch.object(router, "_call_provider", side_effect=RuntimeError("offline")):
            with patch("core.llm.router.time.sleep"):
                result = router.generate("hello", model="gpt-4o", fallback_models=[], max_retries_per_model=1)
        self.assertFalse(result.verified_provider_call)
        self.assertTrue(result.usage_is_estimated)
        self.assertEqual(result.cost_usd, 0)
        self.assertEqual(router.cost_manager.total_spent_usd, 0)

    def test_strict_mode_rejects_simulation(self):
        router = KonigLLMRouter()
        with patch.object(router, "_call_provider", side_effect=RuntimeError("offline")):
            with patch("core.llm.router.time.sleep"):
                with self.assertRaises(RuntimeError):
                    router.generate("hello", fallback_models=[], max_retries_per_model=1, require_real_provider=True)
        self.assertEqual(router.cost_manager.total_spent_usd, 0)

    def test_empty_fallback_chain_only_attempts_primary(self):
        router = KonigLLMRouter()
        with patch.object(router, "_call_provider", side_effect=RuntimeError("offline")) as provider:
            with patch("core.llm.router.time.sleep"):
                router.generate("hello", fallback_models=[], max_retries_per_model=1)
        self.assertEqual(provider.call_count, 1)

    def test_real_provider_response_is_marked_verified(self):
        router = KonigLLMRouter()
        with patch.object(router, "_call_provider", return_value=("hello", 10, 5)):
            result = router.generate("hello", model="gpt-4o", fallback_models=[], max_retries_per_model=1)
        self.assertTrue(result.verified_provider_call)
        self.assertFalse(result.usage_is_estimated)


if __name__ == "__main__":
    unittest.main()
