# Code Generator

A RIDDL model whose subject is how you generate code for a RIDDL model.

This is dogfooding in the sharpest available sense: if RIDDL cannot
express the design of a RIDDL code generator, that is a finding about
RIDDL, not an excuse to reach for another notation. The intended reader
is a future session building a *new* generator — a TypeScript/Effect
one, a Pekko/Scala one, or whatever a client needs next — so this
document explains what each context is for and what each stage owes,
not what any particular product (riddlg included) does with them.

## The seven contexts, in pipeline order

**`Intake`** loads the model, from source or from a `.bast`, and
applies the generability bar: a model with any Error, or any warning
of class `Completeness`, `Missing` or `Usage`, is refused outright.
Code cannot be generated from unstated intent, so this bar is stricter
than riddlc's own actionability threshold, and it is the one place a
run can end before anything is planned.

**`Naming`** is pure functions, no state. It derives the output
package or namespace for every definition from the domain/context
hierarchy, applies `option namespace` where a scope overrides the
derived path, and sanitizes identifiers for the target language. It
holds no aggregates because naming has no lifecycle of its own.

**`Planning`** holds the `LoweringRule` and `TargetProfile`
repositories and is the only context where a target is visible. For
each definition, it selects the paradigm the target's profile names
for that definition's kind, consults the matching lowering rule, and
produces the planned artifact list. Everything upstream and
downstream of `Planning` is target-agnostic by construction.
**Before copying this structure, know its real status**: the
catalogue's rules live as prose in `LoweringCatalogue`'s
`described as`, not as RIDDL definitions `LowerDefinition` actually
references, so nothing here mechanically checks that consultation
happens or that every definition kind has a rule — see
`LowerDefinition`'s own note in `PlanningContext.riddl` for what a
real implementation still owes.

**`SpecEmission`** emits the test suite derived from the model. It is
necessarily red: the suite states what the filled code must do, and
nothing has filled it yet. Red here is the design, not a regression —
it mirrors a generator whose pass-1 gate runs before behaviour is
assertable.

**`CodeEmission`** emits structure and headers — the nearest scope's
copyright, verbatim, in the target's comment syntax — opens
`[[AI FILL]]` holes wherever the language deliberately leaves prose,
and records a `Decision` wherever a non-obvious choice was made and
why. Its `Artifact` entity tracks each file through
Planned → Emitted → Filled → Verified.

**`HoleFilling`** assembles each hole's *local* fill context — the
enclosing processor, the artifact's code so far, and the declarations
in scope — rather than the entire model, because that local slice is
the difference between a fill that works and one that hallucinates.
Holes come from exactly two places in the grammar: the `do`/`prompt`
statement's string, and an unascribed `prompt`. Conditions and
branching are not holes; 2.0's typed conditions and structured match
patterns already moved that work into the deterministic tier.

**`Proving`** runs the two-gate cycle: pass-1 (compiles, augments,
boots — behaviour not asserted) and pass-2 (the generated suite goes
green). A failed pass-2 emits `ProofFailed`, which `HoleFilling`
answers by reopening the named holes and refilling them. The retry is
an event cycle, not a loop construct, and it is bounded by an attempt
count on `Hole` so an AI-backed fill/prove cycle cannot run away.

## The precedence of representations

"Generic" here does not mean parametric — RIDDL has no generics, and
that turns out not to matter. It means the model generalizes over the
*kinds of computing abstraction* a target can offer, ranked by how much
of a RIDDL processor's requirements each supplies natively, so a
generator can take the highest one available before building the rest
as a facade.

The admission test is encapsulation: data and behaviour bundled in one
unit. Anything short of that cannot receive a RIDDL Entity at all —
which is why Entity-Component-System and tuple-space/Linda are excluded
outright rather than ranked; both deliberately separate state from
behaviour. Among paradigms that pass admission, three tiers are the
ones a generator author will actually meet:

- **Actor** — encapsulation, serial per-identity execution, addressable
  identity and channel-only interaction, all native. This is first
  because a RIDDL processor already *is* an actor: it consumes messages
  one at a time per identity, runs in parallel across identities, and
  interacts only over abstract channels using a closed set of 19
  statements. Nothing has to be built to get here.
- **Bean/component** — encapsulation and container-managed addressing
  are native; serial execution and channel semantics are not, so the
  generator (or a runtime library) must supply a facade for both.
- **Object** — only encapsulation is native. Every other guarantee —
  mailbox ordering, addressability, asynchronous channels — is owed as
  hand-written scaffolding.

A target's `TargetProfile` names, per RIDDL processor kind, the
highest tier it reaches, and every gap below that tier is a facade the
generator must emit — not a reason to refuse the target. A missing
event-sourcing library is a cost the generator can pay by emitting the
journal itself, not a disqualification; only failing encapsulation
disqualifies, because there is no boundary to generate code into.

## How to add a target

Write a `TargetProfile`, not a model. A profile is a small record
naming, per RIDDL processor kind, the paradigm the target supplies and
the capability gaps it must fill. Adding a target this way adds one
profile and reuses every lowering rule already exercised by another
target on the same paradigm tier — a second bean-tier target, for
instance, resolves to the same rules a first one does. Only where a
target's own idioms genuinely differ — import lines, build scaffolding
— does it need its own emission templates; that is emission, not
lowering, and belongs beside the templates, not inside the
`LoweringRule` catalogue.

## What is deliberately absent

- **riddlg's product surface.** Auth, tiering, freemium gating, serve
  mode, MCP and AI-provider plumbing are riddlg-the-product, not code
  generation. A bespoke client generator reproduces none of them.
- **Per-target concrete models.** One model, plus profiles and
  templates — never a second copy of this domain per target.
- **A generated-source domain.** An earlier draft modelled the
  generated system as a second domain; it was retired because a
  generic AST-per-language is enormous and teaches nothing, and the
  runtime behaviours it would hold (single-writer per identity,
  ordered mailbox) are properties of a *running* system, not of text.

No `## NAICS Code` section appears in this README. Models under
`tooling/` describe our own toolchain rather than an industry, so
there is no classification to give — Reid's ruling, 2026-08-26.
