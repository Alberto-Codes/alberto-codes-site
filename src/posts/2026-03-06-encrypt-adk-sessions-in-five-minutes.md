---
title: Encrypt ADK Sessions in 5 Minutes
date: 2026-03-06
type: how-to
summary: Install adk-secure-sessions, swap one import, and verify your agent's session data is encrypted at rest — start to finish in under 5 minutes.
tags:
  - python
  - ai
  - google adk
  - security
  - encryption
  - open source
---

[In Part 1](/blog/2026-03-01-your-ai-agents-memories-arent-encrypted), I showed that Google ADK stores everything your agent knows — tool calls, user messages, conversation context — in plaintext SQLite. If that made you uncomfortable, this post fixes it.

This is the recipe card. Ingredients, steps, done. The explanation of why the soufflé rises comes later in Part 3.

---

## Prerequisites

- **Python 3.12+**
- **An existing ADK agent** using `DatabaseSessionService` (or a willingness to create a minimal one)

No system libraries, no C compilation, no Docker. The library is pure Python with two runtime dependencies: `google-adk` and `cryptography`. A short ingredient list.

---

## Step 1: Install

```bash
pip install adk-secure-sessions
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add adk-secure-sessions
```

Verify the install:

```bash
python -c "import adk_secure_sessions; print('OK')"
```

---

## Step 2: Swap the Import

Your agent code probably has something like this:

```python
# Before — ADK default (unencrypted):
from google.adk.sessions import DatabaseSessionService

session_service = DatabaseSessionService(
    db_url="sqlite+aiosqlite:///sessions.db"
)
```

Replace it with:

```python
# After — encrypted:
from adk_secure_sessions import EncryptedSessionService, FernetBackend

session_service = EncryptedSessionService(
    db_url="sqlite+aiosqlite:///sessions.db",
    backend=FernetBackend("your-secret-passphrase"),
)
```

Two changes: the import line and the constructor. Everything else in your agent stays the same — `create_session`, `get_session`, `list_sessions`, `delete_session`, `append_event` — the full ADK session lifecycle, identical behavior. The difference is what hits the disk.

---

## Step 3: Use the Async Context Manager

For proper connection cleanup, wrap the service in `async with`. Here's a complete, runnable script:

```python
import asyncio
from adk_secure_sessions import EncryptedSessionService, FernetBackend


async def main():
    backend = FernetBackend("my-secret-passphrase")

    async with EncryptedSessionService(
        db_url="sqlite+aiosqlite:///sessions.db",
        backend=backend,
    ) as service:
        # Create a session with sensitive state
        session = await service.create_session(
            app_name="my-agent",
            user_id="user-123",
            state={
                "patient_name": "Jane Doe",
                "diagnosis_code": "J06.9",
                "api_key": "sk-secret-key-12345",
            },
        )
        print(f"Created session: {session.id}")

        # Retrieve — state is automatically decrypted
        session = await service.get_session(
            app_name="my-agent",
            user_id="user-123",
            session_id=session.id,
        )
        print(f"Decrypted state: {session.state}")

        # List sessions for this app/user
        response = await service.list_sessions(
            app_name="my-agent",
            user_id="user-123",
        )
        print(f"Sessions found: {len(response.sessions)}")

        # Clean up when you're done
        await service.delete_session(
            app_name="my-agent",
            user_id="user-123",
            session_id=session.id,
        )
        print("Session deleted")


asyncio.run(main())
```

Copy this into a file and run it. The API behaves identically to ADK's `DatabaseSessionService` — same methods, same signatures, same return types. The only difference is what's stored on disk: switching from a glass jar to a lockbox. Same ingredients go in, same ingredients come out, but nobody can peek inside without the key.

---

## Step 4: Verify the Encryption

Trust but verify. Open the SQLite database directly and confirm the data is actually encrypted.

**Using the `sqlite3` CLI:**

```bash
sqlite3 sessions.db "SELECT state FROM sessions LIMIT 1;"
```

You'll see a base64-encoded string — the encrypted envelope — not readable JSON:

```
AQFnQUFBQUJuVm1Gc2RX...
```

**Using Python:**

