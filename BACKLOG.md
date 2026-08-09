# BACKLOG.md — riddl-models

Open work. Completed items leave: lessons to NOTEBOOK.md, durable facts to
CLAUDE.md. Verified claims carry their evidence so nothing is re-derived.

---

## 1. The 87 remaining warnings, already triaged

Down from 1233. Two whole classes were closed on 2026-08-09 — the five
unwired repositories and four of the eleven adaptor advisories — leaving:

| count | category | verdict |
|------:|----------|---------|
| 79 | domain types/records never referenced | needs per-model judgment |
| 7 | adaptor advisories, all reactive-bbq | **blocked upstream — do not fix** |
| 1 | an unreferenced record | with the 79 |

**The 7 are deliberately left alone and must stay that way until riddl
responds.** Following the advisory makes the model strictly worse: an
`Adaptor` is not a `Streamlet`, and the sink-upstream BFS in
`StreamingValidation` is typed over `Streamlet`, so an adaptor placed in
the path severs the sink's route back to a source. Doing it exactly as
suggested took reactive-bbq from 7 findings to 8. Filed as
`../riddl/task/2026-08-09-adaptor-advisory-conflicts-with-sink-upstream-check.md`.
The other four adaptor sites were fixable precisely because their path is
`entity -> adaptor -> external context` with no internal sink.

**The 79 are not mechanically fixable.** They are standalone vocabulary —
`AcademicTerm`, `TrainerInfo`, `ActionItem`, `DailySchedule` — spread over
48 models. Using one means deciding *where*: a new field on an existing
message, or a capability the model does not expose. knowledge-management
shows why they are left: `SearchQuery` and `SearchResult` plainly imply a
search, but adding one invents a capability rather than repairing it.
Reid's standing instruction covers this: if unsure, leave it, it is only a
usage warning. **10 of the 79 have a near-duplicate declaration**
(`AccountSummary` vs the projector's inline `AccountSummaryView`), where
the fix is to share one shape — the tractable subset. Three of those carry
a doubled suffix (`AccountSummaryViewView`, `DailyRevenueViewView`,
`PolicyMetricsViewView`, 6 sites in 2 files) that is worth fixing on its
own.

`scripts/collect-warnings.py --grep "is unused"` reproduces the list, but
**note it passes `--provide-tips`**, which riddl uses to gate an advisory
tier: 95 further findings appear under it, 89 of them `Initialize<Entity>`
placeholder commands with no `on command` clause. Those are deliberately
not part of the 87 (riddl: "advisory … message types are often defined at
context scope"). Not a blanket delete either — 37 `Initialize*` commands
are genuinely told or sent somewhere.

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

**2026-08-05 — the writer was `../riddl`, not anything here.** Mid session,
181 `.bast` were rewritten (10:09:04–07) from a tree that was clean at session
start. Each differed from `HEAD` by **9 bytes in the container only** — the
length field at `0x14` and the checksum at `0x18`; unbastifying both recovered
**byte-identical** source.

The cause was riddl's `RiddlModelsRoundTripTest` (modified in the `../riddl`
checkout), run there against this corpus and writing `.bast` from riddl's
working-tree build. Four local candidates were tested first and none
reproduced it — not `riddlcValidate`, not `Test/executeTests` at either pin,
not a `build.sbt` touch, and no file watcher exists — because **the writer
was never in this repository**. `../bin/riddlc` had not moved (`md5`
`38b557b3838d…` identical before and after).

So: an unexplained `.bast` diff means look at `../riddl` first. And note the
corollary — the corpus can be rewritten by a build you are not running, so a
diff that appears mid-session is not necessarily yours.

**The decisive check, which costs one command:** regenerate everything and ask
git.

```
./scripts/verify-bast-roundtrip.sh   # bastifies in place, then round-trips
git status --short -- '*.bast'       # empty => committed .bast are correct
```

It came back 187/187 with **zero** `.bast` modified, which proves the
committed bytes are exactly what the staged binary produces. That makes the
rule stronger than this item's original form: a `.bast` diff is only meaningful
if it **survives** a regenerate-and-compare. Restore with
`git checkout -- '*.bast'` (never delete them) and re-run that check before
believing a diff.
