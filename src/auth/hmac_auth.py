import hashlib
import hmac
import os
from typing import Optional


def verify_signature(payload_body: bytes, signature_header: Optional[str]) -> bool:
    """Verifies the GitHub webhook signature using HMAC SHA256 and constant-time comparison."""
    if not signature_header:
        return False

    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    if not secret:
        return False

    if not signature_header.startswith("sha256="):
        return False

    expected_signature = "sha256=" + hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)
