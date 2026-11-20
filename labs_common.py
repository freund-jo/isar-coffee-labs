"""Connection helper for the Isar Coffee labs.

You don't need to read or change this file to do the labs. It does the plumbing, so the notebooks
can stay about evals and inference.

How the notebooks use it – the first cell of each lab runs:

    from labs_common import connect
    lab = connect()                      # read the key, test it, show a green or red box
    client = lab.make_client()           # the client the lab uses for its API calls

What `lab` gives you:

    lab.HAIKU, lab.SONNET, lab.OPUS      the model names to pass as model=...
    lab.make_client(...)                 a client for the lab's calls (longer timeout)
    lab.cost(model, usage)               what one API call cost, in US$

Where the settings come from: the file .env in the repo folder. setup_labs.py writes it for you.

    ANTHROPIC_API_KEY     your key (an Anthropic key, or a key from a company AI gateway)
    ANTHROPIC_BASE_URL    only for a gateway: its address
    LABS_MODEL_PREFIX     only for a gateway, optional: text in front of the model names
    LABS_TLS              "system" if your network needs the computer's own certificate store
"""

import os
import pathlib
from dataclasses import dataclass

REPO_ROOT = pathlib.Path(__file__).resolve().parent
ENV_FILE = REPO_ROOT / ".env"

# The three models used in the labs, from smallest and cheapest to largest.
MODELS = {
    "haiku": "claude-haiku-5-5",
    "sonnet": "claude-sonnet-5-5",
    "opus": "claude-opus-5-5",
}

# List prices in US$ per million tokens (Anthropic API, November 2026).
# "cache_read" is the price for tokens read back from the prompt cache.
# Writing tokens into the cache costs the input price × CACHE_WRITE_FACTOR.
PRICES = {
    "haiku": {"input": 0.10, "output": 0.50, "cache_read": 0.010},
    "sonnet": {"input": 2.00, "output": 10.00, "cache_read": 0.10},
    "opus": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
}
CACHE_WRITE_FACTOR = 1.25

SETUP_HINT = "In a terminal in the repo folder, run:  python3 setup_labs.py   (Windows: py setup_labs.py)"


# ── Messages for the person in front of the screen ──────────────────────────

def _show(ok, title, lines):
    """Show a result: a green or red box in a notebook, plain text with ✓ / ✗ in a terminal."""
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
    """Turn a connection error into plain words: what went wrong and how to fix it."""
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


# ── Creating the client ──────────────────────────────────────────────────────

def _new_client(timeout):
    """An Anthropic client with the key from .env – and the gateway address, if there is one."""
    import anthropic
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "").strip() or None
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"].strip(), base_url=base_url, timeout=timeout)


def _switch_off_haiku_thinking(client):
    """Make every Haiku call on this client run without thinking (unless the call sets thinking itself).

    Used in Lab 2, where Haiku is meant to be the fastest and cheapest option. Calls to Sonnet and
    Opus are passed through unchanged.
    """
    for name in ("create", "stream"):
        original = getattr(client.messages, name)

        def wrapped(*args, _original=original, **kwargs):
            if MODELS["haiku"] in str(kwargs.get("model", "")) and "thinking" not in kwargs:
                kwargs["thinking"] = {"type": "disabled"}
            return _original(*args, **kwargs)

        setattr(client.messages, name, wrapped)


def _gateway_prefix(client):
    """Find out how a company gateway names the models.

    Some gateways put text in front of the model names, e.g. 'bedrock.anthropic.claude-haiku-5-5'.
    This asks the gateway for its model list and returns that text ('' if the names are unchanged).
    LABS_MODEL_PREFIX in .env overrides the search.
    """
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


# ── What connect() gives you ─────────────────────────────────────────────────

@dataclass
class Lab:
    """The result of connect(): the model names to use, plus two helpers."""
    client: object            # the client used for the connection test
    HAIKU: str                # full model names – pass them as model=lab.HAIKU etc.
    SONNET: str
    OPUS: str
    via_gateway: bool = False  # True if the key goes through a company gateway (no Batch API there)

    def make_client(self, timeout=600.0, haiku_thinks=True):
        """The client a lab uses for its API calls.

        timeout:       how long one call may take, in seconds (long answers can take a while).
        haiku_thinks:  False = every call to Haiku runs without thinking – the fastest and cheapest
                       setting. Lab 2 uses this. Sonnet and Opus are not affected.
        """
        client = _new_client(timeout)
        if not haiku_thinks:
            _switch_off_haiku_thinking(client)
        return client

    def cost(self, model, usage):
        """What one API call cost in US$: input, output, cache writes and cache reads.

        model:  the model name used for the call (e.g. lab.SONNET)
        usage:  response.usage from that call
        """
        tier = next(name for name in MODELS if name in model)
        p = PRICES[tier]
        write = getattr(usage, "cache_creation_input_tokens", 0) or 0
        read = getattr(usage, "cache_read_input_tokens", 0) or 0
        return (usage.input_tokens * p["input"] + write * p["input"] * CACHE_WRITE_FACTOR
                + read * p["cache_read"] + usage.output_tokens * p["output"]) / 1_000_000


def connect():
    """Check that everything is ready and return a Lab.

    1. Are the packages installed? If not: say how to run the setup.
    2. Read the key (and gateway address, if any) from .env.
    3. Make one tiny test call to Haiku.
    4. Show a green box – or a red one that says what to fix – and stop the cell if it failed.
    """
    try:
        import anthropic  # noqa: F401  (only checks that the package is installed)
        from dotenv import load_dotenv
    except ImportError:
        _show(False, "Setup not done yet",
              [SETUP_HINT, "Then pick the kernel “Isar Coffee Labs (.venv)” at the top right and run this cell again."])
        raise SystemExit("Setup needed – see the message above.")

    load_dotenv(ENV_FILE, override=True)
    if os.environ.get("LABS_TLS", "").strip() == "system":
        import truststore
        truststore.inject_into_ssl()      # use the computer's certificate store (company networks)

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
    # `python labs_common.py` runs only the connection test – handy to check a key from the terminal.
    connect()
