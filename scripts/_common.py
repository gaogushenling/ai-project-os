#!/usr/bin/env python3
"""Shared internals for the ai-project-os scripts.

The scripts stay dependency-free: everything here uses only the Python
standard library and travels with the package. Nothing in this module
performs side effects on import.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

AWS_KEY_PATTERN = re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")
OPENAI_KEY_PATTERN = re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")
PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")

# Credentials that must never be committed to project memory.
SECRET_PATTERNS = (
    AWS_KEY_PATTERN,
    OPENAI_KEY_PATTERN,
    PRIVATE_KEY_PATTERN,
    re.compile(
        r"(?i)\b(?:api[_-]?key|token|password|secret|private[_-]?key|connection[_-]?string)\b"
        r"\s*[:=]\s*[\"']?[^\s\"']{8,}"
    ),
)

# Narrower variant for CLI arguments, where words like "connection" can
# legitimately appear in commands or URLs.
CLI_SECRET_PATTERNS = (
    AWS_KEY_PATTERN,
    OPENAI_KEY_PATTERN,
    PRIVATE_KEY_PATTERN,
    re.compile(r"(?i)(?:api[_-]?key|token|password|secret)\s*[:=]\s*\S{8,}"),
)


def tree_hash(path: Path) -> str:
    """Deterministic SHA-256 over a directory's file paths and contents."""
    digest = hashlib.sha256()
    files = sorted(item for item in path.rglob("*") if item.is_file())
    for item in files:
        relative = item.relative_to(path).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        content = item.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()
