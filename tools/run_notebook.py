"""Run a lab notebook top to bottom from the terminal, to test it.

From the repo root:

    .venv/bin/python tools/run_notebook.py 01_eval/Eval_solution.ipynb
    .venv/bin/python tools/run_notebook.py 02_inference/Inference.ipynb

Normally the notebook uses the API key from .env.
With --gateway it uses the company gateway from your Claude Code settings instead
(base URL + SSO key helper). The labs find the gateway's model names themselves.
"""

import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
LABS = HERE.parent


def use_gateway():
    settings = json.loads((pathlib.Path.home() / ".claude/settings.json").read_text())
    token = subprocess.run(settings["apiKeyHelper"], shell=True, capture_output=True, text=True).stdout.strip()
    os.environ["ANTHROPIC_BASE_URL"] = settings["env"]["ANTHROPIC_BASE_URL"]
    os.environ["ANTHROPIC_API_KEY"] = token
    import labs_common
    labs_common.ENV_FILE = pathlib.Path("/nonexistent")  # keep .env from overriding the token


def main():
    nb_path = pathlib.Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(LABS))
    os.chdir(LABS / ("02_inference" if "Inference" in nb_path.name else "01_eval"))
    if "--gateway" in sys.argv:
        use_gateway()
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__"}
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        print(f"\n──── cell {i} ────", flush=True)
        exec(compile(source, f"{nb_path.name}[{i}]", "exec"), namespace)


if __name__ == "__main__":
    main()
