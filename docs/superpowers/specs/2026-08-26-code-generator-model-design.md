# Design: a generic RIDDL code generator, modelled in RIDDL

**Date:** 2026-08-26
**Branch:** `release/2`
**riddlc:** `2.0.0-rc.26` (published; `riddlcPath := None`)
**Status:** design approved in conversation; not yet implemented

---

## 1. What this is

A RIDDL model whose subject is **how you generate code for a RIDDL model**.
It is dogfooding in the sharpest available sense: if RIDDL cannot express the
design of a RIDDL code generator, that is a finding about RIDDL.

Its intended reader is a future AI session building a *new* generator — the
TypeScript/Effect one, the Pekko/Scala one, or whatever a client needs. The
model must tell that reader what a generator is made of and what each stage
owes, without being a description of riddlg-the-product.

### Reid's brief, in one line

> Can we define what a riddl code generator's design is?

---

## 2. Decisions taken, and why

Each of these was settled in conversation on 2026-08-26. They are recorded
with their reasoning because the reasoning is what a later session needs in
order to revisit them safely.

### 2.1 One domain, not two

The brief originally proposed two domains — the generator, and the generated
source code — with a strong separation. **Reid retired this himself** during
design:

> I don't think we can generically model the target system as a separate
> domain or context. The design is only for the production of the source code
> corresponding to a RIDDL model so what's really important is just that: how
> do you generate code for a riddl model.

So: **one domain.** A "generated source code" domain would have had to be
either an AST for every target language (enormous, and it teaches a generator
builder nothing) or a set of runtime behaviours (`single-writer per identity`,
`ordered mailbox`) that are properties of a *running system*, not of text.

### 2.2 The eight CM aspects are NOT model data

An earlier draft proposed representing the CM document's eight aspects as
required fields on a per-definition structure, so that riddlc's completeness
checking would enforce them. **Reid rejected this, correctly:**

> Explain how those eight aspects would be represented and what code would be
> generated for the code generator's model that include "free-to-choose" or
> "required capabilities" or "degrees of freedom". These are lofty high level
> goals that aren't relevant to software design.

Taking the proposal seriously answers it: a field `degreesOfFreedom: String*`
lowers to a list-of-strings field, a getter and a column. Nothing branches on
it, no emitted artifact differs, and the content already exists — better
written — in the CM document. It would have been 40 sections of prose retyped
into RIDDL fields and called a design.

**Where they actually belong:** "must preserve" and "degrees of freedom" are
*acceptance criteria for the generator's output*. They are satisfied by what
the emission logic does, and their home in the model is a sentence in
`described as` on the handler that does it.

**The one narrow exception**, agreed: a handful of CM rulings are genuine
*decisions* with a condition and two outcomes — "a cross-context connector
lowers to a persistent channel" is one, and riddlg currently defaults it the
wrong way (riddl-generator BACKLOG item 6). Those become invariants on the
lowering that makes the choice, because a generated invariant check is real
code.

**Primary source:** riddlg's `release/1` branch, not the CM document. Reid:
*"I would expect that the design and code in riddlg's release/1 branch to be
VASTLY more relevant to the generic design than anything in the CM."* The CM
supplies rules; riddlg supplies the design.

### 2.3 Genericity is expressed as required capabilities

RIDDL has no generics, so "entity → actor | object | bean" cannot be
parameterised. The model therefore does not name a target construct at all.
Each lowering states the **capabilities** its construct requires —
single-writer per identity, ordered mailbox, durable append-only journal,
location-transparent addressing — and a target profile declares which the
platform natively provides. The decision is then a function of the two: use
the native construct, or emit a facade that supplies the missing guarantee.

This is the CM's own escape hatch, §4.1: *"where the target (e.g.,
TypeScript/Effect) does not [support Actors], implementing the actor model can
be challenging, and a runtime library should probably be developed to provide
an Actor facade."*

Consequence: a new target is a new **profile**, not a new model.

### 2.4 A lowering is behaviour, not an entity

Three things in a generator have identity and a lifecycle, and therefore earn
aggregate status:

- **`GenerationRun`** — one per invocation, with a real state machine.
- **`Artifact`** — a file, identified by path, moving Planned → Emitted →
  Filled → Verified.
- **`Hole`** — an `[[AI FILL]]` marker, moving Open → Filled → Proven.

A lowering ("how an event-sourced entity becomes a class plus a journal") has
none of the three. It is a function. Modelling the 40 RIDDL definition kinds
as entities would emit 40 stateful classes that never change state, and would
teach a generator builder a structure they should not copy.