```python
import sqlite3

conn = sqlite3.connect("sessions.db")
row = conn.execute("SELECT state FROM sessions LIMIT 1").fetchone()
print(row[0][:60])  # First 60 chars of the encrypted envelope
conn.close()
```

What you won't see: `{"patient_name": "Jane Doe", "diagnosis_code": "J06.9"}`. That's the point. With `DatabaseSessionService`, anyone with file access reads your mise en place. With `EncryptedSessionService`, they see noise.

For a more convincing demo, run the [basic usage example](https://github.com/Alberto-Codes/adk-secure-sessions/blob/main/examples/basic_usage.py) from the repo — it runs a real multi-turn ADK agent with Ollama and then inspects the raw database to prove no plaintext leaks. After a three-turn conversation about patient intake, the database contains zero occurrences of "Jane Doe" or "headache."

---

## Step 5: Manage Your Passphrase

The passphrase is the only secret. Never hardcode it.

```python
import os
from adk_secure_sessions import EncryptedSessionService, FernetBackend

backend = FernetBackend(os.environ["SESSION_KEY"])
```

Set it in your environment, your `.env` file, or your secrets manager. The library handles everything else — `FernetBackend` derives a cryptographic key using PBKDF2-HMAC-SHA256 with 480,000 iterations. You don't need to generate, store, or rotate raw key material.

If you use the wrong passphrase to read a session encrypted with a different one, you get a clear `DecryptionError` — never garbage data, never silent corruption.

---

## What You Just Built

Five steps, plaintext to encrypted-at-rest:

1. **Installed** — `pip install adk-secure-sessions`
2. **Swapped** — one import, one constructor change
3. **Ran** — same API, encrypted storage
4. **Verified** — the database contains ciphertext, not JSON
5. **Secured** — passphrase in the environment, not the codebase

Your agent still works the same way. Your tests still pass. But the SQLite file is now useless without the key — like a walk-in freezer with a combination lock. Nothing changes about how the food is stored or retrieved, but the back door isn't open anymore.

---

## Error Handling

When things go wrong, the library tells you what happened:

- **`ConfigurationError`** — raised at startup if the backend is misconfigured. You'll catch this before any data is written.
- **`DecryptionError`** — raised if you read a session with the wrong key. The library never returns garbage.

```python
from adk_secure_sessions import (
    ConfigurationError,
    DecryptionError,
    EncryptedSessionService,
    FernetBackend,
)

try:
    async with EncryptedSessionService(
        db_url="sqlite+aiosqlite:///sessions.db",
        backend=FernetBackend("correct-passphrase"),
    ) as service:
        session = await service.get_session(
            app_name="my-agent",
            user_id="user-123",
            session_id="some-session-id",
        )
        if session is None:
            print("Session not found")
except ConfigurationError:
    print("Backend doesn't conform to EncryptionBackend protocol")
except DecryptionError:
    print("Wrong key — cannot decrypt session data")
```

---

## Key Takeaways

- **One install, one import change** — `pip install adk-secure-sessions`, swap the constructor, done
- **Full ADK lifecycle** — `create_session`, `get_session`, `list_sessions`, `delete_session`, and `append_event` all work identically
- **Verify it yourself** — inspect the SQLite file to confirm ciphertext, not plaintext
- **Passphrase management** — use environment variables, never hardcode secrets
- **Clear errors** — `DecryptionError` for wrong keys, `ConfigurationError` for bad setup

---

## Further Reading

- [adk-secure-sessions documentation](https://alberto-codes.github.io/adk-secure-sessions/)
- [Getting Started guide](https://alberto-codes.github.io/adk-secure-sessions/getting-started/) — the library's own tutorial with additional details
- [adk-secure-sessions on PyPI](https://pypi.org/project/adk-secure-sessions/)
- [Google ADK Session docs](https://google.github.io/adk-docs/sessions/session/) — the underlying session model this library encrypts
- Previous in this series: [Your AI Agent's Memories Aren't Encrypted](/blog/2026-03-01-your-ai-agents-memories-arent-encrypted) (Part 1)
- Next in this series: The Architecture of Encrypted Sessions (Part 3)
