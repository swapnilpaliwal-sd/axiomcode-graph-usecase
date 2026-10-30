# Spec → rule → check (the simple version)

Turn one sentence of a spec into a rule, and let the graph check it. Three tiny TypeScript files, one Datalog rule: [`spec.md`](spec.md) becomes [`spec.dl`](spec.dl).

![spec to rule](spec-to-rule.png)

## The spec

> Every function that removes a user also writes to the audit log.

## The code

```ts
// src/db.ts
export function removeUser(id: number) { … }

// src/audit.ts
export function audit(message: string) { … }

// src/users.ts
export function banUser(id: number) {
  removeUser(id);
  audit(`banned ${id}`);      // ✓ audits
}

export function deleteUser(id: number) {
  removeUser(id);             // ✗ forgot to audit
}
```

## The rule

The spec, written as a question to the graph: *which functions call `removeUser` but never call `audit`?*
That is [`spec.dl`](spec.dl):

```prolog
.decl method(id: symbol, name: symbol, file: symbol, line: number)
.input method
.decl calls(caller: symbol, callee: symbol)
.input calls

// f calls a function named `name`.
.decl calls_named(f: symbol, name: symbol)
calls_named(f, name) :- calls(f, t), method(t, name, _, _).

// The rule: calls removeUser, never calls audit.
.decl breaks_the_spec(name: symbol, file: symbol, line: number)
breaks_the_spec(n, file, line) :-
    method(f, n, file, line),
    calls_named(f, "removeUser"),
    !calls_named(f, "audit").
.output breaks_the_spec(IO=stdout)
```

Read `:-` as "if", `,` as "and", `!` as "not".

- `method`: every function in the code.
- `calls`: every call the graph found (`caller` calls `callee`).

[`check.sh`](check.sh) writes those two facts from `.axiomcode/out/graph.sqlite` and runs the rule with
[Soufflé](https://souffle-lang.github.io) (`brew install souffle`).

**No rows means the spec holds.** Each row is a function that breaks it.

## Step 1: Build the graph

```console
$ axiomcode index
building typescript graph for . … (typescript 3 files)
graph at .axiomcode/out/graph.sqlite
```

## Step 2: Check the spec

```console
$ sh check.sh
breaks_the_spec
===============
deleteUser	src/users.ts	9
```

`deleteUser` breaks the spec, at `src/users.ts:9`.

## Step 3: Fix it, check again

```diff
 export function deleteUser(id: number) {
   removeUser(id);
+  audit(`deleted ${id}`);
 }
```

```console
$ axiomcode index
$ sh check.sh
breaks_the_spec
===============
                                    ← no rows: the spec holds
```

## Step 4: Someone adds new code later

```ts
// src/cleanup.ts  (new file)
export function purgeInactive(ids: number[]) {
  for (const id of ids) removeUser(id);      // forgot to audit
}
```

```console
$ axiomcode index
$ sh check.sh
breaks_the_spec
===============
purgeInactive	src/cleanup.ts	3
```

Nobody changed the rule. It caught the new function because of **what the function does** (it calls
`removeUser`), not because of its name. That is the difference between a rule and a test: a rule also covers code
written after the rule.

## Try it

```bash
cd spec-to-rule
axiomcode index
sh check.sh          # shows deleteUser
```

Then add the `audit(...)` line to `deleteUser` and run both commands again.

## Write your own

1. Pick one sentence from your spec (`spec.md`).
2. Name the functions it talks about (here: `removeUser`, `audit`).
3. Write it in `spec.dl` as "the functions that break it" (here: call `removeUser` **and not** `audit`).
4. Run `sh check.sh` after every `axiomcode index`, for example in CI. Any row fails the build.

Raw output of every step: [`logs/`](logs/).