### 2.5 Scope: the generation core only

In scope: intake and the generability bar, naming derivation, target profile
and mapping tables, per-definition lowering, spec and code emission, hole
filling, and the proving gates.

Out of scope: auth, Keycloak tiers, freemium gating, serve mode, MCP, and AI
provider plumbing. Those are riddlg-the-product. A bespoke client generator
would reproduce none of them.

---

## 3. Location and gating

`tooling/code-generation/code-generator/`

`tooling/` is a **new, 19th top-level sector**, chosen over squeezing the
model into `technology/`. It gives future tooling models (Synapify, riddlc
itself) a home, and is honest that this is our own toolchain rather than an
industry domain.

Consequences, all of which are wanted:

- Every corpus gate applies: `sbt v`, `sbt pc`, `sbt checkAll`, the library-API
  test suite, and a committed `.bast`.
- The corpus census moves **190 → 191**.
- `CLAUDE.md`'s sector table and its "18 top-level sectors" line become 19;
  `README.md`'s repository tree gains a `tooling/` entry (it carries a tree,
  not a sector table).
- The model must reach and hold **zero findings of every severity**, the
  standard the rest of the corpus is held to.

---

## 4. Architecture

One domain, seven contexts, one domain-level saga.

```
domain CodeGeneration
├── saga GenerationPipeline        (domain level; addresses CONTEXTS only)
├── context Intake                 (GenerationRun entity)
├── context Naming                 (pure functions; no ports, no processors)
├── context Planning               (LoweringRule repository)
├── context SpecEmission           (the derived, deliberately-red suite)
├── context CodeEmission           (Artifact entity, Decision repository)
├── context HoleFilling            (Hole entity, fill-context assembly)
└── context Proving                (pass-1 boot gate, pass-2 green gate)
```

### 4.1 The saga addresses contexts, never their internals

`GenerationPipeline` is declared at **domain** level and every step tells a
command **to a context**:

```riddl
step StepPlan is {
  do "lower every definition in the admitted model"
  let planModel: type Planning.PlanModel = prompt("the plan command for this run")
  tell planModel to context Planning
} reverted by {
  do "discard the plan"
  let discardPlan: type Planning.DiscardPlan = prompt("the discard command for this run")
  tell discardPlan to context Planning
}
```

**Reid's ruling, 2026-08-26**, which is why no step names an entity:

> It is fine for a saga, at domain scope, to send messages to various contexts
> to get work done. That is typical and usual. But to reach past the context
> and into one of its entities or streamlets or repositories, etc. is an
> encapsulation violation. […] No such thing should be permitted by RIDDL.

riddlc does **not** currently enforce this — both forms validate identically
(§6.1). Filed upstream as
`../riddl/task/2026-08-26-saga-tell-must-not-reach-into-a-context.md`. The
model adopts the boundary-respecting form now, so it validates today and
survives the rule landing.

The payoff is not merely compliance: each message-driven context ends up with
a **declared API** — a command alternation, an event alternation, an inlet, an
outlet and a boundary handler — and the saga is written against those APIs. A
generator builder reading the model sees six named service surfaces and the
orchestration over them. Six, not seven: `Naming` is reached by function call,
not by message, so it declares no ports and the saga never addresses it.

### 4.2 Contexts

"Stateful definitions" below means aggregates and repositories; a context with
none is stateless and holds only handlers or functions.

| Context | Stateful definitions | Responsibility |
|---|---|---|
| `Intake` | `GenerationRun` entity | Load the model (source or `.bast`); apply the generability bar; refuse |
| `Naming` | none — functions only | Hierarchy → package, sanitization, `namespace` precedence |
| `Planning` | `LoweringRule` repository | One lowering function per definition kind; produce planned artifacts |
| `SpecEmission` | none | Emit the test suite derived from the model |
| `CodeEmission` | `Artifact` entity, `Decision` repository | Emit structure and headers; open holes; record rationale |
| `HoleFilling` | `Hole` entity | Assemble each hole's local context; fill it |
| `Proving` | none | Pass-1 boot gate; pass-2 green gate; emit `ProofFailed` |

### 4.3 Intake and the generability bar

The bar is CM §0.3 ruling 5, and it is operational rather than advisory —
an admission decision with a refusal:

- A **conforming** model has no Errors.
- A **generable** model has no Errors and no warnings other than Style.

`CompletenessWarning`, `MissingWarning` and `UsageWarning` are all hard stops
for a generator, because code cannot be generated from unstated intent. Note
that riddlc's own `Messages.isActionable` sits at a *lower* threshold; the
generability bar is the stricter of the two and is the one Intake applies.

