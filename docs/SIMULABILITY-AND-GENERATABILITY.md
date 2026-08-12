# What a model needs before Synapify can simulate it and riddlg can generate from it

These rules were **derived, not invented**. Each traces to an accepted item
in `../RIDDL-Tools-To-Do-List.md` (Part B is riddlg, Part C is Synapify) or
to `../RIDDL-Computational-Model.md`. The point of writing them down is that
"suitable for simulation and code generation" then becomes something a test
can assert, rather than something proved by running a tool and squinting at
the output — and something riddlc could eventually report itself.

`reactive-bbq` is the reference model these rules are enforced against, by
`src/test/scala/com/ossuminc/riddl/models/ReactiveBbqCompletenessTest.scala`.

## Why rules rather than a tool run

Running `riddlg gen …` proves the generator did not crash. It does not prove
the model carried enough meaning to generate anything *useful*, and it cannot
prove simulability at all — riddlg is not the simulator. Worse, Quarkus
`gen code` is Pro-gated (exit 3 without `riddlg login`), so the most
demanding generator cannot be part of an automated gate here.

The rules below are what the tools consume. Asserting them is stronger than
asserting exit 0.

## R1 — Nothing is a placeholder

**No `???` anywhere in the model.**

`???` means "known to be incomplete". riddlc deliberately exempts a `???`
body from most completeness checks, so a model full of them validates while
being unrunnable. A simulator has nothing to execute and a generator has
nothing to emit.

*Source: Computational Model §0.3 ruling 2 — the generator emits `[[AI FILL:
…]]` for what is vague, but only where the model expressed something. `???`
expresses nothing.*

## R2 — Every definition carries a brief **and** a description

Not decoration. Per **B3's AI-context census**, the inputs to AI-assisted
generation are exactly: in-scope **Terms**, **local description content**
(inline doc blocks and file-based descriptions), and **options**, which are
definitional. Explicitly excluded: comments, URL description content, and
attachments.

So a missing description is a missing generator input.

**R2a — descriptions must say something.** A description of `|Order ID.` on
a field named `orderId` satisfies presence and starves generation. The test
enforces a floor: a description must be longer than its brief, and must not
merely restate the definition's own name.

*Source: Part B item 3.*

## R3 — The glossary is real

**Terms are defined for the domain vocabulary**, not as a token gesture.

Synapify surfaces Terms as hover-docs and doc-comments in generated code
(**C1**), and Terms are the first item in B3's inclusion census. A model with
two terms for a four-domain business teaches a generator almost nothing.

*Source: Part C item 1; Part B item 3.*

## R4 — UI intent is expressed in the model

For riddlg's UI generator (**B4**): groups become a component tree, inputs
become controls emitting the modeled messages, and outputs become
subscriptions rendering the modeled results **via `put` statements**.

Therefore:

- every application-intent context that has outputs uses `put`
- every declared `input` and `output` is reachable from an epic step
- groups exist per screen, not one group for an entire business

*Source: Part B item 4.*

## R5 — Epics are test specifications

riddlg turns an Epic into a Feature, a Use Case into a Scenario using that
case's **own user story** as the narrative, and interactions into steps
(**B1**). The block kinds are not stylistic:

| Construct | Generated meaning |
|---|---|
| sequential block | asserts order |
| parallel block | order-tolerant "eventually" assertions |
| optional block | spawns scenario variants |
| refusal step | asserts InvariantViolated |
| vague / arbitrary step | AI attempts translation; blocks for a human if it cannot (**B3**) |

So every use case needs a user story, and a model intended to exercise the
test generator must use each block kind at least once.

*Source: Part B items 1 and 3.*

## R6 — Personas are real users

Load-test generation (**B2**) builds per-persona simulated actors scaled into
load profiles. `user` definitions therefore need descriptions that
characterise behaviour, not just a name.

*Source: Part B item 2.*

## R7 — Authors carry contact data

When a generated artifact hits an impossible situation, the message must
carry **"Notify: ⟨author⟩"** with contact details — which is why Author
definitions hold contact data at all. The system must *not* auto-notify.

*Source: Part B item 5.*

## R8 — Identity is durable where it matters

Generators should prefer a definition's ULID over its name as the durable
identifier, so identity survives renames (**B6**). ULID attachments in
metadata map an external tool's identity onto AST definitions.

*Source: Part B item 6.*

## R9 — Versions exist so staleness is detectable

Synapify's git-based type-delta warning (**C2**) reports when a type's
content changed but its containing scope's version did not. With no `version`
anywhere, the check has nothing to compare against.

*Source: Part C item 2.*

## R10 — Clean under the validator

**Zero errors and zero warnings**, at the pinned riddlc. A warning is riddl
telling you the model says something it did not mean; a generator consuming
it will faithfully reproduce the mistake.

## R11 — Survives the round trip

The model must survive `prettify` and `bastify`/`unbastify` byte-identically
(`scripts/verify-bast-roundtrip.sh`). Synapify loads `.bast`, so anything
that does not round-trip is something Synapify cannot see.

## R12 — Canonical forms only

No deprecated spellings — not `option is external`, not an `inlet_ref` as a
`send` target. Generators and human readers both learn from this model, and a
deprecated form teaches the wrong thing.

---

## Applying these beyond reactive-bbq

R1, R2, R10, R11 and R12 are reasonable for every model in the corpus.
R3-R9 are specific to being a *reference* model for the two tools, and are
enforced only against reactive-bbq.

The intent is that these rules move upstream: riddlc reporting, at the end of
a run, whether a model is fit for simulation and for generation and why not.
That proposal is filed in `../riddl/task/`.
