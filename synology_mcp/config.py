"""Configuration for the Synology MCP server.

All settings come from environment variables, optionally seeded from a local
``.env`` file. No credentials are ever hard-coded.
"""

from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv() -> None:
    """Seed os.environ from the first ``.env`` found (cwd, then package parent).

    A tiny loader so the project has no hard dependency on python-dotenv.
    Existing real environment variables always win (``setdefault``).
    """
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ]
    for env_path in candidates:
        if not env_path.exists():
            continue
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        break


_load_dotenv()


def _flag(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# ── Connection ───────────────────────────────────────────────────────────────
URL: str = os.getenv("SYNOLOGY_URL", "http://localhost:5000").rstrip("/")
USER: str = os.getenv("SYNOLOGY_USER", "")
PASSWORD: str = os.getenv("SYNOLOGY_PASS", "")

# ── Two-factor auth ────────────────────────────────────────────────────────────
# OTP_CODE is only for the one-time bootstrap; DEVICE_ID is the persistent token
# that lets the server log in without a fresh OTP on every start.
OTP_CODE: str = os.getenv("SYNOLOGY_OTP", "")
DEVICE_ID: str = os.getenv("SYNOLOGY_DEVICE_ID", "")

# ── Behaviour ──────────────────────────────────────────────────────────────────
VERIFY_SSL: bool = _flag("SYNOLOGY_VERIFY_SSL", False)
TIMEOUT: float = float(os.getenv("SYNOLOGY_TIMEOUT", "30"))
# DSM resolves ``session`` against its list of installed applications and then
# checks the account's privilege for it. An arbitrary name is not a real app, so
# DSM rejects the login with error 402 for any non-administrator account.
# Default to empty, which omits the parameter and lets DSM use a plain session.
SESSION_NAME: str = os.getenv("SYNOLOGY_SESSION_NAME", "")
DEVICE_NAME: str = os.getenv("SYNOLOGY_DEVICE_NAME", "SynologyMCP")

# Irreversible data operations (deleting files / shared folders) and outward-facing
# ones (creating public share links) are not even registered as tools unless this
# is explicitly turned on. See app.destructive_tool.
ENABLE_DESTRUCTIVE: bool = _flag("SYNOLOGY_ENABLE_DESTRUCTIVE", False)

# Destructive power operations (reboot / shutdown / install DSM update) are
# disabled unless this is explicitly turned on.
ENABLE_POWER_CONTROL: bool = _flag("SYNOLOGY_ENABLE_POWER_CONTROL", False)


def validate() -> None:
    """Raise a helpful error if the minimum required settings are missing."""
    missing = [
        name
        for name, value in (("SYNOLOGY_USER", USER), ("SYNOLOGY_PASS", PASSWORD))
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill it in."
        )