### 4.4 Naming

Pure functions, no state. Derived from riddlg's actual behaviour:

- Package is `<base>.<domain>.<context>`, each segment lower-cased with every
  non-alphanumeric mapped to `_`.
- `option namespace` **replaces** the derived path rather than extending it,
  and becomes the base for everything the scope contains.
- Precedence: model > CLI flag > config > built-in.
- Domain-level shared types belong to the **domain's** package.

Verified legal: a context with only functions and no ports validates at zero
errors, and is callable cross-context (§6.2).

### 4.5 Planning and the lowering catalogue

`Planning` holds a **`LoweringRule` repository**, one record per RIDDL
definition kind, stating the capabilities that kind requires, the artifacts it
plans, and the guarantees that must survive lowering. Each lowering function
**consults** the repository rather than hard-coding its rule.

Consulting rather than sitting beside is deliberate. It is what makes the
catalogue partially self-enforcing: a rule nothing consults surfaces as a
`usage` finding, and this corpus's zero standard turns that into a build
failure. It does not enforce the converse — a definition kind with no rule is
still only visible by inspection — so that gap is stated here rather than
pretended away.

### 4.6 The two emissions

Split because Reid's recursive-TDD ruling gives them different acceptance:

> A generated artifact is not correct because it compiles — it is correct
> because it ships with the means to prove itself.

- **`SpecEmission`** emits the suite derived from the model. It is
  **necessarily red**: it states what the filled code must do, and nothing has
  filled it yet. Red here is the design, not a regression.
- **`CodeEmission`** emits framework and structure with `[[AI FILL]]` holes,
  plus headers (the nearest scope's copyright, verbatim, in each artifact's
  comment syntax) and a `Decision` record wherever a non-obvious choice was
  made and why.

This mirrors riddlg's existing gate split, where the pass-1 gate runs with
`-DskipTests` precisely because behaviour is not yet assertable.

### 4.7 HoleFilling

A context of its own, on Reid's design:

> They are going to come up in different places (statements and expression
> evaluation), and at different phases. Plus filling holes depends on a lot of
> context but not the ENTIRE context of the model for which you're generating
> code. You might want to keep the basic details about the processor you're
> working on and its code, so far, as the relevant context for filling holes
> so the AI can draw from the local resources in that bit of code to fill the
> hole.

So `Hole` carries not just its prompt text but its **fill context** — the
enclosing processor, the artifact's code so far, and the declarations in
scope. Assembling that slice is a modelled responsibility, because the
difference between a fill that works and one that hallucinates is what got
sent.

Holes arise from prose the language deliberately leaves vague: the `do`
statement's string, and an unascribed `prompt`. Conditions and branching are
**not** holes — 2.0 shipped typed holes, a closed boolean expression grammar,
and structured match patterns, which moved that work into the deterministic
tier. A generator still routing conditions through AI FILL is doing work the
language now does for it.

### 4.8 Proving, and the retry cycle

Two gates, matching riddlg's:

- **Pass-1 gate** — compiles, augments and boots. Behaviour not asserted.
- **Pass-2 gate** — the generated suite goes green.

The cycle spans two contexts: `Proving` emits `ProofFailed`, `HoleFilling`
reopens the named holes and refills.

**There is no loop construct, and that is the correct shape.** RIDDL has
`foreach` for fan-out over the hole work list, but retry-until-green is an
**event cycle**: a failed proof causes a re-entry, which is what a reactive
system does instead of looping. It is bounded by an attempt count on `Hole`
with a `require` capping it, because an unbounded fill/prove cycle against an
AI backend is a runaway.

The terminating condition is a count reaching zero — the same argument CM
§0.3.5 makes for completeness counts driving an AI authoring loop.

If this turns out clumsy to express, that is a genuine finding and goes
upstream: bounded retry is common enough that "model it as an FSM with a
counter" may be the wrong answer.

---

## 5. Out of scope

- Any model of the target *runtime system* (§2.1).
- The eight CM aspects as model data (§2.2).
- riddlg's product surface: auth, tiers, serve, MCP, AI providers (§2.5).
- Per-target concrete models. One model plus target profiles (§2.3).

---

## 6. Verified language facts

Everything here was measured this session with
`~/.cache/riddlc/2.0.0-rc.26/bin/riddlc --no-ansi-messages validate` on
purpose-built minimal models. These are recorded because several contradict
what was previously believed.

