# Isar Coffee – Returns & Warranty Handbook

Version 3 · for the customer care team

This handbook is what the care team works from when a return or warranty claim comes in. Every
claim gets exactly one decision, recorded in the returns database. Use the rules in sections 2–6
in this order, and check the case library in section 9 when you're unsure.

---

## 1. What we decide

For every claim we record four things:

| Field | Values |
|---|---|
| `claim_id` | The ID of the claim, e.g. `R-1042` |
| `decision` | `refund`, `replacement`, `reject` or `need_info` |
| `refund_eur` | The amount we pay back in euros. `0` for every decision except `refund` |
| `reason` | One reason code from the list below |

**Reason codes.** Use exactly these spellings:

| Code | When |
|---|---|
| `within_return_window` | Unopened, unused item returned within 30 days of delivery → refund |
| `outside_return_window` | Unopened item, but more than 30 days after delivery, and no defect → reject |
| `opened_coffee` | Coffee that has been opened and has no quality problem → reject |
| `quality_issue` | Coffee that arrived damaged or stale → replacement |
| `warranty_defect` | Equipment that broke through normal use within 2 years → replacement |
| `misuse` | Equipment damaged by use against the care instructions → reject |
| `missing_proof_of_purchase` | We can't confirm where and when the item was bought → need_info |

Only one reason per claim. If several apply, use the first rule in sections 2–6 that decides the claim.

---

## 2. Proof of purchase

- **Online orders** always have an order number. That is enough proof – we can see the order,
  the delivery date and what the customer paid.
- **Market stand purchases.** Before the online shop existed we sold at the weekend markets
  (Viktualienmarkt, Elisabethmarkt). These customers often write by email. For them we need a
  receipt, a photo of the receipt or a card statement showing the purchase.
- If an email claim has no order number and no proof of purchase, the decision is `need_info`
  with reason `missing_proof_of_purchase`, refund 0. Don't decide anything else yet – we ask for
  the proof first.

---

## 3. Returns within 30 days

- Customers can return **unopened and unused** items within **30 days of delivery**. Count the
  days from the delivery date to the date the claim came in. Day 30 still counts.
- We refund the **price of the returned items**.
- **Shipping.** Orders under €40 pay €4.90 shipping, orders of €40 or more ship for free.
  We refund the €4.90 only if the **whole order** is returned **and** shipping was actually
  charged. Partial returns never get shipping back.
- A return for "changed my mind", "wrong size" or "gift I don't need" is fine, as long as the
  item is unopened and unused and within 30 days.
- After 30 days, an unopened item can't be returned: `reject`, reason `outside_return_window`.
  If the item is broken, it's not a return any more – see the warranty in section 5.

---

## 4. Coffee

- **Opened coffee can't be returned.** Once a bag is opened we can't resell it. "I don't like the
  taste" or "changed my mind" on an opened bag is `reject`, reason `opened_coffee`.
- **Quality problems are the exception.** If the bag arrived torn or not sealed, or the beans
  were stale or past the best-before date on arrival, we send a new bag: `replacement`, reason
  `quality_issue`, refund 0. This applies to opened bags too – customers often only notice once
  they open it.
- Taste is not a quality problem. "Too bitter", "too sour", "not strong enough" on an opened bag
  is `opened_coffee`.
- Unopened coffee follows the normal 30-day return rule in section 3.

---

## 5. Warranty on equipment

- Moka Pot, French Press, Hand Grinder and Milk Frother have a **2-year warranty** from the
  delivery date. The Espresso Cups and the Gasket Set have no warranty (but they can be returned
  unopened within 30 days like everything else).
- A **defect** is something that breaks through normal use. For a defect we send a **new item**:
  `replacement`, reason `warranty_defect`, refund 0. We don't refund the money for a defect.
- **Misuse** is not covered: `reject`, reason `misuse`, refund 0. Section 6 lists what counts as
  misuse for each product.
- If you can't tell from the claim whether it's a defect or misuse, decide on what the customer
  describes. Don't assume misuse the customer didn't mention.

---

## 6. Defect or misuse? Product by product

### Moka Pot (aluminium, 6 cups)
Care instructions: hand wash only with warm water, no dishwasher, no soap residue. Always fill
the bottom with water before heating. Not for induction hobs. Replace the gasket about once a year.

