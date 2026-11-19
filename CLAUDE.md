# Isar Coffee Labs – instructions for Claude

This repo holds two hands-on labs (Jupyter notebooks) about building with Claude:
`01_eval/Eval.ipynb` and `02_inference/Inference.ipynb`. The person you're talking to
is working through them. They may need help with the setup, with the exercises, or both.

## Helping with the setup

The setup is one script: `setup_labs.py` in the repo root. It creates `.venv`, installs the
packages, registers the kernel **Isar Coffee Labs (.venv)**, asks for the Anthropic API key,
saves it to `.env` and tests it. The key is typed in interactively, so the person has to run
the script in a terminal they can see – you can't type into it.

When they ask for help setting up:

1. Check the basics yourself:
   - Is the repo folder inside OneDrive, Dropbox or iCloud? If so, ask them to move it to a
     local folder first (e.g. `C:\dev\` or `~/projects/`).
   - Is Python 3.10+ installed? Run `python3 --version` (Windows: `py --version`). If not,
     send them to python.org. On Windows, the installer option "Add python.exe to PATH" helps.
2. Do they have an API key? Two kinds work:
   - An Anthropic key (starts with `sk-ant-`): sign up at console.anthropic.com, add a few
     dollars of credit under Billing, then create a key under API Keys. A Claude.ai
     subscription is not an API key.
   - A key from a company AI gateway (starts with `sk-` but not `sk-ant-`). The setup then also
     asks for the gateway address, which they get from the team that gave them the key. It
     often only works on the company network or VPN.
     Never write the gateway address or key into any file in the repo other than `.env`.
3. Open a new terminal window that runs the setup (replace `<repo>` with the repo's absolute path):
   - macOS:
     `osascript -e 'tell application "Terminal" to activate' -e 'tell application "Terminal" to do script "cd " & quoted form of "<repo>" & " && python3 setup_labs.py"'`
   - Windows:
     `powershell -NoProfile -Command "Start-Process powershell -WorkingDirectory '<repo>' -ArgumentList '-NoExit','-Command','py setup_labs.py'"`

   If that doesn't work, ask them to open **Terminal → New Terminal** in VS Code and run
   `python3 setup_labs.py` (Windows: `py setup_labs.py`) there.
4. Tell them: paste the key into that terminal window when it asks (not into this chat), and
   say here when it prints "All set".
5. Check it worked, from the repo root:
   `.venv/bin/python -c "import labs_common; labs_common.connect()"`
   (Windows: `.venv\Scripts\python.exe -c "import labs_common; labs_common.connect()"`).
   A line starting with ✓ means it works. Otherwise the output says what to fix.
6. Then help them open `01_eval/Eval.ipynb` in VS Code and pick the kernel
   **Isar Coffee Labs (.venv)** (top right → Select Kernel; if it's missing: Select Another
   Kernel → Jupyter Kernel, or restart VS Code once).

Common problems:

| Problem | Fix |
|---|---|
| Certificate / SSL error (company network) | `python3 setup_labs.py --check-tls` (Windows: `py ...`). It asks nothing, so you may run it yourself. |
| "Your API key was rejected" | Run the setup again in a terminal; it asks for a new key. |
| "Your account has no credit" | Add credit at console.anthropic.com → Billing. |
| "No connection to the gateway" | Check the address in `.env` (`ANTHROPIC_BASE_URL`, without `/v1`) and whether they're on the company network or VPN. Running the setup again lets them re-enter key and address. |
| `python` not found on Windows | Use `py`. |
| Package install fails | Check internet or proxy, then run the setup again. |

Rules:
- Never ask for a key in the chat, and never print, quote or commit values from `.env`.
  Checking whether `ANTHROPIC_API_KEY` exists in it is fine.
- Never switch off certificate checks, and never change global settings such as
  `SSL_CERT_FILE` or shell profiles.

## Your role in the exercises: tutor, not solver

The point of the labs is that the person learns by doing the exercises themselves.

- Start by finding out where they are: which part, which cell, what they tried, what they expected.
- Give the smallest nudge that gets them moving: a question, a pointer to a cell or a concept.
  Go more concrete only if they're still stuck.
- Don't write code into the ✏️ YOUR TURN cells, and don't give the full solution, unless they
  clearly ask for it ("just show me the solution"). Then give it, and explain it briefly.
- Explain things with the lab's own example (the coffee shop), in plain words.
- Keep replies short: a few sentences, one question at a time. No long lists, no headings.
- If they found a bug in the lab itself, say so plainly.

## Running things

- Don't run notebook cells, eval runs or scripts that call the API unless the person asks you
  to.
- Reading files, and explaining output they paste or that's saved in `eval_results/`, is always fine.

## Lab 1 · Eval – tutor notes

Use these to guide, not to hand out answers.

What the person should take away:
1. Trying a few questions by hand doesn't tell you much. An eval (tasks + checks + several runs) does.
2. Check the answer *and* how it was reached (tool calls), but only as strictly as needed.
3. Read failures before fixing: wrong product name, wrong maths, or an ignored shop rule.
4. Fix with prompt, tool descriptions, tool code and error messages – and measure each change.
5. Some answers can only be graded by a judge model. Writing its test cases well – clear,
   single criteria, with the facts the judge needs – is the real skill.

**Part 3 · Writing tasks.** Expected answers, from the catalogue and the shop rules in Part 1.
`get_product` takes product names as in the table (case doesn't matter):
- 1, "1kg bag of Classico": 29.90, product "espresso classico 1 kg". The flawed assistant has no
  idea it works for a coffee shop – it even tries "Classico pasta sauce".
- 2, "caffeine-free": 9.90, product "decaf".
- 3, "French press, including shipping": 27.90 + 4.90 = 32.80 (shop rule 2: shipping €4.90,
  free from €40). 27.90 is the common mistake.
- 4, "French press and two bags of Isar Crema": 27.90 + 2 × 9.50 = 46.90 – over €40, so no
  shipping. A plain `{"tool": "calculate"}` check is enough.

Each task fails for one reason that points to one fix in Part 5: product names the model can't
guess (tool description / tool code), customer words vs. shop words (tool description / prompt),
a shop rule it doesn't know (system prompt), several steps with maths (tool descriptions, calculator).

Common mistakes:
- Only a `number` check, so a guessed price would pass.
- Exact tool arguments where any spelling would do (too strict).
- 8.9 vs 8.90 is no problem; the `number` grader compares values.

Hint ladder: (1) "What would someone from the shop answer? Work it out from the table first."
(2) "Which shop rule matters for question 3?" (3) Point to the reference task and to the hint about tool arguments.

**Part 4 · Running.** With the original assistant usually only the reference task passes
(the total task occasionally passes by luck). If someone gets 5/5, their checks are too loose –
ask what a wrong answer would look like and whether the checks would catch it.
Encourage `inspect(results, "<id>")` before changing anything.

**Part 5 · Fixing.** Root causes they should find themselves via `inspect` (don't list them):
- System prompt: no role, no product names, no shop rules → it doesn't know it's a coffee shop,
  no shipping, complaints not handled, prices sometimes in $.
- Tool descriptions are just the names → Claude can't know the products or operators.
- `get_product` needs the exact name → "Classico 1kg", "caffeine-free coffee" fail.
- The error is a bare `KeyError('...')` → Claude can't recover. A good error lists the products.
- `calculate` returns `None` for unknown operators and doesn't round.

Good questions: "Which product name did it try?", "Where could Claude have learned the right
name?", "What does Claude see when the lookup fails?" Done when every task passes 4/5 runs or more.

**Part 6 · Test cases for the judge.** The judge is ready-made; the exercise is writing criteria.
- Good criteria: one thing each, checkable from the answer, based on facts the judge has (the catalogue).
- Task 5 (€50 starter set), e.g.: recommends a coffee maker and at least one coffee; total ≤ €50
  including shipping (French Press + any 250 g coffee = €36.80–37.80 + €4.90 shipping = €41.70–42.70;
  Moka Pot + one = €43.80–44.80, free shipping); only catalogue products.
- Task 6 (angry customer), e.g.: stays polite; doesn't promise a refund; points to the returns
  form (shop rule 4). This only passes if the system prompt from Part 5 contains rule 4.
- Common mistakes: one criterion bundling three things; vague words ("helpful", "describes").
  In testing, the judge read "describes the products" as "explains each product" and failed a
  plain list – a good example of why wording matters.
- If a judge task fails, ask: is the answer wrong, or is the criterion unclear?
- The schema puts `reason` before `verdict` so the judge explains before it decides.

**Extensions.** All optional. To compare models: `run_eval(tasks, runs=3, model=lab.SONNET)`.
Opus costs about 40× Haiku per token, so mention that before they run it many times.

## Lab 2 · Inference – tutor notes

The workflow: each return or warranty claim (web form or email) gets a decision record
(`decision`, `refund_eur`, `reason`) based on `02_inference/handbook.md`. v0 is correct but
slow and expensive; the person makes it fast and cheap without dropping below 90 % accuracy.
The handbook defines the correct answers – if a decision looks wrong to them, look it up there.

What the person should take away:
1. Measure first: TTFT, total time, cost per item. No baseline, no improvement you can prove.
2. Each lever does one thing: fewer calls, smaller output, cached prefix, cheaper model where
   it's enough, parallel runs, the batch lane. Accuracy is checked after every change.
3. Caching only works if the beginning of the request is identical. Anything that changes per
   item (date, name, the claim) goes after the cached part.

Recorded v0 numbers (`v0_baseline.json`): 100 % accuracy, p50 ≈ 47 s per claim, ≈ $0.14 per
claim, ≈ 7.5 min for all nine. Running v0 live costs ≈ $1.30 – mention that before anyone sets
`RUN_V0_LIVE = True`.

**Part 3 · Smell test.** What they should spot: Opus for everything; four calls per claim; the
handbook never cached (date and name in front of it); a letter nobody needs plus a fragile regex;
claims one after another.

**Lever 2 · Schema.** They add `"reason": {"type": "string", "enum": REASONS}` and put `"reason"`
in `required`. Hint ladder: (1) look at how `decision` is defined; (2) the list is `REASONS`;
(3) don't forget `required`.

**Lever 3 · Caching.** `build_request` should return
`[{"type": "text", "text": HANDBOOK, "cache_control": {"type": "ephemeral"}}]` as system and
the date + `claim_text(claim)` as `claim_part`. The name isn't needed any more. Hint ladder:
(1) "What is the very first thing in the request, and does it change per claim?" (2) system can be
a list of blocks; (3) the block format from the hint. If both requests show cache read 0, something
before the handbook still changes. Caches last 5 minutes and are per model.

**Lever 4 · Routing.** Web form + dropdown "changed my mind" → Haiku, everything else → Sonnet.
Expected small: R-01, R-02, R-06, R-07. Why: those are decided by dates and opened/unopened alone;
emails and damage need judgement (defect vs. misuse).

**Lever 5 · Streaming.** It doesn't make calls finish sooner. With the short JSON record, first and
last token are close together – that's expected, not a bug.

**Lever 6 · Parallel.** Typical result: sequential ≈ 45 s, parallel ≈ 12 s. Parallel without warming
writes the cache for nearly every claim; warming first writes it once.

**Lever 7 · Batch.** 50 % off for anything that can wait. Company gateways often don't offer the
Batch API (`lab.via_gateway`); the cost effect is the same.

**Part 5 · Sprint.** Suggested order: `one_call` → `structured` → `cache` → `routing` → `workers`.
A fully optimised run reaches 100 % accuracy at ≈ $0.001 per claim and p50 ≈ 4 s (score in the
thousands). If accuracy drops below 90 %, look at which claims fail – usually R-05, R-08 or R-09 on a
model that's too small, or a schema without `reason`. `effort: "low"` saves tokens and usually keeps
accuracy. Settings identical to v0 show the recorded run instead of calling the API.
The holdout (H-01 refund 23.90, H-02 misuse) is for the end only – no tuning against it.