### 6.1 A domain-level saga may reach into a context — riddlc does not object

A two-step domain-level saga telling `to entity Running.Runner` and the same
saga telling `to context Running` both report:

```
24 definitions checked, 0 errors, 12 warnings (1 missing, 1 usage, 6 completeness)
```

Identical counts, identical rule ids. **This corrects `CLAUDE.md`**, which
stated flatly that a saga's tell may not cross a context boundary; that rule
was derived from the *context-level* case and is narrower than it read. The
sideways case — a saga inside context A telling into context B — remains
**untested**; do not generalise from this result.

The four `[warning] [msg-tell-target-unreachable]` findings present on both
are about **connector wiring**, not boundaries, and fire whether or not a
boundary is crossed. They are not a substitute for the missing check.

### 6.2 A context with only functions is valid, and callable cross-context

A `Naming` context holding two records and one function, no ports and no
processors, called from an entity handler in a *different* context, validates
at **0 errors with no finding naming either the context or the function**.

### 6.3 `call` is a value, not a statement

`value = literal_string | prompt_value | call | ask | initiate | constructor |
get_value`. A bare `call function F(args)` as a statement is a parse error;
the accepted form is `let x = call function F(args)`. CLAUDE.md documents that
the `function` keyword is required but not that `call` is a value.

Canonical function form, from `reactive-bbq/restaurant/LoyaltyContext.riddl:56`:

```riddl
function PointsForSpend is {
  requires type SpendForPoints
  returns  type PointsEarned
  return prompt("floor(spendAmount * PointsPerDollar)")
}
```

### 6.4 A `let` name that matches a field of the returned record shadows it

`let sanitized = call function Naming.Sanitize(...)` where `NameResult` has a
field `sanitized` draws `[warning] [name-shadows-definition]`.

### 6.5 A domain cannot hold functions

`domain_content` reaches functions only through `vital_definition_contents`,
which is `type_def | comment`. Functions live in
`processor_definition_contents`. No upstream task filed: §6.2 shows a
functions-only context is legal, so the workaround is a context, not a gap.

### 6.6 `module` exists, but is root-level

`root_content = bast_import | root_definition | module | root_include`. It
replaced the deprecated anonymous `nebula` and can hold contexts, domains,
entities and functions. It is **not** a sub-context partition, so it does not
answer the "module inside a context" question raised in design.

---

## 7. Risks and open questions

1. **Size.** Seven contexts with declared APIs, three aggregates, a
   repository and ~40 lowering functions is a large model — comparable to
   reactive-bbq. It will not reach zero findings in one pass.
2. **The catalogue can drift.** Consulting makes an *unused* rule visible;
   nothing makes a *missing* rule visible (§4.5).
3. **The retry cycle may be clumsy** to express without a loop construct
   (§4.8). If so, that is the dogfooding finding, not a defect to work around.
4. **The sideways saga case is untested** (§6.1) and should be settled before
   anyone relies on the corrected CLAUDE.md rule in the other direction.
5. **`.bast` and the census.** Adding the model moves the corpus to 191 and
   requires a committed `.bast`; `verify-bast-roundtrip.sh` requires the
   source to be in prettify canonical form.

---

## 8. Acceptance criteria

1. The model lives at `tooling/code-generation/code-generator/` with a `.conf`
   naming its entry file.
2. `riddlc validate --corpus .` reports **191 models, 0 failed, 191 ok**.
3. `collect-warnings.py`, run with the pinned binary, reports **0 findings**
   for the new model — every severity, style included.
4. `sbt v`, `sbt pc` and `sbt checkAll` are green.
5. A committed `.bast` that survives `verify-bast-roundtrip.sh`.
6. No saga step names any definition inside a context.
7. Every RIDDL definition kind that a generator must lower has a
   `LoweringRule` record, and every lowering function consults one.
8. `CLAUDE.md`'s "**18 top-level sectors**" (line 66) reads 19, its sector
   table gains a `tooling` row, and `README.md`'s repository-tree listing
   gains a `tooling/` entry. README carries a directory tree, not a sector
   table — checked 2026-08-26.
9. A README for the model explaining, for a generator builder, what each
   context is for — with a NAICS code, per corpus convention.

---

## 9. Upstream tasks filed

- `../riddl/task/2026-08-26-saga-tell-must-not-reach-into-a-context.md` —
  make it an Error for a `tell`/`send` from outside a context to name a
  definition inside it. Includes both measured outputs, a four-case rule on
  enclosing contexts, and an impact analysis showing all three corpus sagas
  are intra-context and unaffected.
