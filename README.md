# MyPass — Password Manager

A desktop password manager built with Python and Tkinter. Generates strong
random passwords, stores them encrypted in a local SQLite database, and lets
you look them up by website later.

## Features

- **Random password generation** using `secrets` (cryptographically secure),
  guaranteed to include at least one lowercase letter, uppercase letter,
  digit, and symbol.
- **Encrypted storage** — passwords are never written to disk in plaintext.
  Each entry is encrypted with a key derived from a master password using
  PBKDF2-HMAC-SHA256 (390,000 iterations) + Fernet symmetric encryption.
- **SQLite database** for storage, with case-insensitive lookup by website.
- **Master password unlock flow** — first run creates a vault protected by a
  master password; later runs require it to unlock, and it's never stored
  anywhere, only a salt and a verification token are.
- **Unit tested** with `pytest` — password generation, field validation,
  encryption round-trips, and the database layer are all covered.

## Project structure

```
main.py                    # Tkinter GUI, wires everything together
password_logic.py          # Password generation + input validation
crypto_utils.py            # Key derivation, encryption, decryption
db.py                      # SQLite data access layer
test_password_manager.py   # pytest suite
```

## Running it

```
pip install -r requirements.txt
python main.py
```

The first time you run it, you'll be asked to create a master password —
this protects every entry stored afterward. Losing this password means
losing access to saved entries, since it's never stored anywhere.

## Running the tests

```
pytest test_password_manager.py -v
```

## What this is based on

This started as a project from Angela Yu's 100 Days of Code course (Day
29–30) and was substantially rebuilt: the original stored passwords in
plaintext in a CSV file with no encryption and no tests. This version adds
a SQLite backend, password encryption, a search/retrieve feature, and a
pytest suite.
