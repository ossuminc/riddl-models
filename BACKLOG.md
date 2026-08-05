# BACKLOG.md — riddl-models

Open work. Completed items leave: lessons to NOTEBOOK.md, durable facts to
CLAUDE.md. Verified claims carry their evidence so nothing is re-derived.

---

## 1. Upgrade to riddlc 2.0.0-rc.9-54 (next up)

`build.sbt` pins `riddlVersion = "2.0.0-rc.9-48-fdc5c171"`, but
`../bin/riddlc` was restaged to **rc.9-54** on 2026-08-04 22:35 and local
ivy already holds `riddl-language_3` at rc.9-51, rc.9-52 and **rc.9-54**.

**Already verified against the rc.9-54 binary** (it is what `riddlcPath`
resolves to, so the last full run used it): 187 models validate, 189 test
cases pass, round trip 187/187. So the upgrade is a version bump, not a
migration — but confirm rather than assume.

What the restage carries (`riddl` `b163d3c85`, `64b7b4134`): `invariant X`
accepted in conditions, plus a **BAST byte-stream corruption fix for
`require invariant X`** that had never round-tripped. That fix does not
touch this corpus — `grep -rc 'invariant'` over all `*.riddl` returns **0
occurrences**, so no `.bast` here was affected.

Bump `riddlVersion` (one value pins binary *and* the test-suite libraries),
then `sbt checkAll` and the round trip.

## 2. Pattern templates: 2 of 7 validate as whole models

`scripts/verify-templates.py` gates on **parse**, and all 7 pass. Under
`--validate` only 2 do (`repository`, `read-model`).

The remaining findings split two ways, and only the first is actionable:

- **Real**: entity templates have no `on query` clause, so nothing can read
  them. Worth adding.
- **Inherent to being a fragment**: "declare the Id type in the containing
  context" is impossible when the template *is* the entity, and a template
  cannot connect its own outlet.

Decide whether `--validate` should ever become a gate, or stay advisory.
Findings naming a scaffold definition are already classified out, so what
`--validate` reports is genuinely about the template.

## 3. Pattern examples diverge from canonical formatting (deliberate)

`patterns/entity/*/example.riddl` differ from `riddlc prettify` output by
**151 lines** — hand-wrapped alternations, `Decimal(12, 2)` spacing. They
are documentation, and canonicalising would emit 341-character alternations
and two ports per line.

They are excluded from `scripts/verify-bast-roundtrip.sh` for that reason;
their `.bast` are still regenerated. Revisit if prettify's port/alternation
formatting improves — riddl has recorded that **formatting waits for the 2.0
release** (`fdc5c1718`).

## 4. `main` stays on 1.x until riddl 2.0 ships

`origin/main` is **72 commits behind** `release/2` and still carries
`state X of type Y`. Reid's decision, 2026-08-04: leave it. `release/2` pins
a staged, unpublished RC, so merging would make the default branch depend on
something nobody can resolve.

Synapify reads `release/2` and has a settings panel for it. **Merge when
riddl 2.0 ships**, not before. Full reasoning in
`task/done/main-still-1x-syntax-breaks-consumers.md`.

## 5. `sbt test` is a weak gate for model edits

sbt 2 routes `test` to `testQuick`, which skips tests it believes unchanged,
and the suite reads `.riddl` files at **run** time — so sbt never sees a
model edit as an input. A second `sbt test` reports success having run
nothing.

`sbt checkAll` (`riddlcValidate` then `Test/executeTests`) forces all 189
and is the command to trust. Could be improved by declaring the model files
as task inputs so sbt invalidates properly.

## 6. No CI in this repository

`.github/` contains only `FUNDING.yml`. Every gate runs locally.

riddl's own CI validates this corpus externally via
`validate_external_riddl.py`, but that will not catch template rot — the
templates are not parseable models.

A workflow running `sbt checkAll` on push needs the pinned riddlc to be
resolvable, so it is blocked until riddl 2.0 publishes (or the workflow
builds riddl from source).

## 7. Watch: staged binary swaps invalidate `.bast` silently

On 2026-08-04 the `.bast` committed at 21:11 were stale by 22:27 with no
source change — because `../bin/riddlc` was restaged underneath. Bastify is
deterministic (two consecutive runs produce identical bytes; verified by
`md5`), so a `.bast` diff with clean `.riddl` means **the binary moved**,
not that anything is wrong with the models.

After any restage: regenerate `.bast`, re-run the round trip, commit.
