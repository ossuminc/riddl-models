# Design: a generic RIDDL code generator, modelled in RIDDL

**Date:** 2026-08-26
**Branch:** `release/2`
**riddlc:** `2.0.0-rc.26` (published; `riddlcPath := None`)
**Status:** revised after Reid's review, 2026-08-26. Sections **2.3**,
**3**, **4.5**, **5**, **7**, **8**, **9** and **Appendix A** are new or
rewritten in response to it, including his two follow-up rulings — ECS and
tuple space dropped as viable targets, and a missing event-sourcing library
made a cost rather than a disqualification. **No open questions remain for
Reid.** Awaiting approval to plan; no RIDDL written.

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

### 2.3 What "generic" means: a precedence over representation paradigms

This is the design's centre, and the previous draft got it wrong. That draft
read "generic" as **genericity** — a type-parameter problem, "RIDDL has no
generics, so `entity → actor | object | bean` cannot be parameterised."
**Reid's correction, 2026-08-26:**

> So, all this is what I meant by a "generic" model, not the Genericity you
> chose to include in section 2.3. Generic in the sense that this is the
> uber-design for ANY code generator and we have to generalize (make generic)
> the kinds of computing abstractions that will be used.

The model is generic because it abstracts over **the kinds of computing
abstraction a target can offer, in an order of precedence**. It is not
generic in the parametric-polymorphism sense at all, and the absence of
generics in RIDDL turns out to be irrelevant to it.

#### 2.3.1 Why the actor is first: every RIDDL processor is the same machine

Reid:

> All processors are essentially the same: they have input messages,
> communicate over abstract channels/connectors, process messages the way
> actors do (one at a time) while different processors can run in parallel
> and the set of statements they can use is limited to the 19 that RIDDL
> defines today. The "do" command allows an arbitrarily rich algorithmic
> richness that can be written by AI. That model is based on actors and
> actor systems.

All four clauses check out against the grammar (§6.7). The statement count
is exactly **19**, and `do` is not a twentieth: `prompt_statement =
("do" | "prompt") literal_string_block` — `do` and `prompt` are two
spellings of one statement. So the escape hatch Reid describes is a single
production, which is precisely why it can be the single AI-fill seam (§4.7).

That is the argument for the ordering. It is not that actors are
fashionable; it is that a RIDDL processor **is** an actor — serial message
consumption per identity, parallel across identities, interaction only over
abstract channels — so the actor is the representation that requires no
facade at all. Everything below it in the precedence needs something built.

#### 2.3.2 The second tier: reactive architecture, not just the actor

Below the representation choice sits a set of runtime tenets the target must
also supply, and this is what makes the three chosen targets the ones they
are. Reid:

> The next thing to reach for are the tenets of reactive architecture:
> asynch non-blocking interactions and invocations, reactive streams, R2DBC
> (reactive JDBC), message queuing between contexts, etc. There are reasons
> I selected Quarkus/Java, Pekko/Scala, and Typescript/Effect.

| Target | Representation tier | Reactive tenets | Event sourcing / CQRS |
|---|---|---|---|
| Pekko / Scala | **actor**, native | Pekko Streams, async by construction | Pekko Persistence, native |
| Quarkus / Java | **bean**, actor by facade | Mutiny, SmallRye Reactive Messaging, Hibernate Reactive | not native |
| TypeScript / Effect | **actor** via `@effect/cluster`; fibers + `Queue` otherwise | Effect `Stream`, async by construction | generated, if no library |

**The event-sourcing column does not gate a target — Reid, 2026-08-26:**

> Regardless of whether event sourcing is supported by Effect or not, Effect
> is a viable candidate and event sourcing could be handled by generated
> code if there is no suitable library/plugin available.

