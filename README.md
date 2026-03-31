# OneBrain Python SDK

[![PyPI version](https://img.shields.io/pypi/v/onebrain.svg)](https://pypi.org/project/onebrain/)
[![Python 3.9+](https://img.shields.io/pypi/pyversions/onebrain.svg)](https://pypi.org/project/onebrain/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Typed](https://img.shields.io/badge/typed-mypy--strict-blue.svg)](https://mypy-lang.org/)

The official Python SDK for **OneBrain** — a persistent AI memory layer for humans
and agents. Store, search, and connect memories across every AI tool you use.

- **Homepage:** <https://onebrain.rocks>
- **Dashboard:** <https://onebrain.rocks/dashboard>
- **API Reference:** <https://onebrain.rocks/docs/api>
- **Repository:** <https://github.com/azappnew/onebrain-python>

---

## Installation

```bash
pip install onebrain
```

Requires **Python 3.9+**. The only runtime dependency is
[httpx](https://www.python-httpx.org/).

---

## Quick Start

```python
import onebrain

client = onebrain.OneBrain(api_key="ob_xxx:secret")

# Store a memory
memory = client.memory.create(content="The user prefers dark mode.")

# Search memories
results = client.memory.search(query="user preferences", limit=5)

# Get brain context for an AI prompt
context = client.brain.context(scope="preferences")

client.close()
```

---

## Authentication

Every request requires an API key. You can provide it in two ways:

### 1. Constructor argument

```python
client = onebrain.OneBrain(api_key="ob_xxx:secret")
```

### 2. Environment variable

```bash
export ONEBRAIN_API_KEY="ob_xxx:secret"
```

```python
client = onebrain.OneBrain()  # reads ONEBRAIN_API_KEY automatically
```

### Getting an API key

1. Sign in at <https://onebrain.rocks/dashboard>.
2. Navigate to **Settings > API Keys**.
3. Click **Create API Key** and copy the full key (`ob_prefix:secret`).
4. The secret is shown only once — store it securely.

---

## API Reference

All methods return typed dataclass objects. List endpoints support cursor-based
pagination with `cursor` and `limit` parameters (default 20, max 100).

### Memory

The core resource. Memories are text snippets with metadata, tags, and optional
entity/project links.

```python
# Create a memory
memory = client.memory.create(
    content="User loves hiking in the Alps.",
    tags=["preference", "travel"],
    entity_id="ent_abc123",
    project_id="prj_xyz789",
    source="chat",
)

# Get a single memory
memory = client.memory.get("mem_abc123")

# List memories (cursor-based pagination)
page = client.memory.list(limit=20)
for m in page.data:
    print(m.id, m.content)

# Paginate through all memories
page = client.memory.list(limit=50)
while page.meta.has_more:
    page = client.memory.list(limit=50, cursor=page.meta.cursor)
    for m in page.data:
        print(m.content)

# Update a memory
updated = client.memory.update("mem_abc123", content="Updated content.")

# Delete a memory
client.memory.delete("mem_abc123")

# Semantic search
results = client.memory.search(
    query="travel preferences",
    limit=10,
    entity_id="ent_abc123",       # optional: scope to entity
    project_id="prj_xyz789",      # optional: scope to project
    tags=["preference"],           # optional: filter by tags
)
for result in results.data:
    print(result.content, result.score)

# Extract memories from unstructured text
extracted = client.memory.extract(
    text="I had a great meeting with Sarah. She mentioned she loves Python "
         "and is working on a new ML project.",
    entity_id="ent_sarah",
)
for mem in extracted.data:
    print(mem.content)

# Import memories in bulk
imported = client.memory.import_bulk(
    memories=[
        {"content": "Fact one", "tags": ["imported"]},
        {"content": "Fact two", "tags": ["imported"]},
        {"content": "Fact three", "tags": ["imported"]},
    ],
    project_id="prj_xyz789",
)
print(f"Imported {imported.meta.total} memories")
```

### Entity

Entities represent people, organizations, or any real-world objects that own
memories.

```python
# Create an entity
entity = client.entity.create(
    name="Sarah Connor",
    type="person",
    metadata={"role": "engineer", "company": "Cyberdyne"},
)

# Get an entity
entity = client.entity.get("ent_abc123")

# List entities
page = client.entity.list(limit=20, type="person")

# Update an entity
updated = client.entity.update("ent_abc123", name="Sarah J. Connor")

# Delete an entity
client.entity.delete("ent_abc123")

# Link two entities
client.entity.link(
    source_id="ent_sarah",
    target_id="ent_cyberdyne",
    relation="works_at",
)

# Get entity relationships (graph)
graph = client.entity.graph(
    entity_id="ent_sarah",
    depth=2,
)
for node in graph.nodes:
    print(node.id, node.name)
for edge in graph.edges:
    print(edge.source, edge.relation, edge.target)

# Merge duplicate entities
merged = client.entity.merge(
    source_id="ent_duplicate",
    target_id="ent_primary",
)
# All memories from source are moved to target; source is deleted
```

### Project

Projects group memories and entities into logical workspaces.

```python
# Create a project
project = client.project.create(
    name="ML Research",
    description="Memory space for the ML research initiative.",
)

# Get a project
project = client.project.get("prj_xyz789")

# List projects
page = client.project.list(limit=20)

# Update a project
updated = client.project.update("prj_xyz789", name="ML Research v2")

# Delete a project
client.project.delete("prj_xyz789")

# Link memories to a project
client.project.link_memory(
    project_id="prj_xyz789",
    memory_id="mem_abc123",
)

# Unlink a memory from a project
client.project.unlink_memory(
    project_id="prj_xyz789",
    memory_id="mem_abc123",
)
```

### Brain

The Brain is the intelligence layer. It builds a unified profile from all your
memories and provides optimized context for AI prompts.

```python
# Get the brain profile for the current user
profile = client.brain.profile()
print(profile.summary)
print(profile.key_facts)
print(profile.preferences)

# Get optimized context for an AI prompt
context = client.brain.context(
    scope="work",               # optional: focus area
    project_id="prj_xyz789",   # optional: scope to project
    max_tokens=2000,            # optional: token budget
)
print(context.system_prompt)    # ready-to-use system prompt
print(context.memories)         # relevant memories included
print(context.token_count)      # actual tokens used
```

### Context

The Context resource provides pre-built, optimized memory scopes for common
AI use cases.

```python
# Get context optimized for a specific scope
ctx = client.context.get(
    scope="coding",
    language="python",
    project_id="prj_xyz789",
    max_tokens=1500,
)
print(ctx.system_prompt)
print(ctx.token_count)

# List available scopes
scopes = client.context.list_scopes()
for scope in scopes.data:
    print(scope.name, scope.description)
```

### Connect

The Connect resource implements the agent sync protocol. It allows AI agents
to register, sync memories bidirectionally, and stay up to date.

```python
# Register an agent connection
connection = client.connect.register(
    agent_name="my-assistant",
    agent_version="1.0.0",
    capabilities=["memory_read", "memory_write"],
)
print(connection.connection_id)

# Sync memories from the agent to OneBrain
sync_result = client.connect.sync(
    connection_id="conn_abc123",
    memories=[
        {"content": "User asked about Python decorators.", "source": "chat"},
        {"content": "User prefers type hints.", "source": "chat"},
    ],
)
print(f"Synced {sync_result.meta.total} memories")

# Pull new memories since last sync
updates = client.connect.pull(
    connection_id="conn_abc123",
    since="2026-01-15T09:30:00Z",
)
for mem in updates.data:
    print(mem.content, mem.created_at)

# Disconnect an agent
client.connect.disconnect("conn_abc123")
```

### Billing

View usage metrics and plan information.

```python
# Get current plan details
plan = client.billing.plan()
print(plan.name)           # e.g., "Pro"
print(plan.memory_limit)   # e.g., 100000
print(plan.memory_used)    # e.g., 4523

# Get usage statistics
usage = client.billing.usage(
    period="current",  # or "2026-01", "2026-02", etc.
)
print(usage.api_calls)
print(usage.memories_created)
print(usage.search_queries)
```

### API Keys

Manage API keys programmatically.

```python
# List all API keys (secrets are masked)
page = client.api_keys.list()
for key in page.data:
    print(key.id, key.prefix, key.name, key.created_at)

# Create a new API key
new_key = client.api_keys.create(
    name="Production Server",
    expires_in_days=90,  # optional: auto-expire
)
print(new_key.key)  # full key shown only once: "ob_prefix:secret"

# Revoke an API key
client.api_keys.revoke("key_abc123")
```

### Skill (SkillForge)

SkillForge lets you create, manage, and execute reusable AI skills backed by
your memory context.

```python
# Create a skill
skill = client.skill.create(
    name="summarize-meeting",
    description="Summarize meeting notes using participant context.",
    prompt_template="Summarize this meeting: {{input}}\n\nContext: {{context}}",
    context_scope="work",
)

# List skills
page = client.skill.list()

# Get a skill
skill = client.skill.get("skill_abc123")

# Execute a skill
result = client.skill.execute(
    skill_id="skill_abc123",
    input="Meeting notes from the Q1 planning session...",
    variables={"department": "engineering"},
)
print(result.output)

# Update a skill
updated = client.skill.update("skill_abc123", name="summarize-meeting-v2")

# Delete a skill
client.skill.delete("skill_abc123")
```

### Briefing (BrainPulse)

BrainPulse generates personalized daily briefings based on your recent memories
and activity.

```python
# Get today's briefing
briefing = client.briefing.get()
print(briefing.summary)
print(briefing.highlights)
print(briefing.action_items)
print(briefing.generated_at)

# Get a briefing for a specific date
briefing = client.briefing.get(date="2026-03-30")

# Get a briefing scoped to a project
briefing = client.briefing.get(project_id="prj_xyz789")

# List past briefings
page = client.briefing.list(limit=7)
for b in page.data:
    print(b.date, b.summary[:80])
```

---

## Async Usage

Every resource method is available in an async variant via `AsyncOneBrain`.

```python
import asyncio
import onebrain


async def main():
    async with onebrain.AsyncOneBrain(api_key="ob_xxx:secret") as client:
        # All methods are awaitable
        memory = await client.memory.create(
            content="Async memory creation works great."
        )

        results = await client.memory.search(query="async", limit=5)
        for r in results.data:
            print(r.content, r.score)

        context = await client.brain.context(scope="coding", max_tokens=1000)
        print(context.system_prompt)


asyncio.run(main())
```

---

## Error Handling

The SDK raises typed exceptions for all error conditions. Every exception
inherits from `OneBrainError`.

```python
import onebrain
from onebrain import (
    OneBrainError,
    OneBrainAuthenticationError,
    OneBrainPermissionError,
    OneBrainNotFoundError,
    OneBrainConflictError,
    OneBrainValidationError,
    OneBrainRateLimitError,
    OneBrainConnectionError,
    OneBrainTimeoutError,
    OneBrainInternalError,
)

client = onebrain.OneBrain()

try:
    memory = client.memory.get("mem_nonexistent")
except OneBrainNotFoundError as exc:
    print(f"Memory not found: {exc}")
except OneBrainAuthenticationError as exc:
    print(f"Invalid API key: {exc}")
except OneBrainRateLimitError as exc:
    print(f"Rate limited. Retry after: {exc.retry_after}s")
except OneBrainValidationError as exc:
    print(f"Validation failed: {exc.details}")
except OneBrainConnectionError as exc:
    print(f"Network error: {exc}")
except OneBrainTimeoutError as exc:
    print(f"Request timed out: {exc}")
except OneBrainError as exc:
    # Catch-all for any OneBrain error
    print(f"API error {exc.status_code}: {exc}")
```

### Error Reference

| Exception                      | HTTP Status | When                                  |
|-------------------------------|-------------|---------------------------------------|
| `OneBrainAuthenticationError` | 401         | Invalid or missing API key            |
| `OneBrainPermissionError`     | 403         | Insufficient permissions              |
| `OneBrainNotFoundError`       | 404         | Resource does not exist               |
| `OneBrainConflictError`       | 409         | Duplicate resource or conflict        |
| `OneBrainValidationError`     | 422         | Invalid request parameters            |
| `OneBrainRateLimitError`      | 429         | Too many requests (see `retry_after`) |
| `OneBrainConnectionError`     | —           | Network / DNS / TLS failure           |
| `OneBrainTimeoutError`        | —           | Request exceeded timeout              |
| `OneBrainInternalError`       | 500         | Server-side error                     |

---

## Configuration

### Client Options

```python
client = onebrain.OneBrain(
    api_key="ob_xxx:secret",                    # required (or env var)
    base_url="https://onebrain.rocks/api/eu",   # default EU region
    timeout=10.0,                                # seconds (default: 10)
    max_retries=2,                               # automatic retries (default: 2)
    headers={"X-Custom-Header": "value"},        # extra headers
)
```

### Regions

| Region | Base URL                            |
|--------|-------------------------------------|
| EU     | `https://onebrain.rocks/api/eu`     |
| US     | `https://onebrain.rocks/api/us`     |
| Self   | `https://your-domain.com/api/v1`    |

---

## Self-Hosted Setup

OneBrain can be self-hosted on your own infrastructure. The SDK works with
any self-hosted instance by setting the `base_url` parameter.

```python
client = onebrain.OneBrain(
    api_key="ob_xxx:secret",
    base_url="https://brain.your-company.com/api/v1",
)
```

### Minimum Setup (just works)

Only two environment variables are required:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/onebrain
JWT_SECRET=your_32_character_random_secret_here
```

That is enough to run OneBrain with password authentication, local storage,
and default free-plan limits.

### Email Setup (for Magic Links)

Magic link authentication requires an email provider. OneBrain uses
[Resend](https://resend.com) for transactional email.

```bash
RESEND_API_KEY=re_your_resend_api_key
MAIL_FROM=noreply@your-domain.com
```

1. Create an account at <https://resend.com>.
2. Verify your sending domain.
3. Generate an API key and set `RESEND_API_KEY`.
4. Set `MAIL_FROM` to an address on your verified domain.

When these variables are set, users can sign in via magic link emails. Without
them, password authentication is still fully available.

### Password Authentication (Alternative to Magic Links)

Password authentication is **always available**, even without an email provider.
Users can register and log in with email + password:

```
POST /v1/auth/register
{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "name": "Jane Doe"
}

POST /v1/auth/login
{
    "email": "user@example.com",
    "password": "SecurePassword123!"
}
```

Email verification (the confirmation link sent after registration) requires
`RESEND_API_KEY` to be configured. Without it, accounts are created but
unverified. You can auto-verify accounts via the admin panel or database.

### Billing (Optional, disabled by default)

Billing features are **completely optional**. OneBrain works without Stripe.
When no Stripe keys are configured:

- All users get the default free plan.
- Plan limits (memory count, API calls) are still enforced.
- The billing API returns plan info but payment endpoints are disabled.

To enable paid plans:

```bash
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_signing_secret
STRIPE_PRICE_PRO=price_your_pro_plan_price_id
STRIPE_PRICE_TEAM=price_your_team_plan_price_id
```

Only activates when `STRIPE_SECRET_KEY` is present.

### OAuth (Optional)

Social login providers can be enabled individually. Each requires its own
client ID and secret:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Apple Sign-In
APPLE_CLIENT_ID=your_apple_client_id
APPLE_CLIENT_SECRET=your_apple_client_secret

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

Each provider is enabled only when its `*_CLIENT_ID` is set. Users can link
multiple OAuth providers to a single account.

### Encryption (Recommended)

Memory content can be encrypted at rest using AES-256-GCM. TOTP secrets for
two-factor authentication are encrypted separately.

```bash
# 64-character hex string (32 bytes) for memory encryption
MEMORY_ENCRYPTION_KEY=your_64_char_hex_key_here

# 64-character hex string (32 bytes) for TOTP secret encryption
TOTP_ENCRYPTION_KEY=your_64_char_hex_key_here
```

Generate keys with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Or with OpenSSL:

```bash
openssl rand -hex 32
```

When `MEMORY_ENCRYPTION_KEY` is set, all new memory content is encrypted before
writing to the database. Existing unencrypted memories are encrypted on next
update. Without this key, memories are stored in plaintext.

### Full Environment Variable Reference

| Variable                  | Required | Default                              | Description                            |
|--------------------------|----------|--------------------------------------|----------------------------------------|
| `DATABASE_URL`           | Yes      | —                                    | PostgreSQL connection string           |
| `JWT_SECRET`             | Yes      | —                                    | Secret for signing JWT tokens (32+ chars) |
| `PORT`                   | No       | `3000`                               | HTTP server port                       |
| `NODE_ENV`               | No       | `production`                         | Environment (`development`/`production`) |
| `CORS_ORIGINS`           | No       | `https://onebrain.rocks`             | Comma-separated allowed origins        |
| `RESEND_API_KEY`         | No       | —                                    | Resend API key for magic link emails   |
| `MAIL_FROM`              | No       | `noreply@onebrain.rocks`             | Sender email address                   |
| `STRIPE_SECRET_KEY`      | No       | —                                    | Stripe secret key (enables billing)    |
| `STRIPE_WEBHOOK_SECRET`  | No       | —                                    | Stripe webhook signing secret          |
| `STRIPE_PRICE_PRO`       | No       | —                                    | Stripe price ID for Pro plan           |
| `STRIPE_PRICE_TEAM`      | No       | —                                    | Stripe price ID for Team plan          |
| `GOOGLE_CLIENT_ID`       | No       | —                                    | Google OAuth client ID                 |
| `GOOGLE_CLIENT_SECRET`   | No       | —                                    | Google OAuth client secret             |
| `APPLE_CLIENT_ID`        | No       | —                                    | Apple Sign-In client ID                |
| `APPLE_CLIENT_SECRET`    | No       | —                                    | Apple Sign-In client secret            |
| `GITHUB_CLIENT_ID`       | No       | —                                    | GitHub OAuth client ID                 |
| `GITHUB_CLIENT_SECRET`   | No       | —                                    | GitHub OAuth client secret             |
| `MEMORY_ENCRYPTION_KEY`  | No       | —                                    | AES-256 key for memory encryption (hex) |
| `TOTP_ENCRYPTION_KEY`    | No       | —                                    | AES-256 key for TOTP encryption (hex)  |
| `RATE_LIMIT_WINDOW`      | No       | `60`                                 | Rate limit window in seconds           |
| `RATE_LIMIT_MAX`         | No       | `600`                                | Max requests per window (authenticated) |
| `RATE_LIMIT_WRITE_MAX`   | No       | `30`                                 | Max write requests per window          |
| `LOG_LEVEL`              | No       | `info`                               | Log level (`debug`/`info`/`warn`/`error`) |

---

## Security Notes

- **API key hashing:** API keys are hashed with SHA-256 before storage. Only
  the key prefix (e.g., `ob_abc`) is stored in plaintext for identification.
  The full key is shown once at creation and cannot be recovered.

- **Memory encryption:** When `MEMORY_ENCRYPTION_KEY` is configured, memory
  content is encrypted at rest using AES-256-GCM with per-record random IVs.

- **Rate limiting:** Default limits are 600 requests/minute for authenticated
  endpoints and 30 requests/minute for write operations. The SDK respects
  `Retry-After` headers automatically when `max_retries > 0`.

- **CORS:** The server validates `Origin` headers against a configured
  allowlist. Wildcard origins (`*`) are never permitted in production.

- **Cookies:** Authentication cookies are `httpOnly`, `Secure`, `SameSite=Lax`.
  CSRF protection is enforced on all state-changing endpoints.

- **Transport:** All communication uses HTTPS/TLS 1.2+. The SDK verifies
  server certificates by default (do not disable in production).

---

## Development

### Setup

```bash
git clone https://github.com/azappnew/onebrain-python.git
cd onebrain-python
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
# Unit tests
pytest

# With coverage
coverage run -m pytest
coverage report

# Skip integration tests
pytest -m "not integration"
```

### Type Checking

```bash
mypy src/
```

### Linting

```bash
ruff check src/ tests/
ruff format src/ tests/
```

---

## Versioning

This SDK follows [Semantic Versioning](https://semver.org/):

- **MAJOR** — breaking API changes
- **MINOR** — new features, backward-compatible
- **PATCH** — bug fixes, backward-compatible

---

## License

MIT License. See [LICENSE](LICENSE) for details.

Copyright (c) 2026 AZapp One.
