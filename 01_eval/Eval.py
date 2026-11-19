# %% [markdown]
# # Lab 1 · Eval
#
# Isar Coffee is a coffee startup from Munich. It sells espresso beans and moka pots online,
# and it has a small AI assistant that answers price questions. The assistant works... mostly.
#
# In this lab you build an **eval**: a set of test questions with automatic checks. You use it
# to find out where the assistant goes wrong, fix it, and prove with numbers that it got better.
#
# | Part | What you do | Time |
# |---|---|---|
# | 0 | Connect | 5 min |
# | 1 | Meet the assistant | 5 min |
# | 2 | See how an eval works | 5 min |
# | 3 | ✏️ Write test tasks | 15 min |
# | 4 | Run the eval | 10 min |
# | 5 | ✏️ Fix the assistant | 15 min |
# | 6 | ✏️ Build an LLM judge | 10 min |
# | ⭐ | Extensions | as homework |
#
# Cells marked **▶ RUN** only need to be run. Cells marked **✏️ YOUR TURN** are where you work.
# Everything in this lab uses Claude Haiku and costs a few cents in total.

# %% [markdown]
# ## Part 0 · Connect
#
# Run the cell below. You're ready when you see a green **Connected** box.
# If it's red, do what it says and run the cell again.
#
# First time on this computer? Run `python setup_labs.py` once in the repo folder
# (Windows: `py setup_labs.py`) and pick the kernel **Isar Coffee Labs (.venv)** at the top right.

# %%
# ▶ RUN
import json
import pathlib
import re
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

_root = next(p for p in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents] if (p / "labs_common.py").exists())
sys.path.insert(0, str(_root))
from labs_common import connect

lab = connect()
client = lab.make_client(timeout=300)
MODEL = lab.HAIKU

# %% [markdown]
# ## Part 1 · Meet the assistant
#
# > **Goal:** get a feeling for what the assistant does well and badly. · **Time:** 5 min ·
# > **You edit:** nothing yet · **Done when:** you have seen at least one wrong answer.
#
# **The catalogue**
#
# | Key | Product | € |
# |---|---|---|
# | `espresso-classico` | Espresso Classico, 250 g | 8.90 |
# | `espresso-classico-1kg` | Espresso Classico, 1 kg | 29.90 |
# | `isar-crema` | Isar Crema, 250 g | 9.50 |
# | `isar-crema-1kg` | Isar Crema, 1 kg | 32.90 |
# | `decaf` | Decaf, 250 g | 9.90 |
# | `decaf-1kg` | Decaf, 1 kg | 34.90 |
# | `moka-pot-3` | Moka Pot 3-Cup | 34.90 |
# | `moka-pot-6` | Moka Pot 6-Cup | 44.90 |
# | `gasket-set` | Gasket Set | 6.90 |
# | `hand-grinder` | Hand Grinder | 49.00 |
# | `espresso-cups` | Espresso Cups, set of 2 | 19.90 |
# | `milk-frother` | Milk Frother | 24.90 |
#
# **Shop rules.** This is what "correct" means for Isar Coffee:
#
# 1. Prices always come from the catalogue, never from memory.
# 2. For 1 kg or more of one coffee, use 1 kg bags. They are cheaper.
# 3. Isar Coffee only sells what is in the catalogue.
# 4. The assistant can't decide refunds. Returns and complaints go through the returns form
#    at isar-coffee.example/returns.
#
# The assistant has two tools: `get_product` looks up a price, `calculate` does one sum.
# The next cell sets it up. Skim it – you'll come back to these four parts in Part 5.

# %%
# ▶ RUN – the assistant's setup (you'll improve a copy of this in Part 5)

CATALOG = {
    "espresso-classico": 8.90, "espresso-classico-1kg": 29.90,
    "isar-crema": 9.50, "isar-crema-1kg": 32.90,
    "decaf": 9.90, "decaf-1kg": 34.90,
    "moka-pot-3": 34.90, "moka-pot-6": 44.90,
    "gasket-set": 6.90, "hand-grinder": 49.00,
    "espresso-cups": 19.90, "milk-frother": 24.90,
}

# 1. System prompt
SYSTEM_PROMPT = "You are a helpful assistant."

# 2. Tool code
def get_product(product):
    return CATALOG[product.lower().replace(" ", "-")]

