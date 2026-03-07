---
title: Your AI Agent's Memories Aren't Encrypted
date: 2026-03-01
type: explanation
summary: Google ADK stores everything your agent knows — tool calls, user messages, conversation context — in plaintext SQLite. Here's why that matters and how to fix it.
tags:
  - python
  - ai
  - google adk
  - security
  - encryption
  - open source
---

You built an AI agent. It calls tools, remembers conversations, and tracks state across sessions. It works. You deploy it. Users start talking to it — sharing API keys, asking about internal systems, passing along customer data through tool calls.

Every word of that is sitting in a SQLite file, in plaintext, readable by anyone with file access.

This isn't a vulnerability you introduced. It's the default behavior of Google ADK's session persistence. And if you're building agents that handle anything beyond demo data, it's a problem you need to solve before production.

---

## The Problem You Don't Know You Have

Google's Agent Development Kit gives you `DatabaseSessionService` — a session persistence layer that stores agent state in a relational database. It handles the hard parts: session lifecycle, event ordering, state reconstruction across turns. You configure it with a connection string and move on to the interesting work of building your agent.

```python
from google.adk.sessions import DatabaseSessionService

session_service = DatabaseSessionService(db_url="sqlite+aiosqlite:///sessions.db")
```

That `sessions.db` file now contains everything your agent processes. Every user message. Every tool call and its arguments. Every function response. Every piece of state your agent carries between turns. All of it stored as structured data, fully readable, with no encryption layer between the file system and your users' data.

Open the file. Run a query. Read the JSON. There's nothing stopping you — and nothing stopping anyone else who gains access to that file.

---

## What's Actually in a Session?

ADK sessions aren't just chat logs. They're structured records of everything your agent does:

- **User messages** — the full text of every prompt your users send
- **Tool calls** — function names and their complete argument payloads
- **Function responses** — the raw data your tools return, including API responses and database query results
- **Agent state** — accumulated context the agent carries across turns
- **Event metadata** — timestamps, ordering, session identifiers

![Data flows through an ADK agent session — from user messages and tool calls to storage. DatabaseSessionService stores it as readable JSON. EncryptedSessionService stores it as encrypted blobs.](/adk-session-data-flow.svg)

Think about what flows through a real agent. A user asks your agent to look up a customer record — the tool call contains the query, and the response contains the customer's data. A user passes an API key so the agent can call an external service — that key is now stored in the session. A user discusses internal business logic — the agent remembers it for context, and the database remembers it forever.

And none of this is hypothetical. If you open that SQLite file with any database browser, every session row contains JSON you can read without any special tooling. No keys, no decryption step, no access control. The file is the data, and the data is in the clear.

The session database isn't a chat transcript. It's a complete operational record of everything your agent knows about your users and what it did on their behalf. It's like a kitchen where every order ticket, every ingredient substitution, and every customer allergy note gets pinned to the wall in plain sight — and the back door is unlocked.

---

## Why This Matters Now

When agents live in notebooks and demos, plaintext sessions are fine. Nobody's passing real credentials to a prototype. But agents are leaving the sandbox. It's the difference between cooking at home and running a restaurant — in your own kitchen, nobody cares if the pantry is unlocked. The moment you're serving customers, health inspectors show up and every storage decision matters. Google released ADK to help developers build production-grade agents, and teams are taking that seriously — building agents that handle real workflows with real data.

Production agents process real user data. They call real APIs with real keys. They handle internal workflows where the conversation itself is sensitive. The moment your agent crosses from "demo" to "deployed," the session database becomes a data-at-rest liability.

Compliance frameworks are explicit about this:

- **SOC 2** requires encryption of sensitive data at rest
- **HIPAA** mandates encryption for protected health information in storage
- **GDPR** expects appropriate technical measures to protect personal data

These aren't edge cases. If your agent processes user data and you're pursuing any compliance certification, an auditor will ask how session data is protected at rest. "It's in a SQLite file" is not an answer that passes review.

"The agent works" is necessary. "The agent is secure" is what lets you ship it. And right now, ADK gives you persistence but not protection. That gap between working and secure is exactly where production agents get stuck.

---

## The Fix Is One Import Away

[adk-secure-sessions](https://github.com/Alberto-Codes/adk-secure-sessions) is an encrypted session storage layer for Google ADK. It's a drop-in replacement — same session interface, same behavior, encrypted storage.

```python
from adk_secure_sessions import EncryptedSessionService, FernetBackend

session_service = EncryptedSessionService(
    db_url="sqlite+aiosqlite:///sessions.db",
    backend=FernetBackend("your-secret-key"),
)
```

Your agent code doesn't change. Every call to create, get, list, or delete sessions works the same way. The difference is what happens at the storage layer: session data is serialized, encrypted, then written. On read, it's decrypted and deserialized. The SQLite file contains encrypted blobs instead of readable JSON.

The encryption is Fernet — AES-128-CBC with HMAC-SHA256 for authenticated encryption, meaning data is both confidential and tamper-evident. Key derivation uses PBKDF2-HMAC-SHA256 with 480,000 iterations, so your passphrase becomes a strong cryptographic key without managing raw key material.

Two runtime dependencies: `google-adk` and `cryptography`. Nothing exotic. Nothing heavy. No C extensions to compile, no system libraries to install.

The library extends ADK's `BaseSessionService` directly rather than wrapping `DatabaseSessionService`. That's a deliberate architectural choice — and one that came from a failed first attempt with the decorator pattern. That story, and the generalizable lesson about when composition breaks down, are coming in Part 4 of this series.

---

## What Changes, What Doesn't

What stays the same:

- Your agent code — no changes to how you interact with sessions
- Session behavior — create, read, update, delete all work identically
- The database — still SQLite, still a single file, still portable

What changes:

- Session data at rest is encrypted — the file is useless without the key
- Error messages are precise — `DecryptionError` and `ConfigurationError` tell you exactly what went wrong
- You need a passphrase — managed via environment variable, not hardcoded

```python
import os
from adk_secure_sessions import EncryptedSessionService, FernetBackend

session_service = EncryptedSessionService(
    db_url="sqlite+aiosqlite:///sessions.db",
    backend=FernetBackend(os.environ["SESSION_KEY"]),
)
```

That's the production pattern. The passphrase lives in your environment, the encrypted data lives in your database, and the two never meet in your codebase. Standard secrets management — nothing new to learn, nothing unusual to maintain.

> With `DatabaseSessionService`, an attacker with file access sees everything. With `EncryptedSessionService`, they see noise.

---

## Key Takeaways

- **Google ADK stores session state in plaintext by default** — every tool call, user message, and piece of agent context is readable in the database
- **Sessions contain more than chat history** — tool arguments, API responses, and accumulated state are all persisted
- **Production agents need encryption at rest** — compliance frameworks require it, and good engineering practice demands it
- **adk-secure-sessions is a drop-in replacement** — one import change, same API, encrypted storage
- **Get started now**: `pip install adk-secure-sessions`

---

## Further Reading

- [adk-secure-sessions on GitHub](https://github.com/Alberto-Codes/adk-secure-sessions)
- [adk-secure-sessions on PyPI](https://pypi.org/project/adk-secure-sessions/)
- [Google Agent Development Kit](https://google.github.io/adk-docs/)
- Next in this series: Encrypting ADK Sessions in 5 Minutes (Part 2)
