# Isar Coffee Labs

Two hands-on labs about building with Claude. The example is Isar Coffee, a small coffee
startup from Munich.

| Lab | What you do | Time |
|---|---|---|
| **Lab 1 · Eval** – `01_eval/Eval.ipynb` | Test an AI assistant, fix it, and prove it got better | ~60 min |
| **Lab 2 · Inference** – coming soon | Make an AI workflow fast and cheap without losing accuracy | ~60 min |

## Setup (once, about 5 minutes)

**1. Get an Anthropic API key**

- Sign up at [console.anthropic.com](https://console.anthropic.com).
- Under **Billing**, add a few dollars of credit. Both labs together cost well under that.
- Under **API Keys**, create a key and keep the tab open.

A Claude.ai subscription (Pro, Max) is not an API key.
If your company gave you a key for its AI gateway instead, use that. The setup then also asks
for the gateway address.

**2. Get the code**

Clone the repo or download it as a zip and unzip it. Put it in a normal local folder such as
`C:\dev\` or `~/projects/` – **not in OneDrive, Dropbox or iCloud**, because syncing breaks the setup.

**3. Run the setup**

Open the folder in VS Code (**File → Open Folder**), then **Terminal → New Terminal** and run:

```
python3 setup_labs.py        (Mac)
py setup_labs.py             (Windows)
```

Paste your key when it asks. When it says **All set**, you're done.

**4. Open the lab**

Open `01_eval/Eval.ipynb`. At the top right, click **Select Kernel** and pick **Isar Coffee Labs (.venv)**.
Run the first cell. A green **Connected** box means you're ready.

You need Python 3.10 or newer and VS Code with the *Python* and *Jupyter* extensions.

## Stuck? Ask Claude

If you use [Claude Code](https://claude.com/claude-code), open a terminal in this folder and run `claude`.

- **Setup:** say "help me set up the labs". It knows the steps and opens the setup for you.
- **The labs:** it acts as a tutor. It asks what you tried and gives you a hint instead of the
  answer. If you want the full solution, just ask for it.

Using Claude.ai instead? Upload the notebook and start with: *"Be my tutor for this lab. Give me
hints, not answers, unless I ask for the solution."*

## If something goes wrong

| Problem | Fix |
|---|---|
| Red box: **Setup not done yet** | Run step 3, then pick the kernel (step 4) |
| Red box: **certificate** or **network** | Run `python3 setup_labs.py --check-tls` (Windows: `py setup_labs.py --check-tls`) |
| Red box: **key rejected** | Run step 3 again. It asks for a new key |
| Kernel not in the list | Restart VS Code once |
| `python3` not found on Windows | Use `py` |
