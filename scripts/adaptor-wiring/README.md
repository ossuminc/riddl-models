# Adaptor-wiring campaign tooling

Four scripts for BACKLOG #33 — giving the corpus's placeholder adaptors real
integrations. They were rebuilt from scratch in three consecutive sessions
before being tracked here; do not let them drift back into a scratchpad.

Everything reads `riddlc dump --json` from **stdout alone** (stderr carries
diagnostics and concatenating the two gives `JSONDecodeError: Extra data`).
Nothing parses RIDDL with a regex — see CLAUDE.md, "use riddlc, do not parse
RIDDL with regex", and the nine defects one session of that produced.

`RIDDLC` defaults to `../bin/riddlc` relative to the repository root, and a
relative override is resolved the same way, because these scripts change
directory per model. On a PUBLISHED pin that staged binary is **not** the one
the build uses; pass the cached one explicitly:

```bash
V=$(sed -n 's/.*riddlVersion = "\(.*\)"/\1/p' build.sbt)
RIDDLC=~/.cache/riddlc/$V/bin/riddlc python3 scripts/adaptor-wiring/census.py
```

| script | does |
|---|---|
| `census.py [substring]` | JSONL of every command owned by an **external** context that nothing drives |
| `plan.py <census.jsonl>` | classifies each pair `SETUP` / `INSERT` / `BUILD` by the state of its outbound adaptor |
| `dig.py <model> <Ctx> <Cmd,...>` | the commands to drive and every internal event that could drive them, with briefs — for CHOOSING the source event |
| `wire.py <spec.jsonl> [--dry]` | applies the setup path, transactionally per model |

## The census's one trap

A command counts as driven by **either** a `tell`/`send`/`forward` message ref
**or** a `let`-statement's `declaredType`. The wiring idiom is

```riddl
let item0: type Far.Cmd = prompt("...")
send item0 to outlet Ctx.ToFar.ToFarOut
```

and a `send` of a **bound value carries no message ref at all** — its message
is `{"value": "item0"}`. A census counting only send refs reported all twelve
already-wired payment models as unwired and would have had that session wire
them twice.

**Reconcile, every time.** The models a previous batch wired must come back
CLEAR, and the drop in the total must equal the number of commands wired. That
agreement is the evidence the census is live — the same standard as canarying
the warning sweep. A census that reports nothing is indistinguishable from a
clean corpus.

## `wire.py` spec format

One JSON object per line:

```json
{"model":"sector/subsector/name","ctx":"ExternalCtx","qualify":false,
 "keep":["CommandWithNoTrigger"],
 "clauses":[{"event":"Entity.SomethingHappened",
             "sends":[["FarCommand","why this event is the trigger"]]}]}
```

- `clauses` — one per **source event**; a handler dispatches on message TYPE,
  so an event gets exactly one clause and a second message to the same target
  rides it as another `let`/`send` pair.
- `keep` — commands left in the alternation and the boundary handler but
  **not** given a trigger, because the model has no event for them. Their
  placeholder clause stays; that is the one case where a dead placeholder is
  deliberate.
- `qualify` — write alternation members as `Ctx.Command`. Needed wherever the
  bare name also exists internally (customs-brokerage has `SubmitEntry` on
  both `Entry` and `CBPAceService`), otherwise `ref-ambiguous`.

It snapshots every file it will touch, applies all of a model's pairs,
validates with `--provide-tips` at every severity, and **restores the snapshot
on any finding**. A model is therefore either fully wired or untouched.