This settles what had been recorded as an open question, and it settles more
than the Effect case. CM §4 makes event-sourced entities a first-class
lowering, so a target with no durable append-only journal owes one — but
*owing* a capability and *failing* on it are different things. **The
generator can emit the journal.** The library is a shortcut, not a
prerequisite, and the same reasoning covers a missing mailbox, missing
sharding, or missing reactive data access. That is precisely what the facade
bill in §2.3.4 accounts for, and why the taxonomy has one disqualifier
(§2.3.3) rather than many.

The precedence also explains what a *bad* target looks like without having
to blacklist anything. Reid: *"if someone were to target, say, Visual Basic,
they would have a hard go of it; much harder than Go, or Swift, or Python,
where these kinds of programming idioms, practices, patterns and libraries
are already implemented."* Go lands on CSP natively, Swift has `actor` in
the language, Python has `asyncio` — each reaches a high tier cheaply. A
target that reaches only `object` owes every guarantee as hand-written
scaffolding, and the profile makes that bill explicit rather than letting a
generator discover it artifact by artifact.

#### 2.3.3 The admission test, and the full taxonomy

Reid's bar for whether a target is expressible at all:

> As long as that basic tenet (data + behavior in one abstraction) is
> upheld, we can probably translate riddl models to it.

So **encapsulation is the admission test**, and the precedence among those
that pass is decided by how much of the rest a paradigm supplies *natively*.
A RIDDL processor needs four things; encapsulation admits, and the other
three rank:

- **E — encapsulation:** data and behaviour in one unit *(admission)*
- **S — serial execution:** one message at a time per identity
- **A — addressable identity:** location-transparent, address-not-reference
- **C — channel interaction:** asynchronous, non-blocking, no shared memory

| Paradigm | E | S | A | C | Representative |
|---|:-:|:-:|:-:|:-:|---|
| **Actor** | ● | ● | ● | ● | Pekko, Akka, Erlang/Elixir, Orleans, `@effect/cluster` |
| **Active Object** | ● | ● | ◐ | ● | ACE, proxy-plus-scheduler-plus-queue |
| **CSP process** | ● | ● | ○ | ● | Go, Occam, `core.async` |
| **Service / microservice** | ● | ○ | ● | ● | SOA, microservices |
| **DDD Aggregate** | ● | ◐ | ● | ○ | the pattern RIDDL's `aggregate` names |
| **FRP / Reactive Streams** | ◐ | ● | ○ | ● | RxJS, RxJava, Pekko Streams, Effect `Stream` |
| **Bean / component** | ● | ○ | ◐ | ○ | EJB, CDI, Quarkus, OSGi, Spring, COM |
| **Monadic state machine** | ● | ● | ○ | ○ | Elm, Redux, Haskell `State` |
| **Object** | ● | ○ | ○ | ○ | any OO language |
| **DCI** | ◐ | ○ | ● | ○ | roles bound to data per context |
| ~~ECS~~ | ○ | — | — | — | game engines — **fails admission**, see below |
| ~~Tuple space / Linda~~ | ○ | — | — | ● | JavaSpaces, Linda |

● native · ◐ partial or container-dependent · ○ must be supplied by facade

So Reid's short answer — **actor, bean, object** — is the top, middle and
floor of this table, and those three are the ones a generator author will
actually meet most often. The rest of the table exists so that a target that
lands somewhere unusual (a Go generator, an Elm front end) has a named row
rather than being forced into the wrong one.

**Two entries from Reid's list are excluded, on his ruling of
2026-08-26** — *"I'm okay with dropping ECS/tuple-space as a viable
abstraction."* Both were raised here because they fail the admission test
they were listed under. ECS's own core idea is the opposite of the tenet —
*"instead of combining state and behavior in a single object, state is held
in Entities/Components and behavior is executed by Systems"* — and tuple
space is the same shape, inert tuples with the processes elsewhere. Both are
sound architectures; neither can receive a RIDDL processor without first
rebuilding the encapsulation RIDDL assumes.