| Sign | Verdict |
|---|---|
| Handle loose, wobbling or came off | defect |
| Safety valve hisses or leaks from new | defect |
| Thread doesn't close properly from new | defect |
| Grey, black or dull inside or outside after washing | misuse – dishwasher |
| Melted gasket, discoloured or warped base | misuse – heated without water |
| Doesn't heat on an induction hob | misuse – not for induction (stated on the product page) |
| Dented or cracked after falling | misuse – dropped |

### French Press (glass and steel, 1 litre)
Care instructions: no boiling water straight from the stove onto a cold jug, no metal spoons in
the glass, dishwasher safe except for the plunger.

| Sign | Verdict |
|---|---|
| Plunger mesh comes loose or the rod bends in normal use | defect |
| Glass jug cracks on its own, without being dropped | defect |
| Glass cracked after pouring boiling water into a cold jug | misuse – heat shock |
| Glass broken after falling | misuse – dropped |
| Plunger rusty after going through the dishwasher | misuse – dishwasher |

### Hand Grinder
Care instructions: only coffee beans, no spices or nuts. Clean with the brush, never with water.

| Sign | Verdict |
|---|---|
| Handle or crank breaks while grinding beans | defect |
| Grind setting slips or won't hold | defect |
| Burrs blocked or broken after grinding spices, nuts or rice | misuse |
| Rust on the burrs after washing with water | misuse |

### Milk Frother
Care instructions: rinse the whisk under the tap, never put the handle in water, use the
batteries in the box or the same type.

| Sign | Verdict |
|---|---|
| Stops working, motor doesn't start with fresh batteries | defect |
| Whisk comes off in normal use | defect |
| Stopped working after the handle was put in water | misuse |

### Espresso Cups (porcelain, set of 2)
No warranty. Arrived broken → treat like a quality problem on arrival: `replacement`, reason
`quality_issue`. Broken later → `reject`, reason `misuse`.

### Gasket Set
A spare part. No warranty. Unopened returns within 30 days as usual.

---

## 7. Coffee and prices

| Product | Price (€) |
|---|---|
| Espresso Classico (250 g) | 8.90 |
| Espresso Classico 1 kg | 29.90 |
| Isar Crema (250 g) | 9.50 |
| Isar Crema 1 kg | 32.90 |
| Decaf (250 g) | 9.90 |
| Decaf 1 kg | 34.90 |
| Moka Pot | 34.90 |
| French Press | 27.90 |
| Gasket Set | 6.90 |
| Hand Grinder | 49.00 |
| Espresso Cups (set of 2) | 19.90 |
| Milk Frother | 24.90 |

Shipping: €4.90 per order, free for orders of €40 or more.

Our coffees, so you can answer questions about them:

- **Espresso Classico** – dark roast, 80 % Brazil, 20 % India Robusta. Chocolate, roasted nuts,
  low acidity. Our most popular coffee for moka pots.
- **Isar Crema** – medium roast, 100 % Arabica from Colombia and Ethiopia. Caramel, red berries,
  a bright finish. Good in the French press and with milk.
- **Decaf** – medium-dark roast, Colombia, decaffeinated with the Swiss Water process (no
  chemicals). Cocoa and brown sugar.

All coffees are roasted in Munich every Tuesday and Friday and shipped within two days. The
best-before date is 12 months after roasting. Bags have a one-way valve and should be stored
closed, dry and away from light.

---

## 8. How to read a claim

Claims come in two ways:

- **Web form** (online shop orders). It has fields: order number, what was ordered, what is being
  claimed, the delivery date, whether the item was opened or used, a reason from a dropdown and
  an optional description. Trust the fields.
- **Email.** Customers who bought at the market stand, or who simply prefer email, write to
  care@isar-coffee.example. Read the whole email. Look for: which product, when and where it
  was bought, what happened, and whether there is an order number or a receipt.

The date the claim came in is the date you count to (section 3).

---

## 9. Case library

Past decisions, for when you're unsure. Each line: what happened → decision, refund, reason.

