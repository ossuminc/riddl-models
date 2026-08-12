# What disqualifies a model from being simulated, and from being generated

## How to read this, and a correction

An earlier version of this document derived its rules from
`../RIDDL-Tools-To-Do-List.md` and claimed they were "derived, not invented".
That was wrong twice over, and the corrections shape everything below:

1. **The to-do list is a list of CHANGES.** It is necessary but nowhere near
   sufficient, and it does not define "simulatable" or "generatable" at all.
2. **The right question is not "what features does the tool support".** It is
   **what would instantly disqualify a model** from being simulated or
   generated. Absence of the disqualifiers is the definition. Enumerating a
   tool's current feature support answers a different and much weaker
   question — and in the simulator's case an out-of-date one, since the
   simulator *must* eventually compile every statement type; where it does
   not, that is a simulator gap, not a language rule.

The pipeline both tools share is: **text → validate with zero messages →
AST → run**. BAST is only a performance-optimised way to get an AST into
memory; it is not itself a requirement. **Everything that matters is the
quality of the AST.**

Sources: `../RIDDL-Computational-Model.md` — 40 `Must preserve` clauses, one
per definition, under each `§X.8 Degrees of freedom` — is the authority for
generation. The simulation gate is reasoned from the same document plus the
engine's own entry conditions in `synapify/sim-engine/`.

## The simulation gate

Synapify's engine gates on one thing directly: `loadModel` and
`createSimulation` return `Left` when `result.hasErrors`. Everything else is
a property of the AST that would make a discrete-event run meaningless.

| # | Disqualifier | Why it stops a simulation | Checked by riddlc today? |
|---|---|---|---|
| S1 | Any validation **error** | The engine refuses the model outright | yes — hard gate |
| S2 | A handler with no executable statements | A message arrives and nothing happens; the processor is inert | yes (`has no executable statements`) |
| S3 | A `???` body | Nothing to execute; "known to be incomplete" | partly — `???` is *exempted* from other checks, so it hides |
| S4 | An inlet or outlet not joined by a connector | A message is emitted into nothing, or a port never receives | yes (`is not connected`, `has no connections to any connector`) |
| S5 | A **cycle** in the connector graph | Messages circulate forever; the run never settles | **NO — no cycle check exists** |
| S6 | A sink with no upstream source | Never receives anything; the branch is dead | yes |
| S7 | A source with no downstream sink | Produces into the void | yes |
| S8 | A command no handler handles | An injected message has no effect | advisory only (`--provide-tips`) |
| S9 | An entity with no state, or no handler | Nothing to hold, or nothing to do | partly |

S5 is the notable hole: riddlc has no cycle detection, and a cyclic
connector graph is exactly the model a simulator cannot finish.

## The generation gate

`§0.3` ruling 2 sets the shape: riddlg generates framework, structure and
types **deterministically**, and emits `[[AI FILL: …]]` wherever the model is
vague, for an AI to complete **from surrounding model context**. So the
generation gate has two halves — what must be structurally present, and what
must carry enough meaning for the AI tier to act on.

| # | Disqualifier | Why it stops generation |
|---|---|---|
| G1 | Any validation **error** | Nothing downstream is trustworthy |
| G2 | A definition missing what its `§X.8 Must preserve` names | The generator cannot emit a conforming artifact. Examples from the 40: a **Type** must keep every constraint (bounds, patterns, ranges, precision, cardinality) and union discriminability; a **Function** must keep its signature, described behaviour and purity; a **Repository** must keep its schema shape and its command/query→Result contract; a **Use Case** must keep step structure and each composite's order semantics |
| G3 | Descriptions that restate the identifier | The deterministic tier emits an AI FILL marker and the AI tier has no context to fill it. `orderId` described as `\|Order ID.` is worse than useless — it satisfies a presence check while starving the thing the description exists for |
| G4 | Missing Terms | Terms are in the AI-context inclusion census and become hover-docs in generated code |
| G5 | An Author with no contact data | `§B5` requires generated faults to carry "Notify: ⟨author⟩" with contact details |
| G6 | Vague steps with no describing prose | AI translation blocks and falls to a human; some is intended, wholesale vagueness is not |

**What is deliberately NOT a generation input** (the AI-context exclusion
census): comments — author-to-author communication, and a stale
"TODO: this is wrong" must never steer generation; URL description content —
appendix material; and attachments — docs and tooling only.

## What this means for reactive-bbq

reactive-bbq is the reference model for both tools, so it must clear both
gates. `ReactiveBbqCompletenessTest` asserts the checkable ones. In priority
order, from the decisions of 2026-08-12:

1. **Zero messages of any kind**, including zero deprecation warnings. The
   model is canonical, and the suite pins that.
2. **Every description carries real domain intent.** This is the single
   largest item and the most important for generatability — G3. Restating
   the identifier is treated as a defect, not a pass.
3. **No `???`**, no inert handlers, no unconnected ports, no cycles.
4. **Every statement and definition kind exercised** — once each is enough.
   Type expressions are used as the domain warrants rather than exhaustively;
   missing *statements and definitions* matter far more than missing type
   expressions.

Humans mostly read generated documentation rather than the model source,
which is a further argument for G3: the docs are only as good as the
descriptions they are built from.

## Upstream

S5 (cycle detection) and a run-ending summary — "this model is / is not fit
for simulation, for generation, and why not" — are proposed to riddl in
`../riddl/task/`.