**This is the taxonomy's only disqualifier, and that is the point.** Every
other gap — no mailbox, no sharding, no journal, no reactive driver — is a
facade the generator emits (§2.3.2). Failing to bundle data with behaviour
is the one thing no amount of generated code can paper over, because there
is no boundary to generate *into*.

#### 2.3.4 Capabilities remain — as the facade bill, not the selector

The previous draft's capability mechanism survives, demoted to its proper
job. The precedence **selects** the paradigm; capabilities **describe what
the selection costs**.

A `TargetProfile` names, per RIDDL processor kind, the highest-precedence
paradigm the target supplies, and every capability that paradigm leaves
unmet becomes a facade the generator must emit — the ○ and ◐ cells above,
made concrete. This is the CM's own escape hatch generalised beyond the
actor case it currently states (§4.1):

> where the target (e.g., TypeScript/Effect) does not [support Actors],
> implementing the actor model can be challenging, and a runtime library
> should probably be developed to provide an Actor facade.

Consequence, unchanged from the previous draft and now better founded: **a
new target is a new profile, not a new model.**

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

In scope: intake and the generability bar, naming derivation, target profiles
and the lowering catalogue, per-definition lowering, spec and code emission,
hole filling, and the proving gates.

Out of scope: auth, Keycloak tiers, freemium gating, serve mode, MCP, and AI
provider plumbing. Those are riddlg-the-product. A bespoke client generator
would reproduce none of them.

**§5 carries the full scope statement**, including the two boundaries that
are narrower than an earlier draft claimed — the target runtime, which is in
scope as catalogue and templates, and the eight CM aspects, which bind the
design without being model data.

---

## 3. Location and gating

`tooling/code-generator/`

**Two levels, not three** — Reid, 2026-08-26: *"In section 3, I don't think
we need 3 levels for this so `tooling/code-generator` is sufficient."* The
corpus convention is `sector/subsector/model`, and the intermediate
`code-generation/` level would have held exactly one model with no sibling
in prospect.

Verified safe, 2026-08-26: nothing in the build or the scripts assumes a
depth. `build.sbt` sets `riddlcSourceDir := baseDirectory.value` and the
plugin discovers models by scanning for `.conf` files; every script in
`scripts/` globs `**/*.conf` and uses `relative_to(ROOT).parts` only to
exclude `patterns/`. A two-level model is found by all of them.

`tooling/` is a **new, 19th top-level sector**, chosen over squeezing the
model into `technology/`. It gives future tooling models (Synapify, riddlc
itself) a home, and is honest that this is our own toolchain rather than an
industry domain.

**No NAICS code** — Reid, 2026-08-26: *"a NAICS code is not needed for
tooling so don't stress about it."* This is a deliberate, recorded exception
to the convention in `CLAUDE.md` that every model README carries one, and it
generalises to the `tooling/` sector as a whole: these models describe our
own toolchain, which has no industry classification to give. `CLAUDE.md`'s
NAICS paragraph gains that exception (§8, criterion 10).

Consequences, all of which are wanted:

- Every corpus gate applies: `sbt v`, `sbt pc`, `sbt checkAll`, the
  library-API test suite, and a committed `.bast`.
- The corpus census moves **190 → 191**.
- `CLAUDE.md`'s sector table and its "18 top-level sectors" line become 19;
  `README.md`'s repository tree gains a `tooling/` entry (it carries a tree,
  not a sector table).
- The model must reach and hold **zero findings of every severity**, the
  standard the rest of the corpus is held to (§8, criterion 3).

---

## 4. Architecture

One domain, seven contexts, one domain-level saga.