1. Isar Crema 250 g, unopened, returned 6 days after delivery, the order was only this bag (shipping €4.90 paid) → refund, 14.40, within_return_window
2. Espresso Classico 1 kg, unopened, returned 29 days after delivery, order of €29.90 only → refund, 34.80, within_return_window
3. Decaf 250 g, unopened, 31 days after delivery → reject, 0, outside_return_window
4. Isar Crema 1 kg, opened, "too sour for me" → reject, 0, opened_coffee
5. Espresso Classico 250 g, opened, "changed my mind" → reject, 0, opened_coffee
6. Decaf 250 g, opened, "beans smelled stale when I opened it, roast date 14 months ago" → replacement, 0, quality_issue
7. Isar Crema 250 g, "bag arrived split open, beans all over the parcel" → replacement, 0, quality_issue
8. Moka Pot, 5 months old, "the handle broke off while pouring" → replacement, 0, warranty_defect
9. Moka Pot, 2 weeks old, "valve hisses even with the right amount of water" → replacement, 0, warranty_defect
10. Moka Pot, "I washed it in the dishwasher and now it's dark grey" → reject, 0, misuse
11. Moka Pot, "forgot to put water in, the gasket melted" → reject, 0, misuse
12. Moka Pot, "doesn't work on my new induction hob" → reject, 0, misuse
13. French Press, 1 month old, "the mesh came off the plunger" → replacement, 0, warranty_defect
14. French Press, "dropped it while washing up, glass broke" → reject, 0, misuse
15. French Press, unopened, 12 days after delivery, part of a €46.90 order, only the press returned → refund, 27.90, within_return_window
16. Hand Grinder, 8 months old, "crank snapped while grinding beans" → replacement, 0, warranty_defect
17. Hand Grinder, "I ground some pepper in it and now it's stuck" → reject, 0, misuse
18. Hand Grinder, unopened, 40 days after delivery, "changed my mind" → reject, 0, outside_return_window
19. Milk Frother, 6 months old, "doesn't start, tried new batteries" → replacement, 0, warranty_defect
20. Milk Frother, "dropped it in the sink, now dead" → reject, 0, misuse
21. Espresso Cups, "one cup arrived broken" → replacement, 0, quality_issue
22. Espresso Cups, "broke one when I dropped it" → reject, 0, misuse
23. Espresso Cups, unopened, 8 days, part of a €54.80 order, only the cups returned → refund, 19.90, within_return_window
24. Gasket Set, unopened, 10 days, order of €6.90 only → refund, 11.80, within_return_window
25. Email: "bought a moka pot at your market stand, the handle wobbles", photo of the receipt attached → replacement, 0, warranty_defect
26. Email: "bought coffee at the Elisabethmarkt, it was stale", no receipt, no date → need_info, 0, missing_proof_of_purchase
27. Email: "the French press from your stand cracked", no receipt → need_info, 0, missing_proof_of_purchase
28. Web form: 2 × Decaf 250 g, unopened, 3 days, whole order (€19.80, shipping paid) → refund, 24.70, within_return_window
29. Web form: Moka Pot + Espresso Classico 250 g, both unopened, whole order (€43.80, free shipping), 20 days → refund, 43.80, within_return_window
30. Moka Pot, unopened, gift, 25 days after delivery, order of €34.90 only → refund, 39.80, within_return_window
31. Isar Crema 250 g, unopened, 35 days, "forgot to send it back" → reject, 0, outside_return_window
32. French Press, 23 months old, "glass cracked on its own" → replacement, 0, warranty_defect
33. Hand Grinder, "rusty after I washed it" → reject, 0, misuse
34. Espresso Classico 250 g, "parcel arrived wet, bag soaked" → replacement, 0, quality_issue
35. Web form: Isar Crema 1 kg, unopened, "changed my mind", 2 days, order of €32.90 only → refund, 37.80, within_return_window
36. Email with order number IC-7310: "French press plunger rod bent the first time I used it" → replacement, 0, warranty_defect

---

## 10. Writing to the customer

The decision comes first; the letter only explains it. Keep letters short and friendly:
thank them, say what we decided and why in one or two sentences, and say what happens next
(refund within 5 working days to the original payment method, replacement ships within two days,
or what we need from them). Never promise anything the decision doesn't cover. For misuse,
point to the care instructions without blaming. Sign with "Your Isar Coffee care team".
