"""One-time setup for the Isar Coffee labs.

Open a terminal in this folder and run:

    python3 setup_labs.py      (Mac)
    py setup_labs.py           (Windows)

It installs everything into a local .venv folder, asks for your Anthropic API key, saves it in
.env and checks that it works. Running it again is safe.

    --check-tls   only fix certificate problems on company networks (asks nothing)
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
    print(text, flush=True)


def read_env():
    values = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip().strip('"')
    return values


def write_env(values):
    lines = ["# Your Anthropic API key. Keep this file private – never share or commit it."]
    lines += [f'{k}="{v}"' for k, v in values.items() if v]
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_key():
    """Returns (ok, message) using the connect() check from labs_common."""
    result = subprocess.run([str(PYTHON), "-c", "import labs_common; labs_common.connect()"],
                            cwd=ROOT, capture_output=True, text=True)
    lines = [l.strip() for l in (result.stdout + result.stderr).splitlines()
             if l.strip() and not l.startswith(("Traceback", "  File", "SystemExit", "    "))
             and "see the message above" not in l]
    return result.returncode == 0, lines


def fix_certificates(values):
    """Company networks often replace certificates. Then the system certificate store helps."""
    values["LABS_TLS"] = "system"
    write_env(values)
    ok, lines = test_key()
    if not ok:
        values.pop("LABS_TLS")
        write_env(values)
    return ok, lines


def main():
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

    # 4. API key
    values = read_env()
    if values.get("ANTHROPIC_API_KEY"):
        ok, lines = test_key()
        if not ok and any("certificate" in l.lower() for l in lines):
            ok, lines = fix_certificates(values)
        if ok:
            say("✓ API key found and working\n")
            say("All set. Open 01_eval/Eval.ipynb in VS Code and pick the kernel “Isar Coffee Labs (.venv)”.")
            return
        say("! The saved key doesn't work: " + " ".join(lines[-2:]))

    if not sys.stdin.isatty():
        say("✗ The API key has to be typed in a terminal. Run this script yourself: python3 setup_labs.py")
        sys.exit(1)

    while True:
        say("\nPaste your Anthropic API key and press Enter.")
        say("(You won't see it while you type. It starts with sk-ant-. Get one at console.anthropic.com)")
        key = getpass.getpass("API key: ").strip()
        if not key.startswith("sk-ant-"):
            say("✗ That doesn't look like an Anthropic API key. Try again.")
            continue
        values["ANTHROPIC_API_KEY"] = key
        write_env(values)
        ok, lines = test_key()
        if not ok and any("certificate" in l.lower() for l in lines):
            say("  Your network replaces certificates – switching to the system certificate store ...")
            ok, lines = fix_certificates(values)
        if ok:
            break
        say("✗ " + " ".join(lines[-2:]))
        if input("Try another key? [Y/n] ").strip().lower() == "n":
            sys.exit(1)

    say("✓ API key saved and working\n")
    say("All set. Open 01_eval/Eval.ipynb in VS Code and pick the kernel “Isar Coffee Labs (.venv)”.")


if __name__ == "__main__":
    main()