```
domain CodeGeneration
├── saga GenerationPipeline        (domain level; addresses CONTEXTS only)
├── context Intake                 (GenerationRun entity)
├── context Naming                 (pure functions; no ports, no processors)
├── context Planning               (LoweringRule + TargetProfile repos)
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
| `Planning` | `LoweringRule`, `TargetProfile` repositories | Select a paradigm per kind; lower; produce planned artifacts |
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

`Planning` holds a **`LoweringRule` repository**, one record per lowering
decision, stating the capabilities the target construct requires, the
artifacts it plans, and the guarantees that must survive lowering. Each
lowering function **consults** the repository rather than hard-coding its
rule.

Consulting rather than sitting beside is deliberate. It is what makes the
catalogue partially self-enforcing: a rule nothing consults surfaces as a
`usage` finding, and this corpus's zero standard turns that into a build
failure. It does not enforce the converse — a definition kind with no rule
is still only visible by inspection — so that gap is stated here rather than
pretended away (§7.2).

#### 4.5.1 The key is (definition kind × paradigm), not (definition kind × target)

Reid raised the shape of the catalogue and left the call to me:

> The lowering catalogue in 4.5 is most useful if it is specified for each
> kind of target. Then the different kinds of targets only need to be
> considered during lowering and the rest of the processing can be shared in
> common across multiple target language/library/systems. That may or may
> not be useful; I'll leave it to you to decide.

**Adopting the goal, adjusting the key.** The goal — confine all
target-awareness to lowering, share everything else — is right and the model
is built to it: `Intake`, `Naming`, the traversal in `Planning`,
`SpecEmission`'s derivation, `CodeEmission`'s mechanics, `HoleFilling` and
`Proving` are all target-agnostic, and `LoweringRule` is the only place a
target can be seen.

Keying literally *by target* is the part I would change. Targets are
unbounded and mostly identical to one another: a Quarkus catalogue and a
Spring catalogue would differ in imports and agree on all forty lowerings,
so the catalogue would carry N near-duplicate copies and the drift risk in
§7.2 would multiply by N. **Paradigms are the axis that actually varies** —
the table in §2.3.3 has ten rows and will not grow much — and the paradigm
is what determines whether a lowering needs a facade.

So:

- **`LoweringRule`** is keyed by `(definitionKind, paradigm)`. "An
  event-sourced entity lowered onto an **actor**" is one rule; "onto a
  **bean**" is another, and it is the one that names the facades.
- **`TargetProfile`** is a small record per target: for each RIDDL processor
  kind, the highest-precedence paradigm this target supplies, plus the
  capability gaps it must fill (§2.3.4).
- **Selection** is `profile(kind) → paradigm`, then
  `catalogue(kind, paradigm) → rule`.

Adding Quarkus after Pekko therefore adds **one profile**, not forty rules,
and the rules it selects are already exercised by any other bean-tier
target. Adding Visual Basic adds a profile that resolves everything to
`object` and consequently owes the longest facade bill in the catalogue —
which is Reid's "hard go of it", made mechanical.

**Where a target genuinely is unique** — a library's own idioms, its import
lines, its build file — that is emission, not lowering, and it belongs in
the templates of §5.1 rather than in the catalogue.

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

## 5. Scope — and what the boundaries do NOT mean

Reid pushed back on the previous draft's flat "out of scope" list, and he is
right that it was blunt where the truth is nuanced:

> You characterized several things as "out of scope" in section 5. But I
> think it is more nuanced than that.

### 5.1 The target runtime IS in the design — as catalogue and templates

Previously listed as out of scope. Reid:

> The model of the target runtime section is essentially that lowering
> catalogue in 4.5. A series of templates would suffice as well, especially
> if substitution were possible. So the target runtime model must be
> considered in the generic design, but perhaps not detailed; still, it is
> instructive to be aware of the kinds of abstractions available in computer
> science constrained to distributed reactive programming.

What §2.1 actually retired was a *separate domain* for generated source — an
AST per target language, or a set of running-system behaviours. What
survives, and is squarely in scope, is the target runtime as it is actually
needed:

- the **`LoweringRule` catalogue** (§4.5) — what each RIDDL construct
  becomes on each paradigm, and what facade covers the gap;
- **emission templates with substitution** — the per-target idiom,
  imports and build scaffolding that the catalogue deliberately does not
  carry;
- the **paradigm taxonomy** (§2.3.3) — the survey of what distributed
  reactive programming has to offer, which is the "instructive to be aware
  of" part.

What stays out is a *detailed* model of any one runtime. The design must
know that Pekko Persistence exists and what guarantee it supplies; it must
not model Pekko.

### 5.2 The eight CM aspects are constraints, not architecture

§2.2's ruling stands — they are not model **data** — but "out of scope" was
the wrong word for them. Reid:

> Also the 8 CM aspects are not to be ignored, they just don't form the
> architecture of the model we're trying to build. Those tenets are still
> relevant in the details of the design as they must be upheld by that
> design.

So they bind, at three places: each lowering's `described as` states which
guarantee it preserves; the narrow class of aspects that are genuine
two-outcome decisions become **invariants** on the lowering that chooses
(§2.2); and the generability bar in `Intake` (§4.3) is itself an aspect
turned operational. They are acceptance criteria for the generator's output
and they are checked — they are simply not forty fields on a record.

### 5.3 Genuinely out

- **riddlg's product surface** — auth, Keycloak tiers, freemium gating,
  serve mode, MCP, AI-provider plumbing. Reid confirmed: *"You're correct
  about riddlg's surface, we're only considering its code generation
  capability here."* A bespoke client generator reproduces none of it.
- **Per-target concrete models.** One model, plus profiles and templates
  (§4.5.1).
- **A generated-source domain.** Retired by Reid in design (§2.1).

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

### 6.7 There are exactly 19 statements, and `do` is not a twentieth

`ebnf-grammar.ebnf:263-267` lists `statement` as 19 alternatives plus
`comment`: `when`, `match`, `foreach`, `send`, `tell`, `forward`, `yield`,
`reply`, `set`, `let`, `put`, `return`, `terminate`, `prompt`, `code`,
`error`, `require`, `morph`, `become`. Reid's count is exact.

Two consequences for the design:

- **`do` and `prompt` are one statement**, spelled two ways:
  `prompt_statement = ("do" | "prompt") literal_string_block` (line 471).
  The arbitrary-algorithmic-richness escape hatch is therefore a single
  production, which is what lets `HoleFilling` (§4.7) have one seam rather
  than several.
- **`code_statement` is a second, literal escape hatch** —
  ` ```("scala" | "java" | "python" | "mojo") code_contents``` ` (line 472)
  — and its language list is **closed and does not include TypeScript**,
  though TypeScript/Effect is one of the three named targets (§2.3.2). A
  model carrying inline target code for a Pekko/Scala generator has no
  equivalent for an Effect one. To be filed upstream (§9).

---

## 7. Risks and open questions

1. **Size.** Seven contexts with declared APIs, three aggregates, three
   repositories and ~40 lowering functions is a large model — comparable to
   reactive-bbq. It will not reach zero findings in one pass; criterion 3
   is a bar to converge on, not a first-run expectation.
2. **The catalogue can drift.** Consulting makes an *unused* rule visible;
   nothing makes a *missing* rule visible (§4.5). Keying by paradigm rather
   than target (§4.5.1) bounds how far it can drift but does not close the
   gap.
3. **The retry cycle may be clumsy** to express without a loop construct
   (§4.8). If so, that is the dogfooding finding, not a defect to work
   around.
4. **The sideways saga case is untested** (§6.1) and should be settled
   before anyone relies on the corrected `CLAUDE.md` rule in the other
   direction.
5. **`.bast` and the census.** Adding the model moves the corpus to 191 and
   requires a committed `.bast`; `verify-bast-roundtrip.sh` requires the
   source to be in prettify canonical form.
6. **`code_statement` has no TypeScript** (§6.7). Not blocking for this
   model, but it undercuts one of the three named targets.

---

## 8. Acceptance criteria

1. The model lives at `tooling/code-generator/` with a `.conf` naming its
   entry file.
2. `riddlc validate --corpus .` reports **191 models, 0 failed, 191 ok**.
3. **The model meets the bar of the rest of the corpus: 0 errors and 0
   warnings of any kind** — style, usage, missing and completeness
   included. Reid, 2026-08-26: *"the model produced must meet the bar of
   the rest of the corpus: 0 errors, 0 warnings (of any kind). That must be
   validated by the staged riddlc or the installed riddlc at or later than
   2.0.0-rc.26."* Measured with `collect-warnings.py` run against a binary
   whose `riddlc info` reports **≥ 2.0.0-rc.26**, recorded in the commit —
   not with `sbt v`, which validates through the `.conf` and is the lenient
   gate (`CLAUDE.md`), and not with `../bin/riddlc`, which is currently a
   tag behind.
4. `sbt v`, `sbt pc` and `sbt checkAll` are green.
5. A committed `.bast` that survives `verify-bast-roundtrip.sh`.
6. No saga step names any definition inside a context.
7. Every RIDDL definition kind a generator must lower has a `LoweringRule`
   for each paradigm it can land on, and every lowering function consults
   one (§4.5.1).
8. At least two `TargetProfile` records exist — one actor-tier, one
   bean-tier — so the paradigm indirection is exercised rather than
   asserted.
9. `CLAUDE.md`'s "**18 top-level sectors**" (line 66) reads 19, its sector
   table gains a `tooling` row, and `README.md`'s repository-tree listing
   gains a `tooling/` entry. README carries a directory tree, not a sector
   table — checked 2026-08-26.
10. `CLAUDE.md`'s NAICS paragraph records the `tooling/` exception (§3).
11. **`RIDDL-Computational-Model.md` §4.1 is enriched** with the paradigm
    precedence and taxonomy — Reid: *"you should enrich section 4.1 (of the
    CM) with those other forms of state + behavior. Updating the CM with
    that should be part of this work."* Draft text in Appendix A, awaiting
    his approval before it is applied.
12. A README for the model explaining, for a generator builder, what each
    context is for. **No NAICS code** (§3).

---

## 9. Upstream tasks

### Filed

- `../riddl/task/2026-08-26-saga-tell-must-not-reach-into-a-context.md` —
  make it an Error for a `tell`/`send` from outside a context to name a
  definition inside it. Includes both measured outputs, a four-case rule on
  enclosing contexts, and an impact analysis showing all three corpus sagas
  are intra-context and unaffected. **Unacknowledged** as of 2026-08-26.

### To file

- **`code_statement` has no TypeScript** (§6.7). The fenced-code statement
  accepts `scala | java | python | mojo`; TypeScript/Effect is one of the
  three targets this design is built for, and Go and Swift are named as
  cheap targets (§2.3.2). Ask for the list to be opened, or for the
  rationale behind its being closed.

### Not upstream — this repository's work

- **`RIDDL-Computational-Model.md` §4.1** (Appendix A). The CM lives at
  `ossuminc/` level, above every project, so this edit is a
  cross-repository artifact rather than a riddl task.

---

## Appendix A — draft enrichment of CM §4.1

Reid, 2026-08-26: *"you should enrich section 4.1 (of the CM) with those
other forms of state + behavior. Updating the CM with that should be part of
this work."*

CM §4.1 currently ends with an **Implementation reality** paragraph that
handles exactly one fallback — the target has actors, or it does not and
needs an actor facade. That is a binary where the real situation is a
ranking. The text below **replaces that paragraph** and leaves the preceding
paragraph (the DDD/Akka mental model) untouched.

Applied to `../RIDDL-Computational-Model.md` at line 1036, on approval.

---

**Implementation reality — a precedence of representations.** Not every
target supplies actors, and the ones that do not are not all equally far
away. The admissible representations for an Entity form an ordered
preference, and a generator should take the highest one its target supports
natively before reaching for a facade. The ordering is not a matter of
taste: a RIDDL processor already *is* an actor — it consumes messages one at
a time per identity, runs in parallel across identities, interacts only over
abstract channels, and draws on a closed set of 19 statements — so the actor
is the representation that costs nothing to reach, and every step down the
list is a guarantee the generator must build instead of inherit.

**The admission test is encapsulation:** data and behaviour bundled in one
abstraction. Any paradigm upholding that can receive a RIDDL model. Among
those that do, rank by how much of the rest comes for free — **serial
execution** (one message at a time per identity), **addressable identity**
(location-transparent, address rather than object reference), and **channel
interaction** (asynchronous, non-blocking, no shared memory).

| Representation | Encaps. | Serial | Address. | Channels | Representative |
|---|:-:|:-:|:-:|:-:|---|
| **Actor** | ● | ● | ● | ● | Pekko, Akka, Erlang/Elixir, Orleans, `@effect/cluster` |
| **Active Object** | ● | ● | ◐ | ● | proxy + scheduler + activation queue |
| **CSP process** | ● | ● | ○ | ● | Go, Occam, Clojure `core.async` |
| **Service / microservice** | ● | ○ | ● | ● | SOA, microservices |
| **DDD Aggregate** | ● | ◐ | ● | ○ | the pattern `aggregate` names |
| **FRP / Reactive Streams** | ◐ | ● | ○ | ● | RxJS, RxJava, Pekko Streams, Effect `Stream` |
| **Component / Bean** | ● | ○ | ◐ | ○ | EJB, CDI, Quarkus, OSGi, Spring, COM/DCOM |
| **Monadic state machine** | ● | ● | ○ | ○ | Elm, Redux, Haskell `State` |
| **Plain object** | ● | ○ | ○ | ○ | any OO language |
| **DCI** | ◐ | ○ | ● | ○ | roles bound to data per context |

● native · ◐ partial or container-dependent · ○ must be supplied by facade

In short form, the three a generator author will actually meet are **actor,
bean, object** — the top, middle and floor of that table.

**Two widely used architectures are excluded, and for the same reason.**
Entity-Component-System deliberately separates state (Entities and
Components) from behaviour (Systems), and the tuple-space/Linda model holds
inert tuples in a shared space with behaviour elsewhere. Both are sound
designs and neither upholds the encapsulation tenet, so neither can receive
a RIDDL Entity without first rebuilding the boundary RIDDL assumes. They are
named here so the omission reads as a decision rather than an oversight.

**Encapsulation is the only disqualifier.** Every other gap in the table —
no mailbox, no location-transparent addressing, no channels — is a facade
the generator can emit, and a target is not ruled out by owing one. Only the
absence of a data-plus-behaviour boundary cannot be generated around, since
there is nothing to generate into.

**What the ranking costs, concretely.** Where a library supports actors
(Akka, Pekko, etc.) it can be used directly. Where the target does not — the
TypeScript/Effect case — implementing the actor model can be challenging,
and a runtime library should probably be developed to provide an Actor
facade, especially guaranteeing processing in order of mailbox receipt and
no concurrent processing of messages for a single actor/entity. A bean-tier
target such as Quarkus/Java inherits encapsulation and container-managed
addressing but owes serial execution and channel semantics; an object-tier
target owes all three, which is why a target like Visual Basic is a far
harder proposition than Go (CSP native), Swift (`actor` in the language) or
Python (`asyncio`). A generator should record this bill per target rather
than rediscovering it per artifact.

**Beyond the representation, the runtime tenets still apply:**
asynchronous non-blocking interaction and invocation, reactive streams,
reactive data access (R2DBC and equivalents), and message queuing between
Contexts. A target may supply a first-rate Entity representation and still
lack a durable append-only journal, in which case `event-sourced` (§4.5)
owes a facade of its own: Pekko Persistence supplies it natively, and where
no suitable library or plugin exists the generator emits the journal itself.
A missing library is a cost, not a disqualification — the target remains
viable and the generated code carries the guarantee.
