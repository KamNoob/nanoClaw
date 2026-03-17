# Security Review

Date: 2026-03-17

## Scope

Manual review focused on:
- Shell execution sandbox (`nanoclaw/security/sandbox.py`, `nanoclaw/tools/shell.py`)
- Workspace file access controls (`nanoclaw/tools/files.py`)
- Prompt-injection defenses (`nanoclaw/security/prompt_guard.py`)
- Web-fetch SSRF protections (`nanoclaw/tools/web.py`)
- Dashboard exposure and auth (`nanoclaw/dashboard/server.py`)

## Findings

### 1) High: New files were world-readable by default

`file_write` created files with mode `0644`, which allows local non-owner reads.
In a multi-user host this can leak workspace data.

Status: fixed in this review by switching to mode `0600`.

### 2) Medium: Dashboard API can run without authentication

If `dashboard.password` is not configured, `/api/*` routes are unauthenticated.
The service binds to `127.0.0.1`, which reduces exposure, but local-process access remains possible.

Recommendation:
- Require a password by default when dashboard is enabled, or
- Generate a random token at startup and print masked hint + one-time full token to TTY.

### 3) Medium: Shell sandbox is denylist-based

The shell sandbox has strong pattern blocking and confirm gates, but it is still regex denylist based.
This can be bypassed by novel command forms not covered by patterns.

Recommendation:
- Add an allowlist mode for common safe read-only commands (`ls`, `cat`, `pwd`, `git status`, etc.)
- Keep denylist as defense-in-depth for allowlisted commands with risky args.

## Positive controls observed

- Tool outputs are wrapped and injection-scanned before entering model context.
- File path validation prevents workspace traversal and symlink escapes are guarded with `O_NOFOLLOW`.
- Web fetch blocks private/loopback/link-local targets and redirect rechecks target host.
- Dashboard binds to localhost only.

## Validation commands run

- `rg "create_subprocess|subprocess\.|os\.system|popen\(|eval\(|exec\(" nanoclaw -n`
- `PYTHONPATH=. pytest -q tests/test_security.py tests/test_tools.py` (fails in this environment because `pytest-asyncio` plugin is unavailable)
