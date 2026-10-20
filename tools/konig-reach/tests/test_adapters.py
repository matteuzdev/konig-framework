import socket
from unittest.mock import patch
import pytest
from konig_reach.adapters import list_capabilities, scrapling_extract
from konig_reach.core import PolicyError

PUBLIC=[(socket.AF_INET,socket.SOCK_STREAM,6,"",("93.184.215.14",0))]
def test_capability_honesty():
    status={v["name"]:v["readiness"] for v in list_capabilities()}
    assert status["agent-reach"]=="design-only"
    assert status["browser"]=="design-only"
def test_scrapling_adapter_offline():
    with patch("konig_reach.core.socket.getaddrinfo",return_value=PUBLIC):
        result=scrapling_extract("https://example.com",allowed_hosts=("example.com",),
            fetcher=lambda _:b"<title>Demo</title><p>Text</p>")
    assert result.backend=="scrapling-adapter" and result.title=="Demo"
def test_scrapling_rejects_wrong_result():
    with patch("konig_reach.core.socket.getaddrinfo",return_value=PUBLIC):
        with pytest.raises(PolicyError):
            scrapling_extract("https://example.com",allowed_hosts=("example.com",),
                fetcher=lambda _:"not bytes")
