import unittest
from unittest.mock import Mock

from core.runtime.computer_use import (
    ComputerAction, ComputerRequest, ComputerResult,
    ComputerUsePolicy, ComputerUseService,
)


class ComputerUseTests(unittest.TestCase):
    def test_denied_by_default(self):
        adapter = Mock()
        service = ComputerUseService(adapter, ComputerUsePolicy())
        with self.assertRaises(PermissionError):
            service.execute(ComputerRequest(ComputerAction.OPEN_URL, "https://deezer.com"))
        adapter.execute.assert_not_called()

    def test_open_url_with_explicit_permission(self):
        adapter = Mock()
        adapter.execute.return_value = ComputerResult(ComputerAction.OPEN_URL, True, "audit/1")
        service = ComputerUseService(adapter, ComputerUsePolicy(frozenset({ComputerAction.OPEN_URL})))
        result = service.execute(ComputerRequest(ComputerAction.OPEN_URL, "https://deezer.com"))
        self.assertEqual(result.evidence_ref, "audit/1")

    def test_click_requires_approval(self):
        adapter = Mock()
        service = ComputerUseService(adapter, ComputerUsePolicy(frozenset({ComputerAction.CLICK})))
        with self.assertRaises(PermissionError):
            service.execute(ComputerRequest(ComputerAction.CLICK, "play"))
        adapter.execute.assert_not_called()

    def test_missing_evidence_rejected(self):
        adapter = Mock()
        adapter.execute.return_value = ComputerResult(ComputerAction.OPEN_URL, True, "")
        service = ComputerUseService(adapter, ComputerUsePolicy(frozenset({ComputerAction.OPEN_URL})))
        with self.assertRaises(RuntimeError):
            service.execute(ComputerRequest(ComputerAction.OPEN_URL, "https://deezer.com"))


if __name__ == "__main__":
    unittest.main()
