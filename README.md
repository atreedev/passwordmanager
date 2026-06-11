**Local Password Manager**

A fully offline, encrypted password manager for Windows with plausible deniability.
No cloud. No telemetry. No internet required.

**What It Does**

Stores your passwords locally in AES-256-GCM encrypted files.
Two decryption keys exist — one real, one fake.
Entering the fake key opens a decoy vault with dummy data.
An attacker who forces you to unlock sees nothing real.

**Security Architecture**

Encryption
Algorithm: AES-256-GCM with a unique nonce per entry
Key derivation: Argon2id (time=3, memory=64MB, parallelism=4)
The decryption key is never stored — derived fresh each session and wiped on close

Authentication
Master PIN hashed with bcrypt and stored in config.db
Argon2 salts stored separately per vault — useless without the PIN

Plausible Deniability (Dual Vault)
Two vaults: data/vault/ (real) and data/decoy/ (fake)
Each vault has a sentinel file encrypted with its respective key
On login, the app silently checks which vault the entered key unlocks
Identical UI and load time regardless of which vault opens

**Tech Stack**
Encryption - cryptography (AES-256-GCM)
Key derivation - argon2-cffi (Argon2id)
PIN hashing - bcrypt
UI - customtkinter
Clipboard - pyperclip

**Setup**
```
Requirements: Python 3.10+, Windows
git clone https://github.com/atreedev/passwordmanager.git
cd passwordmanager
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
**First Launch**
These are set once and cannot be recovered if forgotten.

1. Set a Master PIN — used every time you open the app
2. Set a Real decryption key — unlocks your actual passwords
3. Set a Fake decryption key — unlocks a decoy vault

**Usage**
Add password - Type service name + email + password, click Add
Reveal - Type service name, click Reveal
Copy password - Type service name, click Copy — clears clipboard in 30s
Delete - Type service name, click delete

**Project Structure**

```
├── core/
│   ├── crypto.py        AES-256-GCM encrypt/decrypt, Argon2 key derivation
│   ├── vault.py         File I/O, dual vault routing, sentinel logic
│   └── auth.py          Master PIN hashing, salt storage, config DB
├── ui/
│   ├── app.py           Main window, screen switching
│   └── screens/
│       ├── login.py     2-step auth + first launch setup
│       └── dashboard.py Add, reveal, copy, delete
├── data/                gitignored — encrypted files live here
├── testcases/
│   └── test.py          Crypto and vault unit tests
└── main.py
```

**Limitations**

Windows only (pywin32 dependency)
Master PIN and decryption keys cannot be recovered if forgotten
6-digit numeric PIN has 1,000,000 combinations — Argon2 makes each guess expensive but a longer passphrase is stronger

**Purpose**

Built to explore applied cryptography, key derivation, and local security architecture.
