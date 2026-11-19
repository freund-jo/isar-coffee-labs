"""Shared helpers for the Isar Coffee labs.

Every notebook starts with:

    from labs_common import connect
    lab = connect()

`connect()` reads your credentials from the .env file in the repo root, makes one tiny test
call and shows a green banner if everything works. You don't need to read this file to do
the labs.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
from dataclasses import dataclass

REPO_ROOT = pathlib.Path(__file__).resolve().parent
ENV_FILE = REPO_ROOT / ".env"

# Model names on the Anthropic API. A gateway may need a prefix (LABS_MODEL_PREFIX).
BASE_MODELS = {
    "haiku": "claude-haiku-5-5",
    "sonnet": "claude-sonnet-5-5",
    "opus": "claude-opus-5-5",
}

# List prices in US$ per million tokens (Anthropic API, November 2026).
# Check https://www.anthropic.com/pricing before you quote them anywhere.
# Cache writes cost 1.25x the input price, cache reads a fraction of it.
PRICES = {
    "haiku": {"input": 0.10, "output": 0.50, "cache_read": 0.010},
    "sonnet": {"input": 2.00, "output": 10.00, "cache_read": 0.10},
    "opus": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
}
CACHE_WRITE_FACTOR = 1.25


# ── Small helpers ────────────────────────────────────────────────────────────

def _in_notebook() -> bool:
    try:
        from IPython import get_ipython
        shell = get_ipython()
        return shell is not None and shell.__class__.__name__ == "ZMQInteractiveShell"
    except Exception:
        return False


def _banner(ok: bool, title: str, lines: list[str]) -> None:
    if _in_notebook():
        from IPython.display import HTML, display
        colour = "#2e7d32" if ok else "#c62828"
        body = "<br>".join(lines)
        display(HTML(
            f'<div style="border-left:6px solid {colour};padding:8px 14px;'
            f'background:{colour}14;font-family:sans-serif;font-size:14px;">'
            f'<b style="color:{colour}">{title}</b><br>{body}</div>'))
    else:
        mark = "✓" if ok else "✗"
        print(f"{mark} {title}")
        for line in lines:
            print(f"  {line}")


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(ENV_FILE, override=True)


def _gateway_headers() -> dict:
    raw = os.environ.get("LABS_GATEWAY_HEADERS", "")
    headers = {}
    for part in raw.split(";"):
        if ":" in part:
            name, value = part.split(":", 1)
            headers[name.strip()] = value.strip()
    return headers


def _gateway_key() -> str:
    command = os.environ.get("LABS_GATEWAY_KEY_COMMAND", "").strip()
    if command:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode != 0 or not result.stdout.strip():
            raise RuntimeError("LABS_GATEWAY_KEY_COMMAND did not print a key.")
        return result.stdout.strip()
    return os.environ.get("LABS_GATEWAY_KEY", "").strip()


def _use_system_certificates() -> None:
    if os.environ.get("LABS_TLS", "").strip().lower() == "system":
        import truststore
        truststore.inject_into_ssl()


# ── The connection object ────────────────────────────────────────────────────

@dataclass
class Lab:
    """What connect() gives you: a client and the model names."""
    client: object
    mode: str            # "anthropic" or "gateway"
    HAIKU: str
    SONNET: str
    OPUS: str
    batch_available: bool

    def make_client(self, timeout: float = 600.0, max_retries: int = 2):
        """A client with a longer timeout, for long-running cells."""
        return _make_client(timeout=timeout, max_retries=max_retries)

    def tier(self, model: str) -> str:
        """'haiku', 'sonnet' or 'opus' for a full model name."""
        for name in BASE_MODELS:
            if name in model:
                return name
        raise ValueError(f"Unknown model: {model}")

    def cost(self, model: str, usage) -> float:
        """Cost of one API call in US$, including cache writes and reads."""
        p = PRICES[self.tier(model)]
        cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
        cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
        return (
            usage.input_tokens * p["input"]
            + cache_write * p["input"] * CACHE_WRITE_FACTOR
            + cache_read * p["cache_read"]
            + usage.output_tokens * p["output"]
        ) / 1_000_000


def _make_client(timeout: float = 120.0, max_retries: int = 2):
    import anthropic
    if os.environ.get("LABS_GATEWAY_URL", "").strip():
        return anthropic.Anthropic(
            base_url=os.environ["LABS_GATEWAY_URL"].strip(),
            api_key=_gateway_key(),
            default_headers=_gateway_headers(),
            timeout=timeout,
            max_retries=max_retries,
        )
    return anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY", "").strip(),
        timeout=timeout,
        max_retries=max_retries,
    )


def _diagnose(error: Exception) -> list[str]:
    text = f"{type(error).__name__}: {error}"
    if "CERTIFICATE" in text.upper() or "SSL" in text.upper():
        return ["Your network blocks the connection with its own certificates.",
                "Fix: in a terminal in the repo folder, run  python setup_labs.py --check-tls",
                "Then run this cell again."]
    if "401" in text or "authentication" in text.lower():
        return ["The key was rejected.",
                "Fix: run  python setup_labs.py  again and enter a valid key."]
    if "404" in text and "model" in text.lower():
        return ["The model name was not found.",
                "If you use a gateway, check LABS_MODEL_PREFIX in .env."]
    if "credit" in text.lower() or "billing" in text.lower():
        return ["Your account has no credit left.",
                "Fix: add credit in the Anthropic Console (Billing)."]
    return [text[:300]]


def connect(check: bool = True) -> Lab:
    """Read .env, create a client, make one tiny test call and show the result."""
    try:
        import anthropic  # noqa: F401
        import dotenv  # noqa: F401
    except ImportError:
        _banner(False, "Packages missing",
                ["Run  python setup_labs.py  once in a terminal in the repo folder.",
                 "Then pick the kernel “Isar Coffee Labs (.venv)” at the top right and run this cell again."])
        raise SystemExit("Setup needed – see the message above.")

    _load_env()
    _use_system_certificates()

    gateway = bool(os.environ.get("LABS_GATEWAY_URL", "").strip())
    if not gateway and not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        _banner(False, "No credentials found",
                ["Run  python setup_labs.py  in a terminal in the repo folder.",
                 "It asks for your key and saves it in .env. Never paste a key into a notebook cell."])
        raise SystemExit("Credentials needed – see the message above.")

    prefix = os.environ.get("LABS_MODEL_PREFIX", "").strip() if gateway else ""
    names = {k: prefix + v for k, v in BASE_MODELS.items()}

    try:
        client = _make_client()
    except Exception as e:
        _banner(False, "Could not create the client", _diagnose(e))
        raise SystemExit("Connection failed – see the message above.")

    lab = Lab(client=client, mode="gateway" if gateway else "anthropic",
              HAIKU=names["haiku"], SONNET=names["sonnet"], OPUS=names["opus"],
              batch_available=not gateway)

    if check:
        try:
            client.messages.create(model=lab.HAIKU, max_tokens=5,
                                   messages=[{"role": "user", "content": "Say OK."}])
        except Exception as e:
            _banner(False, "Connection test failed", _diagnose(e))
            raise SystemExit("Connection failed – see the message above.")
        where = "company gateway" if gateway else "Anthropic API"
        _banner(True, "Connected", [f"via {where} · models: {lab.HAIKU}, {lab.SONNET}, {lab.OPUS}"])
    return lab


if __name__ == "__main__":
    connect()
    sys.exit(0)
