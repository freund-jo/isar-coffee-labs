"""One-time setup for the Isar Coffee labs.

Run it in a terminal, in the repo folder:

    python setup_labs.py        (Windows: py setup_labs.py)

It creates a Python environment in .venv, installs the packages, registers the notebook
kernel, asks for your key (saved in .env, never shown) and checks the connection.
Running it again is safe.

Options:
    --check-tls    only test certificates and save the result (for company networks)
    --no-install   skip creating the environment and installing packages
"""

from __future__ import annotations

import getpass
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
VENV = ROOT / ".venv"
ENV_FILE = ROOT / ".env"
KERNEL_NAME = "isar-coffee-labs"
KERNEL_LABEL = "Isar Coffee Labs (.venv)"
WINDOWS = os.name == "nt"


def say(text: str = "") -> None:
    print(text, flush=True)


def step(n: int, text: str) -> None:
    say(f"\n[{n}/5] {text}")


def venv_python() -> pathlib.Path:
    return VENV / ("Scripts/python.exe" if WINDOWS else "bin/python")


# ── .env handling (no extra packages needed) ────────────────────────────────

def read_env() -> dict:
    values = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"')
    return values


def write_env(values: dict) -> None:
    lines = ["# Isar Coffee Labs – your credentials. Keep this file private.", ""]
    for key, value in values.items():
        if value:
            lines.append(f'{key}="{value}"')
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def has_credentials(values: dict) -> bool:
    return bool(values.get("ANTHROPIC_API_KEY") or values.get("LABS_GATEWAY_URL"))


# ── Steps ────────────────────────────────────────────────────────────────────

def check_location() -> None:
    path = str(ROOT).lower()
    for word in ("onedrive", "dropbox", "icloud", "mobile documents", "google drive"):
        if word in path:
            say(f"  ! This folder is inside a cloud-sync folder ({word}).")
            say("    Syncing can break the Python environment and may upload your key.")
            say("    Better: move the folder somewhere local, e.g. C:\\dev\\ or ~/projects/, and run this again.")
            if input("    Continue anyway? [y/N] ").strip().lower() != "y":
                sys.exit(1)
            return
    say("  ok – local folder")


def check_python() -> None:
    if sys.version_info < (3, 10):
        say(f"  ✗ Python {sys.version.split()[0]} is too old. Please install Python 3.10 or newer.")
        sys.exit(1)
    say(f"  ok – Python {sys.version.split()[0]}")


def install() -> None:
    if not venv_python().exists():
        say("  creating .venv ...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    say("  installing packages (this can take a minute) ...")
    py = str(venv_python())
    subprocess.run([py, "-m", "pip", "install", "--quiet", "--upgrade", "pip"], check=False)
    result = subprocess.run([py, "-m", "pip", "install", "--quiet", "-r", str(ROOT / "requirements.txt")])
    if result.returncode != 0:
        say("  ✗ Package installation failed.")
        say("    On a company network, try:  " + py + " -m pip install --use-feature=truststore -r requirements.txt")
        sys.exit(1)
    subprocess.run([py, "-m", "ipykernel", "install", "--user", "--name", KERNEL_NAME,
                    "--display-name", KERNEL_LABEL], check=True, capture_output=True)
    say(f"  ok – packages installed, kernel “{KERNEL_LABEL}” registered")


def ask_credentials(values: dict) -> dict:
    if has_credentials(values):
        say("  ok – credentials found in .env (delete .env to start over)")
        return values
    if not sys.stdin.isatty():
        say("  ✗ No credentials in .env and no terminal to ask in.")
        say("    Run this script yourself in a terminal: python setup_labs.py")
        sys.exit(1)
    say("  How do you connect to Claude?")
    say("    1  My own Anthropic API key (console.anthropic.com)")
    say("    2  A company AI gateway")
    choice = input("  Choose 1 or 2 [1]: ").strip() or "1"
    if choice == "2":
        values["LABS_GATEWAY_URL"] = input("  Gateway URL: ").strip()
        command = input("  Command that prints a key (leave empty to paste a fixed key): ").strip()
        if command:
            values["LABS_GATEWAY_KEY_COMMAND"] = command
        else:
            values["LABS_GATEWAY_KEY"] = getpass.getpass("  Gateway key (hidden while you type): ").strip()
        values["LABS_GATEWAY_HEADERS"] = input("  Extra headers, e.g. 'x-team-id: 123' (optional): ").strip()
        values["LABS_MODEL_PREFIX"] = input("  Model name prefix, e.g. 'bedrock.anthropic.' (optional): ").strip()
    else:
        key = getpass.getpass("  Paste your API key (hidden while you type): ").strip()
        if not key.startswith("sk-ant-"):
            say("  ! That doesn't look like an Anthropic API key (they start with sk-ant-). Saved anyway.")
        values["ANTHROPIC_API_KEY"] = key
    write_env(values)
    say("  ok – saved to .env")
    return values


def test_connection() -> bool:
    code = "import labs_common; labs_common.connect()"
    result = subprocess.run([str(venv_python()), "-c", code], cwd=ROOT, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        say("  " + output.splitlines()[0])
        return True
    lines = [l for l in output.splitlines() if l.strip() and not l.startswith("Traceback")]
    for line in lines[-4:]:
        say("  " + line)
    return False


def check_tls(values: dict) -> dict:
    """If the default certificates fail, try the operating system's certificate store."""
    values.pop("LABS_TLS", None)
    write_env(values)
    if test_connection():
        say("  ok – default certificates work")
        return values
    say("  trying the operating system's certificate store ...")
    values["LABS_TLS"] = "system"
    write_env(values)
    if test_connection():
        say("  ok – the system certificate store works, saved LABS_TLS=system in .env")
        return values
    say("  ✗ Still no connection. Check the messages above, or ask your IT team about proxies.")
    return values


def main() -> None:
    args = set(sys.argv[1:])
    say("Isar Coffee Labs – setup")

    if "--check-tls" in args:
        check_tls(read_env())
        return

    step(1, "Checking the folder")
    check_location()
    step(2, "Checking Python")
    check_python()
    step(3, "Installing packages")
    if "--no-install" in args:
        say("  skipped")
    else:
        install()
    step(4, "Credentials")
    values = ask_credentials(read_env())
    step(5, "Testing the connection")
    if not test_connection():
        say("  Testing again with the system certificate store ...")
        values = check_tls(values)

    say("\nYou're all set. Open 01_eval/Eval.ipynb, pick the kernel “Isar Coffee Labs (.venv)” and run the first cell.")


if __name__ == "__main__":
    main()