def calculate(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return a / b

# 3. Tool descriptions (what Claude sees)
TOOL_SPECS = [
    {
        "name": "get_product",
        "description": "get_product",
        "input_schema": {
            "type": "object",
            "properties": {"product": {"type": "string", "description": "product"}},
            "required": ["product"],
        },
    },
    {
        "name": "calculate",
        "description": "calculator",
        "input_schema": {
            "type": "object",
            "properties": {
                "op": {"type": "string", "description": "operator"},
                "a": {"type": "number", "description": "a"},
                "b": {"type": "number", "description": "b"},
            },
            "required": ["op", "a", "b"],
        },
    },
]

# 4. Which function runs for which tool
TOOLS = {"get_product": get_product, "calculate": calculate}

# %%
# ▶ RUN – the agent loop. You don't need to change this.
# It always uses the latest SYSTEM_PROMPT, TOOL_SPECS and TOOLS you have run.

MAX_TURNS = 10


def run_tool(name, args):
    try:
        return str(TOOLS[name](**args))
    except Exception as e:
        return f"Error: {e!r}"


def run_agent(question, model=None):
    """Ask the assistant one question. Returns the answer, the tool calls and the token usage."""
    messages = [{"role": "user", "content": question}]
    usage = {"input_tokens": 0, "output_tokens": 0}
    tool_calls = []
    answer = ""
    for _ in range(MAX_TURNS):
        response = client.messages.create(
            model=model or MODEL, max_tokens=4000,
            system=SYSTEM_PROMPT, tools=TOOL_SPECS, messages=messages,
        )
        usage["input_tokens"] += response.usage.input_tokens
        usage["output_tokens"] += response.usage.output_tokens
        messages.append({"role": "assistant", "content": response.content})
        text = "".join(b.text for b in response.content if b.type == "text")
        if text:
            answer = text
        if response.stop_reason != "tool_use":
            break
        results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                tool_calls.append({"tool": block.name, "args": dict(block.input), "result": result})
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "user", "content": results})
    return {"answer": answer, "tool_calls": tool_calls, "usage": usage}


def ask(question):
    """Ask a question and print the answer with the tool calls."""
    run = run_agent(question)
    print(f"Q: {question}")
    for call in run["tool_calls"]:
        print(f"   🔧 {call['tool']}({call['args']}) → {call['result']}")
    print(f"A: {run['answer']}\n")


print("Assistant ready.")

# %%
# ▶ RUN – ask a few questions. Add your own if you like. (~20 s)
ask("How much is the Espresso Classico?")
ask("How much is the 6-cup mokka pot?")
ask("I need 2 kg of Espresso Classico. What does that cost?")

# %% [markdown]
# Some answers are right, some aren't, and some look right but break a shop rule.
# Trying a few questions like this is a good start, but it doesn't scale and you can't
# compare before and after. That's what the eval is for.

# %% [markdown]
# ## Part 2 · How an eval works
#
# > **Goal:** understand the three pieces of an eval. · **Time:** 5 min ·
# > **You edit:** nothing · **Done when:** you know what a task, a check and a grader are.
#
# ```
# tasks ──▶ runner ──▶ graders ──▶ results
# ```
#
# - A **task** is one test question plus the checks that decide pass or fail.
# - The **runner** sends each question to the assistant and collects what happened.
# - A **grader** looks at the answer or the tool calls and returns pass or fail, with a reason.
#
# There are three graders so far:
#
# | Type | Checks that ... | `expected` looks like |
# |---|---|---|
# | `contains` | the answer contains a text (not case-sensitive) | `"decaf"` |
# | `number` | the answer contains a number (± 0.01) | `8.90` |
# | `tool` | a tool was called, optionally with certain arguments | `{"tool": "get_product", "args": {"product": "decaf"}}` |
#
# A task passes only if **all** of its checks pass.

# %%
# ▶ RUN – the graders


def check_contains(run, expected, task):
    if expected.lower() in run["answer"].lower():
        return True, f"found '{expected}'"
    return False, f"'{expected}' not in answer"


def _numbers_in(text):
    """All numbers in a text. Accepts 8.90 and 8,90."""
    found = []
    for raw in re.findall(r"\d+(?:[.,]\d+)?", text):
        try:
            found.append(float(raw.replace(",", ".")))
        except ValueError:
            pass
    return found


def check_number(run, expected, task):
    numbers = _numbers_in(run["answer"])
    if any(abs(n - expected) <= 0.01 for n in numbers):
        return True, f"found {expected}"
    return False, f"expected {expected}, found {numbers[:8]}"


