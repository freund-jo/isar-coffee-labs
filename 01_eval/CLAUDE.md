# Lab 1 · Eval – tutor notes

Notes for Claude. The person sees the same notebook (`Eval.ipynb`, generated from `Eval.py`).
Use these notes to guide, not to hand out answers. The general tutor rules are in the root `CLAUDE.md`.

## What the person should take away

1. Trying a few questions by hand doesn't tell you much. An eval (tasks + checks + several runs) does.
2. Check the answer *and* how it was reached (tool calls), but only as strictly as needed.
3. Read failures before fixing: wrong product key, wrong maths, or an ignored shop rule.
4. Fix with prompt, tool descriptions, tool code and error messages – and measure each change.
5. Some answers can only be graded by a judge model. A judge needs clear, single criteria and
   the facts to judge against.

## Part 3 · Writing tasks

Expected answers (from the catalogue and the shop rules in Part 1):

- 1, "6-cup mokka pot": 44.90, product key `moka-pot-6`.
- 2, "caffeine-free": 9.90, key `decaf`.
- 3, "2 kg of Espresso Classico": 59.80 (2 × 1 kg bag, shop rule 2), key `espresso-classico-1kg`.
  71.20 (8 × 250 g) is the common mistake.
- 4, "6-cup moka pot and two bags of Isar Crema": 44.90 + 2 × 9.50 = 63.90. A plain
  `{"tool": "calculate"}` check is enough.

Common mistakes:
- Only a `number` check, so a guessed price would pass.
- Checking exact tool arguments where any spelling would do. That's too strict.
- Writing 8.9 vs 8.90: both work, the `number` grader compares values.

Hint ladder (go one step at a time):
1. "What would a human from the shop answer? Work it out from the table first."
2. "Which shop rule matters for question 3?"
3. Point to the reference task and the "Only check tool arguments when ..." hint.

## Part 4 · Running

- With the original assistant, usually only the reference task passes. 0–2 of 5 is normal.
- If someone gets 5/5 here, their checks are too loose. Ask what a wrong answer would look like
  and whether their checks would catch it.
- Encourage `inspect(results, "<id>")` on a failing task before they change anything.

## Part 5 · Fixing

Root causes the person should find (don't list them – let them discover them via `inspect`):
- System prompt: no role, no catalogue keys, no shop rules → wrong keys, the 2 kg rule is ignored,
  and refunds or complaints aren't handled.
- Tool descriptions are just the names → Claude can't know valid keys or which operators exist.
- `get_product` only lowercases and swaps spaces for hyphens → "mokka pot", "6-cup moka pot" fail.
- The error is a bare `KeyError('...')` → Claude can't recover. A good error lists the valid keys.
- `calculate` returns `None` for unknown operators and doesn't round.

Good questions to ask: "Which product key did it try?", "Where could Claude have learned the
right key?", "What does Claude see when the lookup fails?"

Done when every task passes at least 4/5 runs.

## Part 6 · Judge

- The judge prompt needs the question, the answer and one criterion. It returns `(ok, reason)`,
  using `output_config={"format": JUDGE_SCHEMA}` and `json.loads` on the text block.
- If their judge says PASS to the bad sample answer: is the criterion in the prompt? Does the
  judge know what the shop sells?
- Task 5 (€50 starter set), one criterion each: recommends a moka pot and a coffee; total
  ≤ €50 (Moka Pot 3-Cup + any 250 g coffee = €43.80–44.80); only catalogue products.
- Task 6 (angry customer): polite; no refund promise; points to the returns form (shop rule 4).
  This only passes if the system prompt from Part 5 includes rule 4.
- Common mistake: one criterion that bundles three things, so a FAIL doesn't say what went wrong.

## Extensions

All optional. For "compare models": `run_eval(tasks, runs=3, model=lab.SONNET)`. Opus costs
about 40× Haiku per token, so warn before running it many times.
