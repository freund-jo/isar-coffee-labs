# Isar Coffee Labs

Two hands-on labs about building with Claude, using a small Munich coffee shop as the example.

| Lab | What you learn | Time |
|---|---|---|
| [Lab 1 · Eval](01_eval/) | Test an AI assistant with an eval, fix it, and prove it got better | ~60–90 min |
| Lab 2 · Inference | Make a slow, expensive AI workflow fast and cheap without losing accuracy | coming soon |

---

## Before the session

You need:

1. **An Anthropic API key** from [console.anthropic.com](https://console.anthropic.com).
   Add a little credit (a few dollars are enough) and set a monthly spend limit under *Billing*.
   A Claude.ai subscription (Pro, Max) is **not** an API key.
   If you were given access to a company AI gateway instead, you don't need your own key.
2. **Python 3.10 or newer**. Check with `python --version` (Windows: `py --version`).
3. **VS Code** with the *Python* and *Jupyter* extensions.
4. Optional: **[Claude Code](https://claude.com/claude-code)**, if you want a tutor next to you while you work (see below).

## Step 1 · Get the code

Either clone it:

```bash
git clone <repo-url> isar-coffee-labs
```

or download the zip and unzip it.

> **Put the folder somewhere local – not in OneDrive, Dropbox or iCloud.**
> For example `C:\dev\isar-coffee-labs` (Windows) or `~/projects/isar-coffee-labs` (Mac).
> Sync folders break the Python environment, and they would upload your key to the cloud.
> On many company laptops the Desktop and Documents folders are synced to OneDrive too.

## Step 2 · Run the setup (once)

Open the folder in VS Code (**File → Open Folder**), then **Terminal → New Terminal** and run:

```bash
python3 setup_labs.py      # Mac
py setup_labs.py           # Windows
```

It creates a Python environment, installs everything, asks for your key and tests the connection.
Paste your key only into this terminal – never into a notebook or a chat.
When it says **You're all set**, you're done.

## Step 3 · Open a lab

Open `01_eval/Eval.ipynb`. At the top right, click **Select Kernel** and pick
**Isar Coffee Labs (.venv)**. If you don't see it, choose *Select Another Kernel → Jupyter Kernel*.

Run the first cell. A green **Connected** box means you're ready.

## Optional · Work with a Claude tutor

If you have Claude Code, open a terminal in the repo folder and run `claude`.
It picks up the tutor instructions in this repo automatically. It won't hand you the answers –
it asks what you tried and gives you a nudge. Useful commands:

| Command | What it does |
|---|---|
| `/hint` | The next hint for the exercise you're on |
| `/check` | Looks at your cell and tells you what's wrong, not how to fix it |
| `/explain <term>` | Explains a term, e.g. `/explain grader` |

If you'd like the full answer, just ask for it.
Using Claude.ai or Claude Desktop instead? Copy [TUTOR_PROMPT.md](TUTOR_PROMPT.md) into a new project or chat.

## If something goes wrong

| Problem | Fix |
|---|---|
| Red box: **Packages missing** | Run the setup again (Step 2), then pick the right kernel |
| Red box: **certificate** / **SSL** | Company networks often check HTTPS traffic. Run `python3 setup_labs.py --check-tls` (Windows: `py setup_labs.py --check-tls`), then run the cell again |
| Red box: **key was rejected** | Delete the `.env` file and run the setup again |
| Kernel not in the list | Restart VS Code once after the setup |
| `python` not found on Windows | Use `py` instead of `python` |

## Cost

Lab 1 uses Claude Haiku and costs a few cents. Each notebook shows a rough cost on the cells
that call the API, so you know what to expect before you run something.