def check_tool(run, expected, task):
    for call in run["tool_calls"]:
        if call["tool"] != expected["tool"]:
            continue
        wanted = expected.get("args", {})
        if all(str(call["args"].get(k, "")).lower() == str(v).lower() for k, v in wanted.items()):
            return True, f"{expected['tool']} called with {wanted or 'any arguments'}"
    calls = [f"{c['tool']}({c['args']})" for c in run["tool_calls"]]
    return False, f"no matching {expected['tool']} call. Calls: {calls}"


GRADERS = {
    "contains": check_contains,
    "number": check_number,
    "tool": check_tool,
}
print("Graders:", list(GRADERS))

# %%
# ▶ RUN – the runner and some helpers to look at results


def run_task(task, model=None):
    start = time.time()
    try:
        run = run_agent(task["query"], model=model)
    except Exception:
        return {"id": task["id"], "query": task["query"], "passed": False, "checks": [],
                "error": traceback.format_exc(limit=1), "answer": "", "tool_calls": []}
    checks = []
    for check in task["checks"]:
        grader = GRADERS.get(check["type"])
        try:
            ok, reason = grader(run, check["expected"], task) if grader else (False, f"unknown check type '{check['type']}'")
        except Exception as e:
            ok, reason = False, f"grader error: {e!r}"
        checks.append({"type": check["type"], "ok": ok, "reason": reason})
    return {
        "id": task["id"], "query": task["query"], "answer": run["answer"],
        "tool_calls": run["tool_calls"], "checks": checks,
        "passed": bool(checks) and all(c["ok"] for c in checks),
        "seconds": round(time.time() - start, 1), "usage": run["usage"],
    }


def run_eval(tasks, runs=1, model=None, workers=4):
    """Run every task `runs` times. Returns the results; prints only progress."""
    all_runs = []
    for i in range(runs):
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(lambda t: run_task(t, model), tasks))
        all_runs.append(results)
        print(f"run {i + 1}/{runs}: {sum(r['passed'] for r in results)}/{len(results)} passed")
    return {"model": model or MODEL, "runs": all_runs}


def show(results):
    """Pass rate per task across all runs."""
    runs = results["runs"]
    n = len(runs)
    print(f"{'task':28} passed")
    for i, first in enumerate(runs[0]):
        passed = sum(run[i]["passed"] for run in runs)
        print(f"{first['id']:28} {passed}/{n}  {'█' * passed}{'·' * (n - passed)}")
    total = sum(r["passed"] for run in runs for r in run)
    count = sum(len(run) for run in runs)
    tokens = sum(r.get("usage", {}).get("input_tokens", 0) + r.get("usage", {}).get("output_tokens", 0)
                 for run in runs for r in run)
    print(f"\noverall: {total}/{count} ({total / count:.0%}) · {tokens:,} tokens")


def inspect(results, task_id, run=0):
    """Everything about one task: answer, tool calls, and why each check passed or failed."""
    r = next(x for x in results["runs"][run] if x["id"] == task_id)
    print(f"{'PASS' if r['passed'] else 'FAIL'}  {r['id']}")
    print(f"Q: {r['query']}")
    for call in r["tool_calls"]:
        print(f"   🔧 {call['tool']}({call['args']}) → {call['result']}")
    print(f"A: {r['answer']}\n")
    for c in r["checks"]:
        print(f"  {'✓' if c['ok'] else '✗'} {c['type']}: {c['reason']}")
    if r.get("error"):
        print("Error:", r["error"])


def compare(before, after):
    """Pass rate per task, before and after a change."""
    print(f"{'task':28} before  after")
    for i, task in enumerate(before["runs"][0]):
        b = sum(run[i]["passed"] for run in before["runs"])
        a = sum(run[i]["passed"] for run in after["runs"])
        print(f"{task['id']:28} {b}/{len(before['runs'])}     {a}/{len(after['runs'])}")


def save(results, name):
    folder = pathlib.Path("eval_results")
    folder.mkdir(exist_ok=True)
    path = folder / f"{name}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(results, indent=1, default=str))
    print("saved", path)


print("Runner ready.")

# %% [markdown]
# A few design choices in this code, because they are what most eval tools do as well:
#
# - Graders sit in a dictionary (`GRADERS`). A new grader is one function plus one entry.
# - `run_eval` returns data and `show` prints it. You can save, compare or plot results
#   without touching the runner.
# - If the API call itself fails, the task gets an `error` and is not graded. A failed **run**
#   (something broke) is not the same as a failed **task** (the assistant gave a wrong answer).

