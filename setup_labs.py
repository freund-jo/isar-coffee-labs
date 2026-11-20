"""One-time setup for the Isar Coffee labs.

Open a terminal in this folder and run:

    python3 setup_labs.py      (Mac)
    py setup_labs.py           (Windows)

What it does, step by step:

    1. Warns if the folder is inside OneDrive, Dropbox or iCloud (syncing breaks the setup).
    2. Checks that Python is 3.10 or newer.
    3. Creates a private Python environment in the folder .venv and installs the packages the labs
       need. It also registers the notebook kernel "Isar Coffee Labs (.venv)".
    4. Asks for your API key – an Anthropic key, or a key from a company AI gateway plus its
       address – saves it in .env and tests it. On company networks that replace certificates it
       switches to the computer's own certificate store by itself.

Running it again is safe: it keeps a working key and only asks again if the key doesn't work.

Option:
    --check-tls   only test the connection and fix certificate problems (asks nothing)

Nothing outside this folder is changed, except the registered notebook kernel.
"""

import getpass
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
VENV = ROOT / ".venv"
ENV_FILE = ROOT / ".env"
PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PACKAGES = ["anthropic>=2.4", "python-dotenv>=1.0", "truststore>=0.9", "matplotlib>=3.8", "ipykernel>=6.29"]
KERNEL = ("isar-coffee-labs", "Isar Coffee Labs (.venv)")


def say(text=""):
    """Print a line straight away (so the output appears even while something slow runs)."""
    print(text, flush=True)


def read_env():
    """The settings saved in .env, as a dictionary (empty if there is no .env yet)."""
    values = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip().strip('"')
    return values


def write_env(values):
    """Save the settings to .env. Empty values are left out."""
    lines = ["# Your API key. Keep this file private – never share or commit it."]
    lines += [f'{k}="{v}"' for k, v in values.items() if v]
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_key():
    """Run the connection test from labs_common inside .venv.

    Returns (ok, lines): ok is True if the test call worked; lines is the message it printed,
    without the Python error details.
    """
    result = subprocess.run([str(PYTHON), "-c", "import labs_common; labs_common.connect()"],
                            cwd=ROOT, capture_output=True, text=True)
    lines = [l.strip() for l in (result.stdout + result.stderr).splitlines()
             if l.strip() and not l.startswith(("Traceback", "  File", "SystemExit", "    "))
             and "see the message above" not in l]
    return result.returncode == 0, lines


def reason(lines):
    """From the test message, the one line that says what went wrong.

    The fix line ("run setup_labs.py") is left out – we are already in the setup.
    """
    return lines[1] if len(lines) > 1 else " ".join(lines)


def fix_certificates(values):
    """Try again with the computer's own certificate store (LABS_TLS=system in .env).

    Company networks often check HTTPS traffic with their own certificates, which Python doesn't
    know. The computer's certificate store does. If that doesn't help either, the setting is removed again.
    """
    values["LABS_TLS"] = "system"
    write_env(values)
    ok, lines = test_key()
    if not ok:
        values.pop("LABS_TLS")
        write_env(values)
    return ok, lines


def main():
    """The four setup steps (see the top of this file)."""
    say("Isar Coffee Labs – setup\n")

    if "--check-tls" in sys.argv:
        values = read_env()
        ok, lines = test_key()
        if not ok and any("certificate" in l.lower() or "connection" in l.lower() for l in lines):
            ok, lines = fix_certificates(values)
        say("\n".join(lines))
        return

    # 1. Folder
    if any(w in str(ROOT).lower() for w in ("onedrive", "dropbox", "icloud", "mobile documents")):
        say("! This folder is inside OneDrive, Dropbox or iCloud. Syncing breaks the setup and")
        say("  would upload your key. Move the folder somewhere local (e.g. C:\\dev or ~/projects)")
        say("  and run this again.")
        if input("  Continue anyway? [y/N] ").strip().lower() != "y":
            sys.exit(1)

    # 2. Python
    if sys.version_info < (3, 10):
        say(f"✗ Python {sys.version.split()[0]} is too old. Install Python 3.10 or newer from python.org.")
        sys.exit(1)
    say(f"✓ Python {sys.version.split()[0]}")

    # 3. Packages
    if not PYTHON.exists():
        say("  Creating the environment ...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    say("  Installing packages (about a minute) ...")
    subprocess.run([str(PYTHON), "-m", "pip", "install", "-q", "--upgrade", "pip"], capture_output=True)
    pip = subprocess.run([str(PYTHON), "-m", "pip", "install", "-q", *PACKAGES])
    if pip.returncode != 0:
        say("  Trying again with the system certificate store (company networks) ...")
        pip = subprocess.run([str(PYTHON), "-m", "pip", "install", "-q", "--use-feature=truststore", *PACKAGES])
    if pip.returncode != 0:
        say("✗ Installing the packages failed. Check your internet connection and run this again.")
        sys.exit(1)
    subprocess.run([str(PYTHON), "-m", "ipykernel", "install", "--user", "--name", KERNEL[0],
                    "--display-name", KERNEL[1]], capture_output=True, check=True)
    say("✓ Packages installed")

    # 4. API key – keep a saved key if it works, otherwise ask for one
    values = read_env()
    if values.get("ANTHROPIC_API_KEY"):
        ok, lines = test_key()
        if not ok and any("certificate" in l.lower() for l in lines):
            ok, lines = fix_certificates(values)
        if ok:
            say("✓ API key found and working\n")
            say("All set. Open 01_eval/Eval.ipynb in VS Code and pick the kernel “Isar Coffee Labs (.venv)”.")
            return
        say("! The saved key doesn't work: " + reason(lines))

    if not sys.stdin.isatty():
        say("✗ The API key has to be typed in a terminal. Run this script yourself: python3 setup_labs.py")
        sys.exit(1)

    while True:
        say("\nPaste your API key and press Enter. (You won't see it while you type.)")
        key = getpass.getpass("API key: ").strip()
        if not key.startswith("sk-"):
            say("✗ That doesn't look like an API key – keys start with sk-. Try again.")
            continue
        values = {"ANTHROPIC_API_KEY": key, "LABS_TLS": values.get("LABS_TLS", "")}
        if not key.startswith("sk-ant-"):
            say("\nThis is not an Anthropic key, so it's probably from a company AI gateway.")
            say("Enter the gateway address you got with the key, e.g. https://ai-gateway.example.com")
            url = input("Gateway address: ").strip().rstrip("/")
            values["ANTHROPIC_BASE_URL"] = url.removesuffix("/v1")
        write_env(values)
        ok, lines = test_key()
        if not ok and any("certificate" in l.lower() for l in lines):
            say("  Your network replaces certificates – switching to the system certificate store ...")
            ok, lines = fix_certificates(values)
        if ok:
            break
        say("✗ " + reason(lines))
        if input("Try another key? [Y/n] ").strip().lower() == "n":
            sys.exit(1)

    say("✓ API key saved and working\n")
    say("All set. Open 01_eval/Eval.ipynb in VS Code and pick the kernel “Isar Coffee Labs (.venv)”.")


if __name__ == "__main__":
    main()
