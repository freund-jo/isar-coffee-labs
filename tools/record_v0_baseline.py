"""Records the v0 run over all nine sample claims into 02_inference/v0_baseline.json.

    .venv/bin/python tools/record_v0_baseline.py [--gateway]     (from the repo root)

Runs the notebook's cells up to and including the v0 definition, then v0 on every claim, one
after another (about 7 minutes, about $1.30 at list prices). Only needed if v0, the claims or
the handbook change. Participants load this file instead
of paying for the run themselves.
"""
import json, os, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
LABS = HERE.parent
sys.path.insert(0, str(HERE))
import run_notebook  # noqa: E402

sys.path.insert(0, str(LABS))
os.chdir(LABS / "02_inference")
if "--gateway" in sys.argv:
    run_notebook.use_gateway()

nb = json.loads((LABS / "02_inference/Inference.ipynb").read_text())
ns = {"__name__": "__main__"}
for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    exec(compile(src, "Inference.ipynb", "exec"), ns)
    if 'print("v0 ready.")' in src:
        break

rep = ns["run_claims"](ns["inference_v0"])
ns["report"](rep, "v0 – recorded")
out = {"note": "Recorded v0 run (Claude Opus 5.5), costs at Anthropic list prices.",
       "wall": rep["wall"], "rows": rep["rows"]}
(LABS / "02_inference/v0_baseline.json").write_text(json.dumps(out, indent=1))
print("saved v0_baseline.json")