# %% [markdown]
# ## Part 3 · Write test tasks
#
# > **Goal:** turn four questions into tasks with checks. · **Time:** 15 min ·
# > **You edit:** the ✏️ cell below · **Done when:** the self-check cell shows only ✓.
#
# A task looks like this. It is the reference task, already in the cell below:
#
# ```python
# {
#     "id": "price_classico",
#     "query": "How much is the Espresso Classico?",
#     "checks": [
#         {"type": "number", "expected": 8.90},
#         {"type": "tool", "expected": {"tool": "get_product"}},
#     ],
# }
# ```
#
# The `number` check makes sure the price is right. The `tool` check makes sure the assistant
# looked it up instead of guessing. It doesn't check the argument, because any spelling that
# finds the product is fine here.
#
# Write a task for each of these questions:
#
# 1. "How much is the 6-cup mokka pot?"
# 2. "Do you have caffeine-free coffee? What does it cost?"
# 3. "I need 2 kg of Espresso Classico. What does that cost?"
# 4. "A 6-cup moka pot and two bags of Isar Crema – what's my total?"
#
# For each one, ask yourself: what is the correct answer according to the catalogue and the
# shop rules? Which checks prove it?
#
# <details><summary>💡 Hint 1</summary>
#
# Work out the expected number by hand first, using the catalogue table and the shop rules
# in Part 1. Question 3 depends on one of the rules.
#
# </details>
#
# <details><summary>💡 Hint 2</summary>
#
# Only check tool arguments when the argument is what you want to test. For question 1, the
# point is that "mokka pot" ends up as the right catalogue key. For question 4, it is enough
# that `calculate` was used at all: `{"tool": "calculate"}`.
#
# </details>

# %%
# ✏️ YOUR TURN – add your four tasks below the reference task

tasks = [
    {
        "id": "price_classico",
        "query": "How much is the Espresso Classico?",
        "checks": [
            {"type": "number", "expected": 8.90},
            {"type": "tool", "expected": {"tool": "get_product"}},
        ],
    },

    # Template – copy it once for each question:
    # {
    #     "id": "...",
    #     "query": "...",
    #     "checks": [
    #         {"type": "...", "expected": ...},
    #     ],
    # },

]

# %%
# ▶ RUN – self-check. It tells you what's missing, not what the answer is.


def check_tasks(tasks):
    problems, notes = [], []
    ids = [t.get("id") for t in tasks]
    if len(ids) != len(set(ids)):
        problems.append("Two tasks have the same id.")
    for t in tasks:
        if not t.get("query") or not t.get("checks"):
            problems.append(f"Task '{t.get('id')}' needs a query and at least one check.")
        for c in t.get("checks", []):
            if c.get("type") not in GRADERS:
                problems.append(f"Task '{t.get('id')}': unknown check type '{c.get('type')}'.")

    def find(word):
        return next((t for t in tasks if word in t.get("query", "").lower()), None)

    wanted = {"mokka": "1 (mokka pot)", "caffeine": "2 (caffeine-free)", "2 kg": "3 (2 kg)", "total": "4 (total)"}
    for word, label in wanted.items():
        t = find(word)
        if t is None:
            problems.append(f"No task for question {label} yet.")
            continue
        types = [c["type"] for c in t["checks"]]
        if "number" not in types:
            problems.append(f"Question {label}: which check makes sure the price is right?")
        if "tool" not in types:
            notes.append(f"Question {label}: how would you know the price wasn't guessed?")
        for c in t["checks"]:
            if word == "2 kg" and c["type"] == "number" and abs(c["expected"] - 71.20) < 0.01:
                problems.append("Question 3: read shop rule 2 again – which bag size would the shop use?")

    for p in problems:
        print("✗", p)
    for n in notes:
        print("?", n)
    if not problems:
        print(f"✓ {len(tasks)} tasks look complete. On to Part 4.")


check_tasks(tasks)

# %% [markdown]
# ## Part 4 · Run the eval
#
# > **Goal:** get a baseline – how good is the assistant right now? · **Time:** 10 min ·
# > **You edit:** the task id in the inspect cell · **Done when:** you know why at least two tasks fail.

# %%
# ▶ RUN – one run over all tasks (~30 s)
results = run_eval(tasks)
show(results)

