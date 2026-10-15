import unittest
from core.runtime.provenance import ExecutionEvidence, OutputOrigin, UnverifiedExecutionError

class ProvenanceTests(unittest.TestCase):
    def test_simulated_output_is_not_live(self):
        with self.assertRaises(UnverifiedExecutionError):
            ExecutionEvidence(OutputOrigin.SIMULATED, 'draft').require_real_generation()

    def test_template_is_not_verified_qa(self):
        with self.assertRaises(UnverifiedExecutionError):
            ExecutionEvidence(OutputOrigin.TEMPLATE, 'draft', test_exit_code=0).require_verified_test()

    def test_provider_requires_request_id(self):
        with self.assertRaises(UnverifiedExecutionError):
            ExecutionEvidence(OutputOrigin.PROVIDER, 'response').require_real_generation()

    def test_verified_generation(self):
        ExecutionEvidence(OutputOrigin.PROVIDER, 'response', 'request-123').require_real_generation()

if __name__ == '__main__':
    unittest.main()
