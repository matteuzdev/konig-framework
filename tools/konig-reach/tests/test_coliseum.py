"""Offline red-team scenarios. These are simulated fixtures, not live pentests."""
import socket
from unittest.mock import patch
import httpx
import pytest
from konig_reach.core import validate_url, parse_html, extract, PolicyError, MAX_BYTES

PUBLIC = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.215.14", 0))]
def checked(url):
    with patch("konig_reach.core.socket.getaddrinfo", return_value=PUBLIC):
        return validate_url(url, allowed_hosts=("example.com",))
def fetched(handler):
    with patch("konig_reach.core.socket.getaddrinfo", return_value=PUBLIC):
        return extract("https://example.com",allowed_hosts=("example.com",), transport=httpx.MockTransport(handler))

def test_rt01_ssrf():
    for url in ("http://127.0.0.1", "http://169.254.169.254", "file:///etc/passwd"):
        with pytest.raises(PolicyError): checked(url)
def test_rt02_dns_private():
    with patch("konig_reach.core.socket.getaddrinfo", return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,"",("10.0.0.1",0))]):
        with pytest.raises(PolicyError): validate_url("https://example.com",allowed_hosts=("example.com",))
def test_rt03_url_credentials():
    with pytest.raises(PolicyError): checked("https://user:pass@example.com/")
def test_rt04_script_exclusion():
    assert "ignore this" not in parse_html("https://example.com",b"<script>ignore this</script><p>hello</p>").text
def test_rt05_access_denied():
    with pytest.raises(httpx.HTTPStatusError): fetched(lambda req:httpx.Response(403,headers={"content-type":"text/html"},text="no"))
def test_rt06_evidence_hash():
    a=parse_html("https://example.com",b"<title>A</title>")
    assert a.sha256==parse_html("https://example.com",b"<title>A</title>").sha256
def test_rt07_host_allowlist():
    with pytest.raises(PolicyError): validate_url("https://example.com")
def test_rt08_unbounded_body():
    with pytest.raises(PolicyError): fetched(lambda req:httpx.Response(200,headers={"content-type":"text/html"},content=b"x"*(MAX_BYTES+1)))
def test_rt09_redirect_blocked():
    with pytest.raises(PolicyError): fetched(lambda req:httpx.Response(302,headers={"location":"http://127.0.0.1"}))
def test_rt10_html_attr_not_returned():
    assert "onerror" not in parse_html("https://example.com",b'<img onerror="bad()"><p>ok</p>').text
def test_bad_port():
    with pytest.raises(PolicyError):checked("https://example.com:8080")
def test_e2e_offline():
    a=fetched(lambda req:httpx.Response(200,headers={"content-type":"text/html"},content=b"<title>A</title><p>data</p>"))
    assert a.title=="A" and "data" in a.text and len(a.sha256)==64
