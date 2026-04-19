import pytest
from envguard.encryptor import (
    EncryptionError,
    encrypt_env,
    decrypt_env,
)


ENV = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "s3cr3t",
    "API_TOKEN": "tok_abc123",
    "PORT": "8080",
}

PASS = "strongpassphrase"


def test_sensitive_keys_encrypted():
    result = encrypt_env(ENV, PASS)
    assert result.encrypted["DB_PASSWORD"].startswith("enc:")
    assert result.encrypted["API_TOKEN"].startswith("enc:")


def test_non_sensitive_keys_unchanged():
    result = encrypt_env(ENV, PASS)
    assert result.encrypted["APP_NAME"] == "myapp"
    assert result.encrypted["PORT"] == "8080"


def test_encrypted_keys_list():
    result = encrypt_env(ENV, PASS)
    assert "DB_PASSWORD" in result.encrypted_keys
    assert "API_TOKEN" in result.encrypted_keys
    assert "APP_NAME" not in result.encrypted_keys


def test_count_matches_encrypted_keys():
    result = encrypt_env(ENV, PASS)
    assert result.count() == len(result.encrypted_keys)


def test_original_not_mutated():
    original = dict(ENV)
    encrypt_env(ENV, PASS)
    assert ENV == original


def test_explicit_keys_override_auto_detect():
    result = encrypt_env(ENV, PASS, keys=["PORT"], auto_detect=False)
    assert result.encrypted["PORT"].startswith("enc:")
    assert not result.encrypted["DB_PASSWORD"].startswith("enc:")


def test_missing_explicit_key_silently_ignored():
    result = encrypt_env(ENV, PASS, keys=["NONEXISTENT"])
    assert "NONEXISTENT" not in result.encrypted


def test_empty_passphrase_raises():
    with pytest.raises(EncryptionError):
        encrypt_env(ENV, "")


def test_decrypt_roundtrip():
    encrypted = encrypt_env(ENV, PASS).encrypted
    decrypted = decrypt_env(encrypted, PASS)
    assert decrypted["DB_PASSWORD"] == ENV["DB_PASSWORD"]
    assert decrypted["API_TOKEN"] == ENV["API_TOKEN"]
    assert decrypted["APP_NAME"] == ENV["APP_NAME"]


def test_decrypt_empty_passphrase_raises():
    with pytest.raises(EncryptionError):
        decrypt_env(ENV, "")


def test_summary_no_encryptions():
    result = encrypt_env({"PORT": "8080"}, PASS)
    assert result.summary() == "No values encrypted."


def test_summary_with_encryptions():
    result = encrypt_env(ENV, PASS)
    assert "Encrypted" in result.summary()
    assert "DB_PASSWORD" in result.summary()
