"""Shared helper for the Isar Coffee labs. You don't need to read this file.

Every notebook starts with:

    from labs_common import connect
    lab = connect()

connect() reads your API key from the .env file, makes one tiny test call and shows a
green box if everything works. It works with an Anthropic API key, or with a key from a
company AI gateway (then .env also holds the gateway address in ANTHROPIC_BASE_URL).
"""

import os
import pathlib
from dataclasses import dataclass

REPO_ROOT = pathlib.Path(__file__).resolve().parent
ENV_FILE = REPO_ROOT / ".env"

MODELS = {
    "haiku": "claude-haiku-5-5",
    "sonnet": "claude-sonnet-5-5",
    "opus": "claude-opus-5-5",
}

# List prices in US$ per million tokens (Anthropic API, November 2026).
# Cache writes cost 1.25x the input price.
PRICES = {
    "haiku": {"input": 0.10, "output": 0.50, "cache_read": 0.010},
    "sonnet": {"input": 2.00, "output": 10.00, "cache_read": 0.10},
    "opus": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
}
CACHE_WRITE_FACTOR = 1.25

SETUP_HINT = "In a terminal in the repo folder, run:  python3 setup_labs.py   (Windows: py setup_labs.py)"


def _show(ok, title, lines):
    try:
        from IPython import get_ipython
        in_notebook = get_ipython().__class__.__name__ == "ZMQInteractiveShell"
    except Exception:
        in_notebook = False
    if in_notebook:
        from IPython.display import HTML, display
        colour = "#2e7d32" if ok else "#c62828"
        display(HTML(
            f'<div style="border-left:6px solid {colour};padding:8px 14px;background:{colour}14;'
            f'font-family:sans-serif;font-size:14px;"><b style="color:{colour}">{title}</b><br>'
            + "<br>".join(lines) + "</div>"))
    else:
        print(("✓ " if ok else "✗ ") + title)
        for line in lines:
            print("  " + line)


def _why(error):
    text = f"{type(error).__name__}: {error}"
    if "CERTIFICATE" in text.upper() or "SSL" in text.upper():
        return ["Your network blocks the connection with its own certificates.",
                "Fix: in a terminal in the repo folder, run  python3 setup_labs.py --check-tls",
                "(Windows: py setup_labs.py --check-tls), then run this cell again."]
    if "401" in text or "authentication" in text.lower():
        return ["Your API key was rejected.", "Fix: " + SETUP_HINT + "  – it asks for a new key."]
    if "credit" in text.lower() or "billing" in text.lower():
        return ["Your account has no credit.", "Fix: add credit at console.anthropic.com → Billing."]
    if "doesn't offer the model" in text:
        return [str(error), "Ask your gateway team which Claude models your key can use."]
    if "connect" in text.lower():
        if os.environ.get("ANTHROPIC_BASE_URL"):
            return ["No connection to the gateway. Is the address in .env right? Do you need the company network or VPN?",
                    "To enter key and address again: " + SETUP_HINT]
        return ["No connection to the Anthropic API. Are you online? Behind a company proxy?",
                "Try: python3 setup_labs.py --check-tls"]
    return [text[:300]]


def _new_client(timeout):
    import anthropic
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "").strip() or None
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"].strip(), base_url=base_url, timeout=timeout)


def _gateway_prefix(client):
    """A gateway may name the models differently, e.g. 'bedrock.anthropic.claude-haiku-5-5'."""
    if os.environ.get("LABS_MODEL_PREFIX"):
        return os.environ["LABS_MODEL_PREFIX"].strip()
    ids = [m.id for m in client.models.list(limit=1000)]
    for prefix in ("", "bedrock.anthropic.", "anthropic."):
        if prefix + MODELS["haiku"] in ids:
            return prefix
    match = next((i for i in ids if i.endswith(MODELS["haiku"])), None)
    if match is None:
        raise RuntimeError(f"The gateway doesn't offer the model {MODELS['haiku']}.")
    return match[: -len(MODELS["haiku"])]


@dataclass
class Lab:
    """What connect() gives you: a client and the model names."""
    client: object
    HAIKU: str
    SONNET: str
    OPUS: str
    via_gateway: bool = False

    def make_client(self, timeout=600.0):
        """A client with a longer timeout, for long-running cells."""
        return _new_client(timeout)

    def cost(self, model, usage):
        """Cost of one API call in US$, including cache writes and reads."""
        tier = next(name for name in MODELS if name in model)
        p = PRICES[tier]
        write = getattr(usage, "cache_creation_input_tokens", 0) or 0
        read = getattr(usage, "cache_read_input_tokens", 0) or 0
        return (usage.input_tokens * p["input"] + write * p["input"] * CACHE_WRITE_FACTOR
                + read * p["cache_read"] + usage.output_tokens * p["output"]) / 1_000_000


def connect():
    """Read the key from .env, make one tiny test call and show the result."""
    try:
        import anthropic
        from dotenv import load_dotenv
    except ImportError:
        _show(False, "Setup not done yet",
              [SETUP_HINT, "Then pick the kernel “Isar Coffee Labs (.venv)” at the top right and run this cell again."])
        raise SystemExit("Setup needed – see the message above.")

    load_dotenv(ENV_FILE, override=True)
    if os.environ.get("LABS_TLS", "").strip() == "system":
        import truststore
        truststore.inject_into_ssl()

    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        _show(False, "No API key found", [SETUP_HINT, "Never paste a key into a notebook cell."])
        raise SystemExit("API key needed – see the message above.")

    gateway = bool(os.environ.get("ANTHROPIC_BASE_URL", "").strip())
    try:
        client = _new_client(120.0)
        prefix = _gateway_prefix(client) if gateway else ""
        lab = Lab(client=client, HAIKU=prefix + MODELS["haiku"], SONNET=prefix + MODELS["sonnet"],
                  OPUS=prefix + MODELS["opus"], via_gateway=gateway)
        client.messages.create(model=lab.HAIKU, max_tokens=5, messages=[{"role": "user", "content": "Say OK."}])
    except Exception as e:
        _show(False, "Connection test failed", _why(e))
        raise SystemExit("Connection failed – see the message above.")
    where = "your company's AI gateway" if gateway else "the Anthropic API"
    _show(True, "Connected", [f"Your key works with {where}. You're ready to go."])
    return lab


if __name__ == "__main__":
    connect()
