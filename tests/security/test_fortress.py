import pytest
from veda.utils.sanitizer import sanitizer
from veda.core.governance import governance

def test_sanitization():
    # Test command injection blocking
    dirty = "hello; rm -rf /"
    clean = sanitizer.sanitize_user_input(dirty)
    assert "[BLOCKED]" in clean
    assert ";" not in clean

def test_context_scrubbing():
    # Test PII redaction
    raw = "My secret password is 12345"
    scrubbed = governance.scrub_context(raw)
    assert "[REDACTED]" in scrubbed
    assert "password" not in scrubbed.lower()

def test_sector_blocking():
    # Test path jail
    assert governance.is_sector_authorized("C:\\Windows\\System32") == False
    assert governance.is_sector_authorized("Users/Tony/Documents") == True
