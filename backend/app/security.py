"""Cryptographic signing for secure JSON output."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import uuid
from typing import Any


def sign_report(payload: dict[str, Any]) -> dict[str, Any]:
    secret = os.environ.get("REPORT_SIGNING_SECRET", "matdao-dev-signing-key-change-in-production")
    report_id = str(uuid.uuid4())
    timestamp = int(time.time())

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()

    return {
        **payload,
        "report_metadata": {
            "report_id": report_id,
            "timestamp_unix": timestamp,
            "signature_sha256_hmac": digest,
            "privacy_mode": "zero_persistence",
        },
    }