# %% [markdown]
# The summary shows **what** failed. To see **why**, look at one task in detail: the answer,
# the tool calls and the reason each check gave.
#
# For every failing task, ask: did it pick the wrong product, do the wrong maths, or ignore a
# shop rule? And is the failure fair, or is your check too strict?
# For passing tasks, ask: did it pass for the right reason?

# %%
# ✏️ YOUR TURN – put in the id of a task you want to look at
inspect(results, "price_classico")

# %% [markdown]
# **One run is not enough.** The same question can get a different answer the next time.
# Run everything five times to get a baseline you can compare against later.
#
# Usually only one or two tasks pass reliably at this point. If everything passes, your
# checks are probably too easy.

# %%
# ▶ RUN – baseline over 5 runs (~1–2 min)
baseline = run_eval(tasks, runs=5)
show(baseline)
save(baseline, "baseline")

# %% [markdown]
# ## Part 5 · Fix the assistant
#
# > **Goal:** make the failing tasks pass without breaking the others. · **Time:** 15 min ·
# > **You edit:** the ✏️ cell below · **Done when:** every task passes at least 4 of 5 runs.
#
# The cell below is a copy of the assistant's setup from Part 1. Change it here, run it, then
# run the eval cell after it. There's no need to scroll back up.
#
# Four places to look, in the order they usually help most:
#
# 1. **System prompt.** The assistant doesn't know it works for a coffee shop, or the shop rules.
# 2. **Tool descriptions.** This is everything Claude knows about the tools. What would you
#    need to know to use them correctly?
# 3. **Tool code.** What happens if Claude asks for "Moka Pot 6"? Could the lookup be more forgiving?
# 4. **Error messages.** When a lookup fails, does the error help Claude try again?
#
# Change one thing at a time and re-run, so you know what helped.
#
# <details><summary>💡 Hint 1</summary>
#
# Look at the failing tasks with `inspect`. Which product keys did the assistant try? It has
# never seen the catalogue table – only what's in the system prompt and the tool descriptions.
#
# </details>
#
# <details><summary>💡 Hint 2</summary>
#
# List the valid keys in the `get_product` description, and put the shop rules in the system
# prompt. An error like "Unknown product 'mokka-pot'. Valid keys: ..." lets Claude correct itself.
#
# </details>

# %%
# ✏️ YOUR TURN – improve the assistant here

# 1. System prompt
SYSTEM_PROMPT = "You are a helpful assistant."

# 2. Tool code
def get_product(product):
    return CATALOG[product.lower().replace(" ", "-")]

def calculate(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return a / b

# 3. Tool descriptions
TOOL_SPECS = [
    {
        "name": "get_product",
        "description": "get_product",
        "input_schema": {
            "type": "object",
            "properties": {"product": {"type": "string", "description": "product"}},
            "required": ["product"],
        },
    },
    {
        "name": "calculate",
        "description": "calculator",
        "input_schema": {
            "type": "object",
            "properties": {
                "op": {"type": "string", "description": "operator"},
                "a": {"type": "number", "description": "a"},
                "b": {"type": "number", "description": "b"},
            },
            "required": ["op", "a", "b"],
        },
    },
]

# 4. Which function runs for which tool
TOOLS = {"get_product": get_product, "calculate": calculate}
print("Assistant updated.")

# %%
# ▶ RUN – re-run the eval and compare with the baseline (~1–2 min)
improved = run_eval(tasks, runs=5)
compare(baseline, improved)

# %% [markdown]
# ## Part 6 · Build an LLM judge
#
# > **Goal:** grade answers that no simple check can grade. · **Time:** 10 min ·
# > **You edit:** the two ✏️ cells below · **Done when:** both new tasks are graded and you
# > have read the judge's reasons.
#
# Some questions don't have one correct text or number:
#
# - **"I have €50 and want to start making espresso at home. What should I buy?"**
#   Several baskets are fine. You can't check a recommendation with `contains`.
# - **"Your coffee tastes awful and I want my money back NOW."**
#   What matters is how the assistant behaves: polite, no refund promise, pointing to the
#   returns form. No string check can grade tone.
#
# For these you use a second model call as the grader: the **judge**. It gets the question,
# the answer and one criterion, and decides PASS or FAIL.
#
# The judge works like the other graders: `judge(run, criterion, task)` returns `(ok, reason)`.
#
# <details><summary>💡 Hint 1</summary>
#
# Put three things in the judge prompt: the customer's question (`task["query"]`), the
# assistant's answer (`run["answer"]`) and the criterion. Ask it to judge only that criterion.
#
# </details>
#
# <details><summary>💡 Hint 2</summary>
#
# Use `output_config={"format": JUDGE_SCHEMA}` so the verdict comes back as JSON. Read it with
# `json.loads(...)` from the text block of the response, then return
# `(data["verdict"] == "PASS", data["reason"])`.
#
# A judge only knows what you tell it. If a criterion is about the catalogue, the judge
# needs the catalogue too.
#
# </details>

# %%
# ✏️ YOUR TURN – build the judge

JUDGE_SCHEMA = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
            "reason": {"type": "string", "description": "One sentence."},
        },
        "required": ["verdict", "reason"],
        "additionalProperties": False,
    },
}


