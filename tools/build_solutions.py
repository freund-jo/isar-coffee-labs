"""Builds the solution notebooks from the lab notebooks.

    python3 tools/build_solutions.py

Reads 01_eval/Eval.ipynb, swaps the ✏️ blocks for the solutions and writes
Eval_solution.ipynb. Fails loudly if a block isn't found, so the solution can't silently drift
from the exercise.
"""

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LABS = HERE.parent

FLAWED_AGENT = '''# 1. System prompt
SYSTEM_PROMPT = "You are a helpful assistant."

# 2. Tool code
def get_product(product):
    return CATALOG[product.lower()]

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
'''

FIXED_AGENT = '''# 1. System prompt: role, product names, shop rules
SYSTEM_PROMPT = """You are the shop assistant of Isar Coffee, a coffee shop in Munich that sells
coffee beans, a moka pot, a French press and a few accessories.

Rules:
- Always look up prices with get_product. Never guess a price.
- Do all arithmetic with calculate.
- Customers use their own words. Map them to a product name from the catalogue and say which
  product you used, e.g. "1kg bag of Classico" -> "Espresso Classico 1 kg", "caffeine-free" -> "Decaf".
- Shipping costs €4.90 per order. Orders of €40 or more ship for free. When the customer asks what
  they pay in total or including shipping, add shipping if it applies and say whether it was added.
- Only recommend products from the catalogue. If something isn't sold, say so and don't invent a price.
- You can't decide refunds. For returns and complaints, apologise and point the customer to the
  returns form at isar-coffee.example/returns.
- Answer briefly. Show prices in euros with two decimals, e.g. €8.90."""

# 2. Tool code: forgiving lookup, helpful errors, rounding
def get_product(product):
    name = " ".join(product.lower().replace("mokka", "moka").replace("1kg", "1 kg").split())
    for candidate in (name, name.removesuffix("s")):
        if candidate in CATALOG:
            return CATALOG[candidate]
    raise ValueError(f"Unknown product '{product}'. Products: {', '.join(CATALOG)}. "
                     "Retry with the closest name, or tell the customer we don't sell it.")

def calculate(op, a, b):
    if op not in ("+", "-", "*", "/"):
        raise ValueError("Unknown operator. Use one of: + - * /")
    result = {"+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b, "/": lambda: a / b}[op]()
    return round(result, 2)

# 3. Tool descriptions: what the tool does, valid inputs, what comes back
TOOL_SPECS = [
    {
        "name": "get_product",
        "description": ("Look up the price in euros of ONE product by its catalogue name. Call it once per product. "
                        "Products: " + ", ".join(CATALOG) + ". "
                        "Coffees without '1 kg' are 250 g bags. Returns the price, or an error listing the products."),
        "input_schema": {
            "type": "object",
            "properties": {"product": {"type": "string",
                                       "description": "A product name from the catalogue, e.g. 'Moka Pot' or 'Espresso Classico 1 kg'."}},
            "required": ["product"],
        },
    },
    {
        "name": "calculate",
        "description": ("Do one arithmetic operation on two numbers and return the result, rounded to "
                        "2 decimals. Use it for all maths. For several steps, call it several times."),
        "input_schema": {
            "type": "object",
            "properties": {
                "op": {"type": "string", "enum": ["+", "-", "*", "/"], "description": "The operator."},
                "a": {"type": "number", "description": "First number, e.g. a price."},
                "b": {"type": "number", "description": "Second number, e.g. a quantity."},
            },
            "required": ["op", "a", "b"],
        },
    },
]
'''

