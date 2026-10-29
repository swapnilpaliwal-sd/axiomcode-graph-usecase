# axiomcode-graph use cases

A tiny, runnable shop service and the **real** output of every `axiomcode` command run against it.
Each scenario shows the command, the output, and where the result lands. The last scenarios show a call the
graph cannot resolve, and how an agent bridges it with `axiomcode link`.

```
shop/api.py        place_order → OrderService.place
shop/service.py    OrderService.place → price_for, payment.charge (interface), events.emit("order.placed")
shop/events.py     EventBus.emit → fn(payload)          ← a call through a value: the graph cannot see the target
shop/receipts.py   bus.subscribe("order.placed", send_receipt); send_receipt → dispatch
shop/notify.py     dispatch → getattr(module, f"notify_{channel}")(message)   ← a computed name, unresolved too
tests/             test_api (end-to-end), test_pricing, test_notify
```

Run it yourself:

```bash
python3 -m pytest -q          # 4 passed
axiomcode index               # builds .axiomcode/ in ~4 s
axiomcode impact notify_email
```

Every output below is copied verbatim from [`logs/`](logs/).

---

## What it is for

| You want to know | Command | Scenario |
|---|---|---|
| Who calls this, what breaks if I change it, which tests cover it | `axiomcode impact <name>` | [1](#1-impact-on-an-interface-method), [4](#4-the-gap-impact-sees-nothing) |
| How does A reach B, hop by hop, with the code at each call | `axiomcode path <A> <B>` | [5](#5-path-the-chain-is-unknown-not-absent) |
| Which tests do my uncommitted edits reach, and the command to run just those | `axiomcode tests` | [8](#8-after-an-edit-tests-and-impact) |
| How a feature works, explained from a plain-English task | `axiomcode context "<task>" --source` | [2](#2-context-how-does-placing-an-order-send-the-receipt) |
| Record where an unresolved call lands, once the code makes it certain | `axiomcode link <file:line:col> <target>` | [6](#6-the-agent-bridges-the-gap-with-axiomcode-link) |
| See the whole codebase as one interactive page | `axiomcode graph` | [9](#9-where-the-change-shows-up) |

---

## How the graph communicates certainty

Every row in an answer carries a label. An agent should read these labels before it trusts the row.

| Label in the output | Arrow | Meaning | What the agent should do |
|---|---|---|---|
| `[resolved]` | `→` solid | The graph proved this call from the code (types, imports, constructors) | Trust it |
| `registered` (callback) | `→` solid, green | A function passed to something that calls it (`bus.subscribe(…, send_receipt)`) | Trust it |
| `⇢` in `context` | one-of-a-set | One of several targets a dispatch can choose | Expect any of them at runtime |
| `[must change · … a name match]` | — | Same member declared in a supertype; matched by name | Check it, it is usually right |
| `[asserted]` | `- - →` dashed | An agent recorded it with `axiomcode link` | Trust it as much as you trust whoever linked it |
| `to resolve:` + `candidates:` | `···?` dotted | A call through a value. The graph does not know the target. Candidates are *leads* | Read the call. Link it only if the code makes it certain |
| `bound: … lower bound` | — | The answer may miss things behind the unresolved calls | Do not treat the list as complete |
| `verified: ✓ (N edge(s) looked up again)` | — | Every printed edge was re-checked against the graph | — |

The rule for agents: **solid arrows are facts, dashed arrows are claims someone made, dotted arrows are gaps.**

---

## 0. index

```console
$ axiomcode index
building python graph for . … (python 12 files)
tier                 edges
known_edge           13
boundary_lib         11
ambiguous_unknown    5
callback_registered  1
graph at .axiomcode/out/graph.sqlite
real 4.32
```

`ambiguous_unknown 5` is the count of calls the graph could not pin down. Two of them matter for this demo.
Full log: [`logs/00-index.txt`](logs/00-index.txt).

## 1. impact on an interface method

`OrderService` only knows `PaymentGateway`; `CardGateway` is injected by `make_service()`.

```console
$ axiomcode impact CardGateway.charge
1. shop/payments.py:6  [must change · declares the same member in a supertype (a name match: this graph has no override table)]
   → 6      def charge(self, amount: float) -> str: ...
2. shop/service.py:25  [resolved · OrderService.place]
   → 25          self.payment.charge(total)
further away (1 place(s), reached through the places above; no code shown):
   shop/api.py:10  place_order  [hop 2]
tests that reach it (1; no code shown):
   tests/test_api.py:5  test_place_order_sends_email_receipt
verified: ✓ (4 edge(s) looked up again)
```

Grep for `CardGateway.charge` finds nothing, because the code calls `self.payment.charge`. The graph follows
the interface and finds the caller, the abstract declaration that must change with it, and the one test.
Full log: [`logs/04-impact-charge-interface.txt`](logs/04-impact-charge-interface.txt).

## 2. context: "how does placing an order send the receipt?"

```console
$ axiomcode context "how does placing an order send the receipt" --source     # trimmed; full log linked below
how it runs — the call flow … (→ resolved call, ⇢ one of a set; ⚠ a call the graph could not resolve …)
   1 send_receipt                     shop/receipts.py:5
   2   → dispatch                     shop/notify.py:14
   3     ⇢ notify_email               shop/notify.py:6
   4     ⇢ notify_sms                 shop/notify.py:10
   5 place_order                      shop/api.py:10
   6   → make_service                 shop/api.py:6
   8   → OrderService.place           shop/service.py:23
  11     → CardGateway.charge         shop/payments.py:10
  12     → EventBus.emit              shop/events.py:11
           ↺ send_receipt (step 1)
```

Each step comes with its code. `→` is a proven call; `⇢` is one of a set (here the two `notify_*` targets of
the `getattr` dispatch). Full log: [`logs/13-context.txt`](logs/13-context.txt). (This was captured after the
links in scenario 6, which is why steps 3 and 4 and the `↺` appear.)

---

## The gap, and how an agent bridges it

![before](diagrams/01-before-link.png)

## 4. The gap: impact sees nothing

`notify_email` sends every email receipt, and `test_api` exercises it. But it is only ever called through
`getattr(...)(message)`:

```console
$ axiomcode impact notify_email
change: notify_email   [method]
directly touches it: nothing the graph can see — the declaration is used only where it is declared, or through something the parser did not record
tests: 0 of 4 test method(s) reach the change
next: nothing resolved depends on it, so the change is local — read shop/notify.py:6 and edit there
```

This is the dangerous answer: "the change is local, 0 tests." In fact a change here breaks `test_api`.

## 5. path: the chain is UNKNOWN, not absent

```console
$ axiomcode path place_order notify_email
No chain of resolved calls connects place_order and notify_email in either direction (searched 14 edges, depth ≤ 40)
  … the connection is UNKNOWN, not absent
  place_order reaches 1 call(s) through a value:
    `fn()` in EventBus.emit at shop/events.py:13 — the callee is a loop variable
to resolve: 1 call site(s) the answer stopped at — what each reaches is not in it:
    shop/events.py:13:13  fn(payload)  [no_rule]
        candidates: no candidate
    read the call first; when it makes the target certain: `axiomcode link <file:line:col> <target>`
```

And asking about `dispatch` names the second gap, with candidates:

```console
$ axiomcode impact dispatch --unknown
…
to resolve: 1 call site(s) the answer stopped at — what each reaches is not in it:
    shop/notify.py:16:5  handler(message)  [computed_attribute_name:notify_*]
        candidates: notify_email shop/notify.py:6 (named notify_…, the constant part of the computed name); notify_sms shop/notify.py:10 (…)
```

The graph says exactly where it stopped (`file:line:col`), why (`computed_attribute_name:notify_*`) and what it
suspects (candidates). It does **not** guess. Full logs: [`02`](logs/02-path-before.txt), [`03`](logs/03-impact-dispatch-unknown.txt).

## 6. The agent bridges the gap with `axiomcode link`

![workflow](diagrams/03-link-workflow.png)

The agent reads the two sites:

- `events.py:13` `fn(payload)` iterates `self._subs[topic]`. The only `subscribe` in the repo is
  `bus.subscribe("order.placed", send_receipt)`. So the target is `send_receipt`. Certain.
- `notify.py:16` `handler(message)` is `getattr(module, f"notify_{channel}")`. The only functions named `notify_*`
  are `notify_email` and `notify_sms`. Either can run. Link both.

```console
$ axiomcode link shop/events.py:13:13 send_receipt
linked shop/events.py:13:13 `fn` → send_receipt [asserted]; return type unknown, calls on its result stay unknown  — applied to 1 graph(s) in 7 ms

$ axiomcode link shop/notify.py:16:5 notify_email
linked shop/notify.py:16:5 `handler` → notify_email [asserted]; … — applied to 1 graph(s) in 6 ms

$ axiomcode link shop/notify.py:16:5 notify_sms
linked shop/notify.py:16:5 `handler` → notify_sms [asserted]; … — applied to 1 graph(s) in 6 ms
```

No rebuild: each link is applied in a few milliseconds.

![after](diagrams/02-after-link.png)

## 7. Ask again: the same questions now have answers

```console
$ axiomcode impact notify_email
1. shop/notify.py:16  [calls it | asserted · dispatch]
   → 16      handler(message)
further away (4 place(s), reached through the places above; no code shown):
   shop/receipts.py:5  send_receipt  [hop 2]
   shop/events.py:11  EventBus.emit  [hop 3]
   shop/service.py:23  OrderService.place  [hop 4]
   shop/api.py:10  place_order  [hop 5]
tests that reach it (1; no code shown):
   tests/test_api.py:5  test_place_order_sends_email_receipt
verified: ✓ (7 edge(s) looked up again)
to resolve: nothing — 2 site(s) the answer stopped at are settled by links
```

```console
$ axiomcode path place_order notify_email
1. shop/api.py:12      [resolved · hop 1/5 place_order → OrderService.place]
2. shop/service.py:28  [resolved · hop 2/5 OrderService.place → EventBus.emit]
3. shop/events.py:13   [asserted · hop 3/5 EventBus.emit → send_receipt]
4. shop/receipts.py:6  [resolved · hop 4/5 send_receipt → dispatch]
5. shop/notify.py:16   [asserted · hop 5/5 dispatch → notify_email]
verified: ✓ (5 edge(s) looked up again)
```

Every hop says how it is known: three `resolved`, two `asserted`. Full logs: [`09`](logs/09-impact-notify_email-after.txt), [`10`](logs/10-path-after.txt).

| Question | Before link | After link |
|---|---|---|
| `impact notify_email`: callers | 0, "the change is local" | 5 (1 direct, 4 further away) |
| `impact notify_email`: tests | 0 of 4 | `test_api.py:5` |
| `path place_order notify_email` | unknown, stopped at `events.py:13` | 5 hops, 2 asserted |
| `to resolve:` | 1–2 open sites | nothing, settled by links |

## 8. After an edit: tests and impact

Change the body of `notify_email`, then:

```console
$ axiomcode tests
1. tests/test_api.py:5  [test · asserted · hop 6]
   → 5  def test_place_order_sends_email_receipt():
bound: a lower bound: a test reached only by reflection, … is not here
run: pytest tests/test_api.py
```

```console
$ axiomcode impact          # no name: whatever your uncommitted edits changed
your edits: body shop.notify.notify_email
1. shop/notify.py:16  [calls it | asserted · dispatch]
…
```

It picks `test_api` and skips `test_pricing` and `test_notify`. That is correct, and it is only possible because
of the link. Full logs: [`11`](logs/11-tests-after-edit.txt), [`12`](logs/12-impact-uncommitted.txt).

## 9. Where the change shows up

| Where | What you see |
|---|---|
| [`axiomcode-links.tsv`](axiomcode-links.tsv) at the repo root | One row per link (file, line, line hash, callee, caller, target, who, when). **Commit it**: `.axiomcode/` is derived and can be deleted; links survive a rebuild |
| `axiomcode link` (no arguments) | Every link and whether the graph took it (`applied`, `changed`, `moved`) |
| `impact`, `path`, `tests`, `context` | Edges labelled `[asserted]`; `to resolve: nothing — settled by links` |
| `axiomcode graph` | `.axiomcode/graph/graph.html`, the whole codebase as one interactive page |

```console
$ axiomcode link
3 asserted link(s) in axiomcode-links.tsv:
    [applied] shop/events.py:13:13  → send_receipt
    [applied] shop/notify.py:16:5  → notify_email
    [applied] shop/notify.py:16:5  → notify_sms
```

## 10. Links follow the code, and refuse guesses

**The line moves.** Add two lines at the top of `notify.py`; the call moves from line 16 to 18:

```console
$ axiomcode link                 # before the graph refreshes
    [changed] shop/notify.py:16:5  → notify_email  — the line was edited since the graph was built; the next refresh re-validates it (followed if it only moved)
$ axiomcode link                 # after the next query refreshed it
    [moved] shop/notify.py:16:5 (now line 18)  → notify_email  — followed by its text from line 16 to 18
```

**A guess is refused.** `not:<target>` rejects one of the graph's own leads. It refuses a target the graph
never proposed for that site:

```console
$ axiomcode link shop/events.py:13:13 not:notify_sms
axiomcode link: rejected — no by-name or one-of-a-set lead at shop/events.py:13 reaches notify_sms
```

Logs: [`14`](logs/14-link-reject.txt), [`15`](logs/15-link-after-line-moved.txt), [`16`](logs/16-link-followed-after-refresh.txt).

---

## Telling your agent how to use this

Paste into `CLAUDE.md` / `AGENTS.md`:

```markdown
- Before changing a function, run `axiomcode impact <name>`. Before running tests, run `axiomcode tests`.
- Labels: `resolved` / `registered` are proven. `asserted` was recorded by an agent. `to resolve:` is a gap.
- A `bound: … lower bound` line means the list may be incomplete. Do not call a change "local" while
  `to resolve:` lists sites.
- To close a gap: read the call at the `file:line:col`. If the code makes the target certain, run
  `axiomcode link <file:line:col> <target>` (once per possible target). Candidates are leads; never link by rank.
- Commit `axiomcode-links.tsv`.
```

## Rebuild the diagrams

```bash
python3 diagrams/make_diagrams.py     # needs matplotlib
```
