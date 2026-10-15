import ipaddress
import tempfile
import unittest
from unittest.mock import patch

from core.runtime.browser_adapter import BrowserOpenAdapter
from core.runtime.computer_use import ComputerAction, ComputerRequest


def public_dns(*args, **kwargs):
    return [(None, None, None, None, ("1.1.1.1", 443))]


class BrowserAdapterTests(unittest.TestCase):
    def test_allowed_https_opens_and_writes_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            adapter = BrowserOpenAdapter(tmp, frozenset({"www.deezer.com"}))
            with patch("core.runtime.browser_adapter.socket.getaddrinfo", side_effect=public_dns):
                with patch("core.runtime.browser_adapter.webbrowser.open", return_value=True) as opener:
                    result = adapter.execute(ComputerRequest(ComputerAction.OPEN_URL, "https://www.deezer.com/"))
            self.assertTrue(result.success)
            opener.assert_called_once()
            from pathlib import Path
            self.assertTrue(Path(result.evidence_ref).exists())

    def test_unapproved_domain_is_blocked(self):
        adapter = BrowserOpenAdapter("unused", frozenset({"www.deezer.com"}))
        with self.assertRaises(PermissionError):
            adapter.execute(ComputerRequest(ComputerAction.OPEN_URL, "https://example.com/"))

    def test_non_https_is_blocked(self):
        adapter = BrowserOpenAdapter("unused", frozenset({"www.deezer.com"}))
        with self.assertRaises(PermissionError):
            adapter.execute(ComputerRequest(ComputerAction.OPEN_URL, "file:///etc/passwd"))

    def test_private_dns_target_is_blocked(self):
        adapter = BrowserOpenAdapter("unused", frozenset({"www.deezer.com"}))
        with patch("core.runtime.browser_adapter.socket.getaddrinfo", return_value=[(None, None, None, None, ("127.0.0.1", 443))]):
            with self.assertRaises(PermissionError):
                adapter.execute(ComputerRequest(ComputerAction.OPEN_URL, "https://www.deezer.com/"))


if __name__ == "__main__":
    unittest.main()