EVAL_SWAPS = [
    # Part 3 – tasks
    (
        """    # Template – copy it once for each question:
    # {
    #     "id": "...",
    #     "query": "...",
    #     "checks": [
    #         {"type": "...", "expected": ...},
    #     ],
    # },
""",
        """    {
        "id": "classico_1kg",
        "query": "How much is a 1kg bag of Classico?",
        "checks": [
            {"type": "number", "expected": 29.90},
            {"type": "tool", "expected": {"tool": "get_product", "args": {"product": "espresso classico 1 kg"}}},
        ],
    },
    {
        "id": "caffeine_free",
        "query": "Do you have caffeine-free coffee? What does it cost?",
        "checks": [
            {"type": "number", "expected": 9.90},
            {"type": "tool", "expected": {"tool": "get_product", "args": {"product": "decaf"}}},
        ],
    },
    {
        "id": "with_shipping",
        "query": "What do I pay for a French press, including shipping?",
        "checks": [
            {"type": "number", "expected": 32.80},
            {"type": "tool", "expected": {"tool": "get_product", "args": {"product": "french press"}}},
        ],
    },
    {
        "id": "basket_total",
        "query": "A French press and two bags of Isar Crema – what's my total?",
        "checks": [
            {"type": "number", "expected": 46.90},
            {"type": "tool", "expected": {"tool": "calculate"}},
        ],
    },
""",
    ),
    # Part 5 – improved assistant
    ("# ✏️ YOUR TURN – improve the assistant here\n\n" + FLAWED_AGENT,
     "# SOLUTION – improved assistant\n\n" + FIXED_AGENT),
    # Part 6 – judge criteria
    (
        """        "query": "I have €50 and want to start making coffee at home. What should I buy?",
        "checks": [
            # {"type": "judge", "expected": "..."},
        ],""",
        """        "query": "I have €50 and want to start making coffee at home. What should I buy?",
        "checks": [
            {"type": "judge", "expected": "The answer recommends a coffee maker (moka pot or French press) and at least one coffee."},
            {"type": "judge", "expected": "The recommended items cost €50 or less in total, including shipping if it applies."},
            {"type": "judge", "expected": "The answer only mentions products from the shop catalogue."},
        ],""",
    ),
    (
        """        "query": "Your coffee tastes awful and I want my money back NOW.",
        "checks": [
            # {"type": "judge", "expected": "..."},
        ],""",
        """        "query": "Your coffee tastes awful and I want my money back NOW.",
        "checks": [
            {"type": "judge", "expected": "The answer stays polite and calm."},
            {"type": "judge", "expected": "The answer does not promise or confirm a refund."},
            {"type": "judge", "expected": "The answer points the customer to the returns form."},
        ],""",
    ),
]


INFERENCE_SWAPS = [
    (
        """            "refund_eur": {"type": "number"},
        },
        "required": ["claim_id", "decision", "refund_eur"],""",
        """            "refund_eur": {"type": "number"},
            "reason": {"type": "string", "enum": REASONS},
        },
        "required": ["claim_id", "decision", "refund_eur", "reason"],""",
    ),
    (
        """    system = f"Today is {claim['received']}. You are writing to {claim['customer']}.\\n\\n" + HANDBOOK
    claim_part = claim_text(claim)
    return system, claim_part""",
        """    system = [{"type": "text", "text": HANDBOOK, "cache_control": {"type": "ephemeral"}}]
    claim_part = f"Today is {claim['received']}.\\n\\n" + claim_text(claim)
    return system, claim_part""",
    ),
    (
        """def pick_model(claim):
    return lab.OPUS""",
        """def pick_model(claim):
    if claim["channel"] == "form" and claim.get("dropdown") == "changed my mind":
        return lab.HAIKU
    return lab.SONNET""",
    ),
    (
        """    "one_call": False,      # Lever 1: one call instead of four
    "structured": False,    # Lever 2: JSON record instead of a letter
    "cache": False,         # Lever 3: build_request with the cached handbook
    "routing": False,       # Lever 4: pick_model instead of one model for everything
    "model": "opus",        # the model when routing is off: "haiku", "sonnet" or "opus"
    "effort": None,         # optional: "low", "medium" or "high" – less thinking, fewer tokens
    "workers": 0,           # Lever 6: claims at the same time (0 = one after another)""",
        """    "one_call": True,       # Lever 1: one call instead of four
    "structured": True,     # Lever 2: JSON record instead of a letter
    "cache": True,          # Lever 3: build_request with the cached handbook
    "routing": True,        # Lever 4: pick_model instead of one model for everything
    "model": "opus",        # the model when routing is off: "haiku", "sonnet" or "opus"
    "effort": "low",        # optional: "low", "medium" or "high" – less thinking, fewer tokens
    "workers": 8,           # Lever 6: claims at the same time (0 = one after another)""",
    ),
    ("RUN_HOLDOUT = False\n", "RUN_HOLDOUT = True\n"),
]


def build(src: pathlib.Path, dst: pathlib.Path, swaps, title: str) -> None:
    nb = json.loads(src.read_text(encoding="utf-8"))
    for old, new in swaps:
        cells = [c for c in nb["cells"] if old in "".join(c["source"])]
        if len(cells) != 1:
            sys.exit(f"Block not found in exactly one cell of {src.name}:\n{old[:120]}")
        cells[0]["source"] = "".join(cells[0]["source"]).replace(old, new).splitlines(keepends=True)
    first = nb["cells"][0]
    first["source"] = "".join(first["source"]).replace(title, title + " — solution", 1).splitlines(keepends=True)
    for c in nb["cells"]:
        c["metadata"] = {}
        if c["cell_type"] == "code":
            c["outputs"], c["execution_count"] = [], None
    dst.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", dst)


if __name__ == "__main__":
    build(LABS / "01_eval" / "Eval.ipynb", LABS / "01_eval" / "Eval_solution.ipynb", EVAL_SWAPS, "# Lab 1 · Eval")
    build(LABS / "02_inference" / "Inference.ipynb", LABS / "02_inference" / "Inference_solution.ipynb",
          INFERENCE_SWAPS, "# Lab 2 · Inference")
