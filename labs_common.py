"""Shared helper for the Isar Coffee labs. You don't need to read this file.

Every notebook starts with:

    from labs_common import connect
    lab = connect()

connect() reads your API key from the .env file, makes one tiny test call and shows a
green box if everything works.
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
    if "connect" in text.lower():
        return ["No connection to the Anthropic API. Are you online? Behind a company proxy?",
                "Try: python3 setup_labs.py --check-tls"]
    return [text[:300]]


@dataclass
class Lab:
    """What connect() gives you: a client and the model names."""
    client: object
    HAIKU: str
    SONNET: str
    OPUS: str

    def make_client(self, timeout=600.0):
        """A client with a longer timeout, for long-running cells."""
        import anthropic
        return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=timeout)

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

    client = anthropic.Anthropic(api_key=key, timeout=120.0)
    lab = Lab(client=client, HAIKU=MODELS["haiku"], SONNET=MODELS["sonnet"], OPUS=MODELS["opus"])
    try:
        client.messages.create(model=lab.HAIKU, max_tokens=5, messages=[{"role": "user", "content": "Say OK."}])
    except Exception as e:
        _show(False, "Connection test failed", _why(e))
        raise SystemExit("Connection failed – see the message above.")
    _show(True, "Connected", ["Your API key works. You're ready to go."])
    return lab


if __name__ == "__main__":
    connect()
