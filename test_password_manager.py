import string

import pytest

from password_logic import generate_password, validate_fields
from crypto_utils import generate_salt, derive_key, encrypt_password, decrypt_password, key_is_correct
import db


# ---------------------------- password_logic ------------------------------- #

def test_generate_password_length():
    assert len(generate_password(12)) == 12
    assert len(generate_password(20)) == 20


def test_generate_password_has_all_character_types():
    password = generate_password(12)
    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(c in string.punctuation for c in password)


def test_generate_password_rejects_too_short_length():
    with pytest.raises(ValueError):
        generate_password(3)


def test_validate_fields_rejects_blank_or_whitespace():
    assert validate_fields("", "user", "pw123") is False
    assert validate_fields("site.com", "   ", "pw123") is False
    assert validate_fields("site.com", "user", "") is False


def test_validate_fields_accepts_filled_fields():
    assert validate_fields("site.com", "user", "pw123") is True


# ---------------------------- crypto_utils ------------------------------- #

def test_encrypt_decrypt_roundtrip():
    salt = generate_salt()
    key = derive_key("my-master-password", salt)
    token = encrypt_password("super-secret", key)
    assert decrypt_password(token, key) == "super-secret"


def test_same_password_and_salt_produce_same_key():
    salt = generate_salt()
    key1 = derive_key("my-master-password", salt)
    key2 = derive_key("my-master-password", salt)
    assert key1 == key2


def test_wrong_master_password_fails_check():
    salt = generate_salt()
    correct_key = derive_key("correct-password", salt)
    wrong_key = derive_key("wrong-password", salt)
    check_token = encrypt_password("verify", correct_key)
    assert key_is_correct(correct_key, check_token) is True
    assert key_is_correct(wrong_key, check_token) is False


# ---------------------------- db ------------------------------- #

def test_add_and_get_entry(tmp_path):
    db_path = str(tmp_path / "test_passwords.db")
    db.init_db(db_path)
    db.add_entry("example.com", "user@example.com", "encrypted-token", db_path)

    result = db.get_entry("example.com", db_path)
    assert result == ("example.com", "user@example.com", "encrypted-token")


def test_get_entry_is_case_insensitive(tmp_path):
    db_path = str(tmp_path / "test_passwords.db")
    db.init_db(db_path)
    db.add_entry("Example.com", "user@example.com", "encrypted-token", db_path)

    assert db.get_entry("example.com", db_path) is not None


def test_get_entry_returns_none_when_missing(tmp_path):
    db_path = str(tmp_path / "test_passwords.db")
    db.init_db(db_path)
    assert db.get_entry("nonexistent.com", db_path) is None
