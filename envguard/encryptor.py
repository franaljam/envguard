"""Encrypt and decrypt sensitive values in an env dict."""
from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PASS", "PRIVATE", "PWD")


class EncryptionError(Exception):
    pass


def _is_sensitive(key: str) -> bool:
    upper = key.upper()
    return any(s in upper for s in _SENSITIVE)


def _xor_cipher(value: str, passphrase: str) -> bytes:
    key_bytes = hashlib.sha256(passphrase.encode()).digest()
    data = value.encode()
    return bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))


@dataclass
class EncryptResult:
    encrypted: Dict[str, str]
    encrypted_keys: List[str]

    def count(self) -> int:
        return len(self.encrypted_keys)

    def summary(self) -> str:
        if not self.encrypted_keys:
            return "No values encrypted."
        keys = ", ".join(sorted(self.encrypted_keys))
        return f"Encrypted {self.count()} key(s): {keys}"


def encrypt_env(
    env: Dict[str, str],
    passphrase: str,
    keys: Optional[List[str]] = None,
    auto_detect: bool = True,
) -> EncryptResult:
    if not passphrase:
        raise EncryptionError("Passphrase must not be empty.")
    result = dict(env)
    encrypted_keys: List[str] = []
    targets = keys if keys is not None else (
        [k for k in env if _is_sensitive(k)] if auto_detect else []
    )
    for k in targets:
        if k not in env:
            continue
        raw = _xor_cipher(env[k], passphrase)
        result[k] = "enc:" + base64.b64encode(raw).decode()
        encrypted_keys.append(k)
    return EncryptResult(encrypted=result, encrypted_keys=encrypted_keys)


def decrypt_env(
    env: Dict[str, str],
    passphrase: str,
) -> Dict[str, str]:
    if not passphrase:
        raise EncryptionError("Passphrase must not be empty.")
    result = {}
    for k, v in env.items():
        if v.startswith("enc:"):
            raw = base64.b64decode(v[4:])
            result[k] = _xor_cipher(raw.decode("latin-1"), passphrase).decode("utf-8", errors="replace")
        else:
            result[k] = v
    return result