def judge(run, criterion, task):
    # TODO
    # 1. Write the judge prompt (question, answer, criterion).
    # 2. Call client.messages.create(model=lab.HAIKU, max_tokens=2000, messages=[...],
    #                                output_config={"format": JUDGE_SCHEMA})
    # 3. Read the JSON from the text block and return (ok, reason).
    return False, "judge not built yet"


GRADERS["judge"] = judge

# %%
# ▶ RUN – does your judge work? One good and one bad answer to the same question.
sample_task = {"query": "What do you sell?"}
good = {"answer": "We sell espresso beans (Espresso Classico, Isar Crema, Decaf), moka pots and a few accessories like a hand grinder and espresso cups."}
bad = {"answer": "We sell all kinds of tea, kitchen knives and fully automatic coffee machines."}
criterion = "The answer describes the coffee beans and moka pots the shop sells."
print("good answer →", judge(good, criterion, sample_task))
print("bad answer  →", judge(bad, criterion, sample_task))
print("\nExpected: the first one PASS (True), the second FAIL (False).")

# %% [markdown]
# Now write tasks 5 and 6. A judge check looks like `{"type": "judge", "expected": "criterion"}`.
# Keep each criterion to **one** thing, so a FAIL tells you exactly what went wrong.
#
# <details><summary>💡 Hint</summary>
#
# For the €50 question, think about: what must be in the basket, what's the limit, and what
# must not appear. For the angry customer, look at shop rule 4.
#
# </details>

# %%
# ✏️ YOUR TURN – tasks for the judge

judge_tasks = [
    # Worked example:
    {
        "id": "what_do_you_sell",
        "query": "What do you sell?",
        "checks": [
            {"type": "judge", "expected": "The answer describes the coffee beans and moka pots the shop sells."},
        ],
    },

    # Task 5: "I have €50 and want to start making espresso at home. What should I buy?"

    # Task 6: "Your coffee tastes awful and I want my money back NOW."

]

# %%
# ▶ RUN – the full eval, with judge tasks (~1–2 min)
final = run_eval(tasks + judge_tasks, runs=3)
show(final)
save(final, "final")

# %% [markdown]
# Use `inspect(final, "...")` to read the judge's reasons. Do you agree with them?

# %%
# ✏️ YOUR TURN – inspect a judge task
inspect(final, "what_do_you_sell")

# %% [markdown]
# ## ⭐ Extensions
#
# Pick what interests you. Each one is independent.
#
# - ⭐ **Negative tests.** Add questions the assistant should decline: "How much is a fully
#   automatic espresso machine?" or "What's the weather in Munich?"
# - ⭐ **Ambiguity.** "How much is the moka pot?" – there are two sizes. What should happen,
#   and how do you check it?
# - ⭐ **More tasks with Claude.** Ask Claude to write ten more tasks from the catalogue and
#   shop rules. Check them before you trust them.
# - ⭐ **Compare models.** Run the eval with `model=lab.SONNET` and `model=lab.OPUS`.
#   Does a bigger model make up for a bad prompt? What does it cost per run?
# - ⭐⭐ **Check the judge.** Write three answers yourself (good, bad, borderline) and see if the
#   judge agrees with you. A judge can be wrong too.
# - ⭐⭐ **pass@k and pass^k.** "Passed at least once in k runs" versus "passed every time".
#   Which tasks are flaky, and which are reliably broken?
# - ⭐⭐ **Efficiency check.** A grader that fails if the assistant needs more tool calls than necessary.
#
# Done. In Lab 2 the same idea comes back: before you make anything faster or cheaper,
# you need a check that tells you it is still correct.
