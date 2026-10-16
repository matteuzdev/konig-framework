import unittest
from core.business.contracts import ActionRisk, BusinessTask, Evidence, RunStatus

class BusinessContractTests(unittest.TestCase):
    def test_external_write_waits_for_approval(self):
        task = BusinessTask("Publish page", "marketing", "tenant-a", ActionRisk.EXTERNAL_WRITE)
        self.assertEqual(task.request_execution(), RunStatus.AWAITING_APPROVAL)
        with self.assertRaises(PermissionError):
            task.approve("owner", "tenant-b")
        task.approve("owner", "tenant-a")
        self.assertEqual(task.request_execution(), RunStatus.RUNNING)

    def test_completion_requires_verified_evidence(self):
        task = BusinessTask("Prepare draft", "sales", "tenant-a")
        task.request_execution()
        with self.assertRaises(ValueError):
            task.complete()
        task.evidence.append(Evidence("file", "draft.md", verified=True))
        task.complete()
        self.assertEqual(task.status, RunStatus.COMPLETED)

if __name__ == "__main__":
    unittest.main()
