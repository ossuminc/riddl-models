# Code Generator Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a RIDDL model of a generic RIDDL code generator at
`tooling/code-generator/`, holding the corpus at zero findings of every
severity, and apply the design's documentation consequences.

**Architecture:** One domain, `CodeGeneration`, with seven bounded contexts
and a domain-level saga that addresses contexts rather than reaching into
them. Target-awareness is confined to `Planning`, where a `LoweringRule`
catalogue keyed by `(definitionKind, paradigm)` is selected through a
`TargetProfile` per target. An application context, `GeneratorDriver`,
drives the pipeline and is what makes each context's command inlet
reachable.

**Tech Stack:** RIDDL 2.0 (`riddlc 2.0.0-rc.26`), sbt 2 with `sbt-riddl`
`2.0.0-rc.24` and `sbt-ossuminc` 3.1.0. No Scala is written by this plan —
the deliverable is a model plus documentation.

**Spec:** `docs/superpowers/specs/2026-08-26-code-generator-model-design.md`
— approved by Reid 2026-08-26, including Appendix A. Read it alongside this
plan; the plan argues from it and does not restate its reasoning.

**Verified skeleton:** `docs/superpowers/reference/verified-skeleton.riddl`
— a 434-line model in prettify-canonical form that validates at **0 errors,
0 warnings with style, usage, missing and completeness all on**, measured
this session with `2.0.0-rc.26`. It contains a working instance of every
structural pattern this plan needs: domain with author and version,
application driver context, persistent cross-boundary connector, context
boundary relay, event-sourced entity with `on init`, projector, repository
with `Persist` commands, a two-step domain-level saga addressing a context,
and the error sink. **Copy shapes from it rather than inventing them.**

---

## Global Constraints

Every task's requirements implicitly include this section.

- **riddlc binary:** `~/.cache/riddlc/2.0.0-rc.26/bin/riddlc`. Confirm with
  `riddlc info` before trusting any result — it must report
  `version: 2.0.0-rc.26`, git commit `c64f3388f`. **Never use
  `../bin/riddlc`**, which is currently `2.0.0-rc.25-11-5e09d98c`, a whole
  tag behind. Scripts in `scripts/` default to the stale one; pass
  `RIDDLC=` explicitly.
- **Zero findings of every severity** — errors, warnings, style, usage,
  missing and completeness. This is spec criterion 3 and it is the gate for
  every task, not just the last.
- **The `.conf` carries only `input-file`.** Do not copy the corpus's usual
  `common { show-style-warnings = false … }` block. Suppressing classes
  would make `sbt v` lenient for this model; carrying only `input-file`
  (as `language-coverage.conf` does) makes `sbt v` enforce the zero
  standard directly.
- **Prettify before every commit:** `sbt r`, or
  `riddlc prettify <entry>.riddl -o <dir>`. `sbt pc` gates it and
  `riddlcValidate` depends on it. Prettify is verified idempotent at
  rc.26, so a second run is a no-op and a safe check.
- **Every definition needs `briefly` and `described as`.** A missing one is
  a `missing` finding and fails the gate. `described as` uses the `|`
  markdown form, and the closing `}` must be on its own line — `|` consumes
  everything to end of line.
- **On-clause bindings must not collide with field names.** `on alphaDone:
  event AlphaDone` where the state record has a field `alphaDone` draws both
  `name-shadows-definition` and `handler-binding-shadows-field`. Name the
  binding for its role, not its type: `doneEvent`, `undoneEvent`. The same
  applies to `let` names.
- **Cross-context connectors must be `persistent connector`**, a keyword
  prefix. Intra-context ones must not be.
- **Saga steps address contexts, never their internals** — `tell x to
  context Foo`, never `to entity Foo.Bar`. riddlc does not yet enforce this
  (spec §6.1); the model adopts it now.
- **Every context a saga addresses needs an inbound connector to one of its
  inlets**, or `tell` draws `msg-tell-target-unreachable`. A `tell` does not
  itself count for reachability. In this model that connector always comes
  from `GeneratorDriver`. **This was the plan's biggest unknown and is now
  settled** — see the skeleton.
- **Sagas need at least 2 steps** (`saga-too-few-steps`) and a timeout
  (`option timeout("PT10M")`).
- **A stateless context declares an INLET ONLY and its boundary handler does
  the work directly.** The relay pattern forwards inbound commands to a
  contained entity's inlet; a context with no aggregate has no such consumer,
  so a relay outlet would dangle and draw `stream-portlet-unconnected`.
  Ascription follows arity as always: `(0 out, 1 in)` = `sink`. A verified
  instance is `docs/superpowers/reference/verified-stateless-context.riddl`
  (80 definitions, 0 errors, 0 warnings, all four classes on). Applies to
  `SpecEmission` (Task 4) and shapes `Proving` (Task 7), which is `flow`
  because it still declares its `ProofFailures` outlet.
- **A context with entities needs a repository** — otherwise
  `context-entities-without-repository`. An entity that sends must declare
  an outlet — otherwise `entity-no-outlet`.
- **Shape ascriptions are derived from arity, not chosen.** `(1 out, 0 in)`
  = `source`, `(0,1)` = `sink`, `(1,1)` = `flow`, `(≥2,1)` = `split`,
  `(1,≥2)` = `merge`, `(≥2,≥2)` = `router`, `(0,0)` = `void`. Let
  `riddlc --provide-tips validate` tell you rather than deriving by hand.
- **Markdown files use an 80-column limit** — `CLAUDE.md`, `README.md`,
  `NOTEBOOK.md`, `BACKLOG.md`.
- **Commit messages go through a FILE**: write with the Write tool, then
  `git commit -F <file>`. Never `git commit -m`, never a heredoc.
  Backticks in a double-quoted shell string are command substitution and
  have previously written live credentials into a commit. Read the message
  back with `git log -1 --format=%B`.
- **Commits are single-purpose.** One task, one commit.
- **A reference's KEYWORD must match the referent's DECLARATION keyword.**
  `record PackagePath is {…}` is referenced as `requires record PackagePath`;
  `type SpendForPoints is {…}` as `requires type SpendForPoints`. Mismatching
  them is `ref-wrong-keyword`. The corpus contains both forms for exactly this
  reason (`LoyaltyContext.riddl:57` vs `OrderFulfillmentSaga.riddl:29`) —
  neither is "the" spelling, the declaration decides. Same applies to a
  repository inlet naming a single command: `is command X`, not `is type X`.
- **`forward` requires the handled message to declare `yields` or `replies`.**
  A boundary relay can only `forward` a command that yields an event. Where a
  context has no aggregate its commands declare no `yields`, so its boundary
  uses `send` (or does the work directly — see the stateless rule below).
- **An `Id(X)` type is declared at CONTEXT scope, never inside the entity.**
  riddlc reports `entity-id-defined-inside` — "move it to the containing
  context so other entities can reference it" — as a completeness finding,
  which fails the gate. So the path is `Intake.GenerationRunId`, NOT
  `Intake.GenerationRun.GenerationRunId`. Verified by measurement 2026-08-27;
  the reference skeleton declares `WidgetId` at context scope for this reason.
- **`any of { }` separates its enumerators with COMMAS; `one of { }`
  separates its alternates with `or`.** Writing `any of { A or B }` PARSES —
  and silently creates a third enumerator named `or`. Measured: the `or` form
  reported 5 definitions where the comma form reported 4, with extra
  `name-too-short` style findings against the invented `or`. A wrong
  separator here is not a syntax error, it is a wrong model.
- **Cross-context type references must be fully qualified** —
  `CodeEmission.ArtifactId`, not `ArtifactId`. A
  reference that does not resolve from where it is written is an error,
  and the path must carry every enclosing scope. Within one context the
  short form is correct.

### The validation command, used in every task

```bash
RIDDLC=~/.cache/riddlc/2.0.0-rc.26/bin/riddlc
$RIDDLC --no-ansi-messages validate tooling/code-generator/code-generator.riddl 2>&1 | tail -30
```

**Read both streams.** `validate` has no stdout product — its diagnostics go
to **stderr**. A harness reading stdout alone reports a clean corpus always,
whatever is wrong. The `2>&1` above is load-bearing.

A clean run prints exactly:

```
N definitions checked, 0 errors, 0 warnings  [style, usage, missing, completeness on]
```

If the trailing bracket does not list all four classes, the run measured
less than you think.

---

## File Structure

Flat, one file per context plus one per aggregate. The corpus's largest
model (reactive-bbq) uses subdirectories and `CLAUDE.md` records that this
has repeatedly caused non-recursive globs to skip it; a flat layout is the
documented default and is what this model uses.

```
tooling/code-generator/
├── code-generator.conf          Task 1  — input-file only, no `common` block
├── code-generator.riddl         Task 1  — domain entry: author, version,
│                                          includes, saga, cross-context
│                                          connectors, error-sink wiring
├── Operations.riddl             Task 1  — error-sink context
├── GeneratorDriver.riddl        Task 2  — application context; the driver
│                                          that makes context inlets
│                                          reachable
├── types.riddl                  Task 2  — domain-level shared types
├── IntakeContext.riddl          Task 2  — + GenerationRun entity, its
├── GenerationRun.riddl          Task 2    projector and repository
├── NamingContext.riddl          Task 3  — functions only, no ports
├── PlanningContext.riddl        Task 4  — LoweringRule + TargetProfile
├── SpecEmissionContext.riddl    Task 5
├── CodeEmissionContext.riddl    Task 6  — + Artifact entity, Decision repo
├── Artifact.riddl               Task 6
├── HoleFillingContext.riddl     Task 7  — + Hole entity
├── Hole.riddl                   Task 7
├── ProvingContext.riddl         Task 8  — the retry event cycle
├── README.md                    Task 11 — no NAICS code
└── code-generator.bast          Task 13 — generated, committed
```

Each context file is self-contained: its own types, ports, boundary
handler, aggregates, projector, repository and intra-context connectors.
Cross-context connectors and the saga live in the entry file, because they
span contexts and RIDDL 2.0 scopes them to the domain.

**Why a file per context.** Each context is independently reviewable and
independently validated — a task can add one, drive it to zero, and commit
without touching another. Files that change together stay together: an
aggregate's commands, events, states and handlers are one file because
changing any one of them changes the others.

---

## Task 1: Scaffold the model and register it in the corpus

The smallest thing that is a real corpus model: a domain, an error sink,
and the census edits that make the build see it. Nothing generator-specific
yet — this task proves the harness before any content depends on it.

**Files:**
- Create: `tooling/code-generator/code-generator.conf`
- Create: `tooling/code-generator/code-generator.riddl`
- Create: `tooling/code-generator/Operations.riddl`

**Interfaces:**
- Consumes: nothing.
- Produces: `domain CodeGeneration`; `context Operations` with
  `inlet ErrorSink`. Later tasks add `include` lines to
  `code-generator.riddl` and nothing else in it.

- [ ] **Step 1: Create the directory and the `.conf`**

```bash
mkdir -p tooling/code-generator
```

`tooling/code-generator/code-generator.conf` — **only `input-file`**. The
corpus's usual `common { show-style-warnings = false … }` block is
deliberately omitted so `sbt v` enforces every severity for this model:

```hocon
validate {
  input-file = "code-generator.riddl"
}
```

- [ ] **Step 2: Write `Operations.riddl`**

The error-sink context. All 190 existing models carry this pattern; it is
not optional.

```riddl
context Operations as sink is {
  inlet ErrorSink is record Riddl.GeneratorError with {
    option error-sink()
    briefly "Hard error destination"
    described as {
      |Where hard errors raised anywhere in this domain are delivered.
    }
  }
} with {
  briefly "Domain-wide operational concerns"
  described as {
    |Holds the domain error sink, which belongs to no one context. A
    |generator's hard failures are domain-wide: a refused model, an
    |unfillable hole and a failed proof are all the same kind of stop.
  }
}
```

- [ ] **Step 3: Write `code-generator.riddl`**

```riddl
domain CodeGeneration is {
  author OssumInc is {
    name = "Ossum Inc."
    email = "info@ossuminc.com"
  } with {
    briefly "Author of this model"
    described as {
      |Ossum Inc., creators of RIDDL.
    }
  }
  version 1 with {
    briefly "Model version"
    described as {
      |The model's version, not the RIDDL language version. A definition's
      |precise version is its versioned ancestors composed root-to-leaf and
      |joined with '.', so this is the leading component for everything
      |beneath it.
    }
  }
  include "Operations.riddl"
  connector ErrorsToSink is from outlet Riddl.ForeverEmpty.void to inlet Operations.ErrorSink with {
    briefly "Hard errors to the domain error sink"
    described as {
      |No modelled component emits a GeneratorError; generators do, at run
      |time. ForeverEmpty states that honestly rather than inventing a
      |producer.
    }
  }
} with {
  briefly "Generic RIDDL code generation"
  described as {
    |A model whose subject is how you generate code for a RIDDL model. Its
    |reader is someone building a new generator — for TypeScript/Effect,
    |for Pekko/Scala, or for whatever a client needs — and it states what a
    |generator is made of and what each stage owes.
  }
}
```

- [ ] **Step 4: Validate — expect zero**

```bash
RIDDLC=~/.cache/riddlc/2.0.0-rc.26/bin/riddlc
$RIDDLC --no-ansi-messages validate tooling/code-generator/code-generator.riddl 2>&1 | tail -10
```

Expected, exactly (measured this session on this content):

```
6 definitions checked, 0 errors, 0 warnings  [style, usage, missing, completeness on]
```

If the count is not 6, something in the three files differs from the text
above. If the bracket does not name all four classes, the `.conf` picked up
a `common` block it should not have.

- [ ] **Step 5: Prettify and confirm canonical form**

```bash
$RIDDLC prettify tooling/code-generator/code-generator.riddl -o /tmp/cg-pretty
diff -r /tmp/cg-pretty tooling/code-generator/
```

Copy any differences back into the sources. Prettify is idempotent at
rc.26, so a second run must produce no further change.

- [ ] **Step 6: Confirm the build sees it — census 190 → 191**

```bash
$RIDDLC validate --corpus . 2>&1 | tail -3
sbt v
sbt pc
```

Expected: `191 models, 0 failed, 191 ok`; both sbt tasks green. If the
census still says 190, the `.conf` is not being discovered — check the
filename matches `input-file` and that the directory is not under
`patterns/`.

- [ ] **Step 7: Commit**

Write the message to a file first — never `-m`.

```bash
git add tooling/code-generator/
git commit -F /tmp/commit-msg.txt
git log -1 --format=%B
git status --short
```

---
## Task 2: The driver, shared types, and the Intake context

The template task. It establishes the per-context pattern every later
context repeats: boundary relay, aggregate, projector, repository, driver
outlet, and the two connectors that make the context reachable. Tasks 3–8
add contexts in exactly this shape.

`Intake` loads the model and applies the **generability bar** (spec §4.3):
a *conforming* model has no Errors; a *generable* model has no Errors and
no warnings other than Style. Completeness, missing and usage warnings are
hard stops, because code cannot be generated from unstated intent.

**Files:**
- Create: `tooling/code-generator/types.riddl`
- Create: `tooling/code-generator/GeneratorDriver.riddl`
- Create: `tooling/code-generator/IntakeContext.riddl`
- Create: `tooling/code-generator/GenerationRun.riddl`
- Modify: `tooling/code-generator/code-generator.riddl` — add four
  `include` lines and one persistent connector

**Interfaces:**
- Consumes: `domain CodeGeneration` (Task 1).
- Produces:
  - `type CodeGeneration.ModelRef`, `type CodeGeneration.Severity` —
    domain-level shared types every later context uses.
  - `context GeneratorDriver` with `outlet IntakeCommands is type
    Intake.IntakeCommand`. **Later tasks add one outlet per context they
    introduce, named `<Context>Commands`, and one persistent connector in
    the entry file.** The driver stays `as source`.
  - `context Intake` with `inlet IntakeCommandsIn`, `outlet
    IntakeCommandsFwd`, and `type IntakeCommand is one of {
    GenerationRun.StartRun or GenerationRun.AdmitModel or
    GenerationRun.RefuseModel }`.
  - `entity Intake.GenerationRun` with `event ModelAdmitted`, which Task 8's
    saga depends on.
  - `type Intake.GenerationRunId is Id(GenerationRun)`, declared at
    **context** scope beside the entity, not inside it — see Global
    Constraints. Tasks 4 and 7 consume it as `Intake.GenerationRunId`.

- [ ] **Step 1: Write `types.riddl` — domain-level shared types**

Domain-level types belong to the domain's package (spec §4.4), so anything
more than one context needs lives here.

```riddl
type ModelRef is String(1,1024) with {
  briefly "Reference to the RIDDL model being generated from"
  described as {
    |A path to a `.riddl` entry file or to a `.bast`. A generator accepts
    |either, because a `.bast` is the same model already parsed.
  }
}
type Severity is any of {
  Error, Warning, Style, Usage, Missing, Completeness
} with {
  briefly "Severity of a riddlc diagnostic"
  described as {
    |The classes riddlc reports. The generability bar (§4.3) admits a model
    |carrying Style and nothing else, so the distinction between these is
    |operational rather than presentational.
  }
}
```

- [ ] **Step 2: Write `GeneratorDriver.riddl` — the application context**

**This is what makes the saga work.** A `tell` does not count for
reachability, so without an inbound connector to a context's inlet every
saga step draws `msg-tell-target-unreachable`. The driver is the process
that starts a run and issues its commands; it is honest modelling and it
satisfies the rule.

```riddl
application context GeneratorDriver as source is {
  outlet IntakeCommands is type Intake.IntakeCommand with {
    briefly "Intake commands from the driver"
    described as {
      |Where the driver publishes the commands that begin a run.
    }
  }
} with {
  briefly "The process that runs a generation"
  described as {
    |A command-line invocation, a serve-mode request, or a test harness.
    |It is modelled because the pipeline's contexts must be reachable from
    |somewhere, and pretending a saga reaches them by itself would leave
    |every step unreachable.
  }
}
```

- [ ] **Step 3: Write `GenerationRun.riddl` — the aggregate**

Three lifecycle states. `Loading` is initial; a run either reaches
`Admitted` or `Refused`, and both are terminal. Note the binding names
(`startedEvent`, `admittedEvent`) — they must not match any field.

The id type is declared at **context** scope, so it goes in
`IntakeContext.riddl` (Step 4) rather than in this file:

```riddl
  type GenerationRunId is Id(GenerationRun) with {
    briefly "Generation run identifier"
    described as {
      |Identifies one invocation of the generator. Declared at context scope
      |so other definitions in Intake can reference it; riddlc rejects an
      |Id type declared inside the entity it identifies.
    }
  }
```

And the entity itself:

```riddl
event-sourced entity GenerationRun as flow is {
  type GenerationRunEvent is one of {
    GenerationRun.RunStarted or GenerationRun.ModelAdmitted or GenerationRun.ModelRefused
  } with {
    briefly "GenerationRun event alternation"
    described as {
      |Events published by the GenerationRun entity.
    }
  }
  inlet GenerationRunCommands is type Intake.IntakeCommand with {
    briefly "Commands routed to this run"
    described as {
      |Commands relayed from the Intake boundary.
    }
  }
  outlet GenerationRunEvents is type GenerationRunEvent with {
    briefly "Events this run publishes"
    described as {
      |Lifecycle events, consumed by the projection that persists them.
    }
  }
  command StartRun yields event RunStarted is {
    generationRunId: GenerationRunId with {
      briefly "Run"
      described as {
        |The run being started.
      }
    }
    subjectModel: ModelRef with {
      briefly "Model"
      described as {
        |The model to generate from.
      }
    }
  } with {
    briefly "Start a generation run"
    described as {
      |Begins a run against a named model, before anything is known about
      |whether that model can be generated from.
    }
  }
  command AdmitModel yields event ModelAdmitted is {
    generationRunId: GenerationRunId with {
      briefly "Run"
      described as {
        |The run whose model passed the bar.
      }
    }
  } with {
    briefly "Admit the model"
    described as {
      |Records that the model cleared the generability bar.
    }
  }
  command RefuseModel yields event ModelRefused is {
    generationRunId: GenerationRunId with {
      briefly "Run"
      described as {
        |The run whose model failed the bar.
      }
    }
    blockingSeverity: Severity with {
      briefly "Blocking class"
      described as {
        |The severity class that blocked admission. Style never blocks.
      }
    }
  } with {
    briefly "Refuse the model"
    described as {
      |Records that the model failed the generability bar, and on what.
    }
  }
  event RunStarted is {
    generationRunId: GenerationRunId with {
      briefly "Run"
      described as {
        |The run that started.
      }
    }
    subjectModel: ModelRef with {
      briefly "Model"
      described as {
        |The model it will generate from.
      }
    }
  } with {
    briefly "Run started"
    described as {
      |A run came into existence.
    }
  }
  event ModelAdmitted is {
    generationRunId: GenerationRunId with {
      briefly "Run"
      described as {
        |The run admitted.
      }
    }
  } with {
    briefly "Model admitted"
    described as {
      |The model cleared the bar and the pipeline may proceed.
    }
  }
  event ModelRefused is {
    generationRunId: GenerationRunId with {
      briefly "Run"
      described as {
        |The run refused.
      }
    }
    blockingSeverity: Severity with {
      briefly "Blocking class"
      described as {
        |What blocked it.
      }
    }
  } with {
    briefly "Model refused"
    described as {
      |The model failed the bar; nothing downstream runs.
    }
  }
  record GenerationRunData is {
    generationRunId: GenerationRunId with {
      briefly "Run"
      described as {
        |The run this state belongs to, carried through every state so the
        |record can be rebuilt by replaying the event log.
      }
    }
    subjectModel: ModelRef with {
      briefly "Model"
      described as {
        |The model under generation.
      }
    }
    admissionBlocker: Severity? with {
      briefly "Blocker"
      described as {
        |What blocked admission, absent while the run is still loading and
        |on a run that was admitted.
      }
    }
  } with {
    briefly "Generation run state data"
    described as {
      |Full state of a run, shared across all its states.
    }
  }
  initial state Loading of record GenerationRun.GenerationRunData is {
    initial handler LoadingInit is {
      on init is {
        let creation: type RunStarted = prompt("the run started that brings this generation run into existence")
        yield creation
      }
    } with {
      briefly "Loading init handler"
      described as {
        |Brings the run into existence by yielding its entering event.
      }
    }
    handler LoadingHandler is {
      on command AdmitModel is {
        yield event ModelAdmitted(generationRunId = AdmitModel.generationRunId)
      }
      on admittedEvent: event ModelAdmitted is {
        send admittedEvent to outlet Intake.GenerationRun.GenerationRunEvents
        morph entity Intake.GenerationRun to state Intake.GenerationRun.Admitted with record GenerationRun.GenerationRunData(generationRunId = admittedEvent.generationRunId, subjectModel = GenerationRunData.subjectModel, admissionBlocker = empty)
      }
      on command RefuseModel is {
        yield event ModelRefused(generationRunId = RefuseModel.generationRunId, blockingSeverity = RefuseModel.blockingSeverity)
      }
      on refusedEvent: event ModelRefused is {
        send refusedEvent to outlet Intake.GenerationRun.GenerationRunEvents
        morph entity Intake.GenerationRun to state Intake.GenerationRun.Refused with record GenerationRun.GenerationRunData(generationRunId = refusedEvent.generationRunId, subjectModel = GenerationRunData.subjectModel, admissionBlocker = refusedEvent.blockingSeverity)
      }
      on startedEvent: event RunStarted is {
        send startedEvent to outlet Intake.GenerationRun.GenerationRunEvents
      }
      on other is {
        error "Unexpected message for GenerationRun while Loading"
      }
    } with {
      briefly "Loading state handler"
      described as {
        |Applies the generability bar's verdict. The bar itself is riddlc's
        |judgement, not this entity's: the entity records which way it went.
      }
    }
  } with {
    briefly "Loading state"
    described as {
      |The model is being read and checked. No artifact exists yet.
    }
  }
  state Admitted of record GenerationRun.GenerationRunData is {
    initial handler AdmittedInit is {
      on init is {
        let entering: type ModelAdmitted = prompt("the model admitted that enters this state")
        yield entering
      }
    } with {
      briefly "Admitted init handler"
      described as {
        |Enters the admitted state.
      }
    }
    handler AdmittedHandler is {
      on other is {
        error "A run that has been admitted accepts no further commands"
      }
    } with {
      briefly "Admitted state handler"
      described as {
        |Terminal. The pipeline proceeds from here by saga, not by further
        |commands to this run.
      }
    }
  } with {
    briefly "Admitted state"
    described as {
      |The model cleared the bar.
    }
  }
  state Refused of record GenerationRun.GenerationRunData is {
    initial handler RefusedInit is {
      on init is {
        let entering: type ModelRefused = prompt("the model refused that enters this state")
        yield entering
      }
    } with {
      briefly "Refused init handler"
      described as {
        |Enters the refused state.
      }
    }
    handler RefusedHandler is {
      on other is {
        error "A run that has been refused accepts no further commands"
      }
    } with {
      briefly "Refused state handler"
      described as {
        |Terminal. A refusal is the generator's answer, not a retryable
        |condition: the model has to change.
      }
    }
  } with {
    briefly "Refused state"
    described as {
      |The model failed the bar. Nothing downstream runs.
    }
  }
} with {
  briefly "One invocation of the generator"
  described as {
    |The only thing in Intake with identity and a lifecycle. Its states are
    |the admission decision, which is the whole of what Intake does.
  }
}
```

- [ ] **Step 4: Write `IntakeContext.riddl` — boundary, projector, repository**

Copy the boundary-relay, projector and repository shapes from
`docs/superpowers/reference/verified-skeleton.riddl`, which contains a
verified instance of each. The context is `as flow` (one inlet, one
outlet). It must contain, in this order:

1. `type IntakeCommand is one of { GenerationRun.StartRun or
   GenerationRun.AdmitModel or GenerationRun.RefuseModel }`
2. `inlet IntakeCommandsIn is type IntakeCommand`
3. `outlet IntakeCommandsFwd is type IntakeCommand`
4. `handler IntakeBoundary` with one `on <binding>: command
   GenerationRun.<Cmd> is { forward <binding> to outlet
   Intake.IntakeCommandsFwd }` clause **per concrete command** — an
   alternation binding is a value, not a message, so a generic relay is not
   expressible — plus `on other is { error "Unexpected message at the
   Intake boundary" }`
5. `type IntakeRepositoryCommand is one of {
   GenerationRunRepository.PersistRunStarted or
   GenerationRunRepository.PersistModelAdmitted or
   GenerationRunRepository.PersistModelRefused }`
6. `projector GenerationRunProjection as flow` with `updates repository
   Intake.GenerationRunRepository`, an inlet of `type
   GenerationRun.GenerationRunEvent`, an outlet of `type
   Intake.IntakeRepositoryCommand`, and one clause per event issuing
   `tell command Intake.GenerationRunRepository.Persist<Event>(...) to
   repository Intake.GenerationRunRepository`
7. `repository GenerationRunRepository as sink` with an inlet of `type
   Intake.IntakeRepositoryCommand`, a `record StoredGenerationRun`, a
   `schema` indexed on the id, the three `Persist…` commands (**no
   `yields`** — storing a row records no new entity state), and a handler
   with `do "…"` prose per command
8. `include "GenerationRun.riddl"`
9. Three intra-context connectors — **not** persistent:
   - `'IntakeCommand Intake'` from `Intake.IntakeCommandsFwd` to
     `Intake.GenerationRun.GenerationRunCommands`
   - `'GenerationRunProjection Feed'` from
     `Intake.GenerationRun.GenerationRunEvents` to the projector's inlet
   - `'GenerationRunProjection Storage'` from the projector's outlet to
     the repository's inlet

- [ ] **Step 5: Wire it into the entry file**

Add to `code-generator.riddl`, before the `ErrorsToSink` connector:

```riddl
  include "types.riddl"
  include "GeneratorDriver.riddl"
  include "IntakeContext.riddl"
  persistent connector 'IntakeCommand Stream' is from outlet GeneratorDriver.IntakeCommands to inlet Intake.IntakeCommandsIn with {
    briefly "Intake commands from the driver"
    described as {
      |Carries the commands that begin a run from the driver to the Intake
      |boundary. Persistent because it crosses a context boundary, where
      |durability can be required for model correctness.
    }
  }
```

- [ ] **Step 6: Validate — drive to zero**

```bash
RIDDLC=~/.cache/riddlc/2.0.0-rc.26/bin/riddlc
$RIDDLC --no-ansi-messages validate tooling/code-generator/code-generator.riddl 2>&1 | tail -30
```

Expected: `0 errors, 0 warnings  [style, usage, missing, completeness on]`.

The findings you are most likely to see first, and what each means:

| Finding | Cause |
|---|---|
| `msg-tell-target-unreachable` | Step 5's persistent connector is missing |
| `stream-portlet-unconnected` | A port with no connector — check all four |
| `context-entities-without-repository` | Step 4 item 7 omitted |
| `entity-no-outlet` | The entity sends but declares no outlet |
| `stream-boundary-not-persistent` | Step 5's connector lacks `persistent` |
| `name-shadows-definition` | A binding or `let` matches a field name |
| `use-unused-definition` | A type nothing references — delete it, do not keep it as documentation |

- [ ] **Step 7: Prettify, re-validate, commit**

```bash
$RIDDLC prettify tooling/code-generator/code-generator.riddl -o /tmp/cg-pretty
diff -r /tmp/cg-pretty tooling/code-generator/    # copy differences back
$RIDDLC --no-ansi-messages validate tooling/code-generator/code-generator.riddl 2>&1 | tail -3
sbt v && sbt pc
git add tooling/code-generator/
git commit -F /tmp/commit-msg.txt
git log -1 --format=%B
```

---
## Task 3: Naming and Planning

**These two contexts ship together, and that is forced.** A function nothing
calls is reported `use-unused-definition`, so `Naming` cannot reach zero on
its own — it needs its first caller in the same commit. Planning's lowering
is that caller. Splitting them would mean a task that ends red, which this
plan does not allow.

`Naming` is functions only, no ports and no processors — verified legal and
callable cross-context (spec §6.2). The saga never addresses it, so it needs
no driver outlet and no connector.

`Planning` is where **all target-awareness is confined** (spec §4.5.1).
Everything upstream and downstream is target-agnostic.

**Files:**
- Create: `tooling/code-generator/NamingContext.riddl`
- Create: `tooling/code-generator/PlanningContext.riddl`
- Modify: `tooling/code-generator/types.riddl` — add `Paradigm`,
  `DefinitionKind`, `Capability`
- Modify: `tooling/code-generator/code-generator.riddl` — two includes, one
  driver outlet's connector
- Modify: `tooling/code-generator/GeneratorDriver.riddl` — add
  `outlet PlanningCommands`

**Interfaces:**
- Consumes: `type ModelRef` (Task 2); `context GeneratorDriver` (Task 2).
- Produces:
  - `type CodeGeneration.Paradigm`, `type CodeGeneration.DefinitionKind`,
    `type CodeGeneration.Capability` — used by Tasks 5, 6 and 9.
  - `function Naming.DerivePackage`, `function Naming.Sanitize`.
  - `repository Planning.LoweringCatalogue` and
    `repository Planning.TargetProfiles`.
  - `context Planning` with `inlet PlanningCommandsIn`, `outlet
    PlanningCommandsFwd`, and `type PlanningCommand`, which Task 8's saga
    addresses.

- [ ] **Step 1: Add the three shared types to `types.riddl`**

`Paradigm` is the spec's §2.3.3 taxonomy, minus the two rows Reid dropped.
Its **order is the precedence** — highest first — and that ordering is the
model's central claim, so it is stated once, here.

```riddl
type Paradigm is any of {
  Actor, ActiveObject, CspProcess, Service, DddAggregate, ReactiveStream, Component, MonadicStateMachine, PlainObject, Dci
} with {
  briefly "A target's representation for a RIDDL processor"
  described as {
    |The kinds of computing abstraction a target can offer, in order of
    |precedence — highest first. A RIDDL processor already is an actor:
    |serial per identity, parallel across identities, interacting only over
    |abstract channels. So Actor costs no facade, and every step down the
    |list is a guarantee the generator must build instead of inherit.
    |
    |Membership is decided by one test: the paradigm must bundle data with
    |behaviour. Entity-Component-System and tuple spaces are excluded for
    |failing it — they hold inert state with behaviour elsewhere, and there
    |is no boundary to generate into.
  }
}
type Capability is any of {
  SerialExecution, AddressableIdentity, ChannelInteraction, DurableJournal
} with {
  briefly "A guarantee a lowering requires of its target"
  described as {
    |What a construct needs in order to carry a RIDDL processor's meaning.
    |A paradigm supplies some natively; the rest become facades the
    |generator emits. Owing a capability never disqualifies a target — only
    |failing to bundle data with behaviour does.
  }
}
type DefinitionKind is any of {
  DomainKind, ContextKind, EntityKind, RepositoryKind, ProjectorKind, ProcessorKind, AdaptorKind, SagaKind, FunctionKind, TypeKind, HandlerKind, ConnectorKind, EpicKind
} with {
  briefly "The RIDDL definition kinds a generator must lower"
  described as {
    |One member per kind of definition that produces an artifact. The
    |catalogue is keyed on this and on Paradigm.
  }
}
```

- [ ] **Step 2: Write `NamingContext.riddl`**

A context with only functions, no ports. Note that `call` is a **value**,
not a statement: `let x = call function F(args)` — a bare `call function
F(args)` is a parse error listing every statement keyword, which reads as
though the function is wrong. Note also that inline aggregation on
`requires`/`returns` is deprecated: declare named record types and
reference them.

```riddl
context Naming is {
  record PackagePath is {
    hierarchyPath: String(1,1024) with {
      briefly "Hierarchy"
      described as {
        |The definition's path from the root, joined with dots.
      }
    }
    basePackage: String(1,256) with {
      briefly "Base"
      described as {
        |The base package the derived path hangs from.
      }
    }
  } with {
    briefly "Input to package derivation"
    described as {
      |What DerivePackage needs: where a definition sits, and what it hangs
      |from.
    }
  }
  record DerivedPackage is {
    packageName: String(1,1024) with {
      briefly "Package"
      described as {
        |The derived package name.
      }
    }
  } with {
    briefly "Result of package derivation"
    described as {
      |The package a definition's artifacts belong to.
    }
  }
  record RawName is {
    sourceName: String(1,256) with {
      briefly "Raw"
      described as {
        |A name as the model spells it.
      }
    }
  } with {
    briefly "Input to sanitization"
    described as {
      |A name that may contain characters the target forbids.
    }
  }
  record SanitizedName is {
    safeName: String(1,256) with {
      briefly "Safe"
      described as {
        |The name with every character the target forbids replaced.
      }
    }
  } with {
    briefly "Result of sanitization"
    described as {
      |A name legal in the target language.
    }
  }
  function DerivePackage is {
    requires record PackagePath
    returns record DerivedPackage
    return prompt("basePackage followed by each segment of hierarchyPath, lower-cased, with every non-alphanumeric character mapped to underscore")
  } with {
    briefly "Derive a package from a definition's hierarchy"
    described as {
      |Package is base, then domain, then context. An `option namespace`
      |REPLACES the derived path rather than extending it, and becomes the
      |base for everything the scope contains. Precedence when they
      |disagree: model, then CLI flag, then config, then built-in.
    }
  }
  function Sanitize is {
    requires record RawName
    returns record SanitizedName
    return prompt("sourceName with every character illegal in the target language replaced by underscore")
  } with {
    briefly "Make a model name legal in the target"
    described as {
      |RIDDL permits names a target may not. Sanitization is per-target and
      |is the one naming concern that is not target-agnostic.
    }
  }
} with {
  briefly "Name derivation"
  described as {
    |Pure functions, no state and no ports. Nothing is told to Naming: it
    |is reached by call, which is why it declares no ports and the saga
    |never addresses it.
  }
}
```

- [ ] **Step 3: Write `PlanningContext.riddl`**

`Planning` follows Task 2's context shape exactly — boundary relay,
aggregate-free, two repositories, driver outlet, connectors. Its distinctive
content:

**`repository TargetProfiles as sink`** — one row per target:
- `record StoredTargetProfile` with fields `targetName: String(1,64)`,
  `processorKind: DefinitionKind`, `selectedParadigm: Paradigm`,
  `owedCapability: Capability?`
- `schema TargetProfileData is relational of profiles as record
  StoredTargetProfile index on field StoredTargetProfile.targetName`
- `command PersistTargetProfile` (no `yields`) and its handler clause

**`repository LoweringCatalogue as sink`** — one row per
`(definitionKind, paradigm)`:
- `record StoredLoweringRule` with fields `ruleDefinitionKind:
  DefinitionKind`, `ruleParadigm: Paradigm`, `requiredCapability:
  Capability`, `plannedArtifactKind: String(1,64)`, `preservedGuarantee:
  String(1,512)`
- `schema LoweringRuleData is relational of rules as record
  StoredLoweringRule index on field StoredLoweringRule.ruleDefinitionKind`
- `command PersistLoweringRule` (no `yields`) and its handler clause

**`type PlanningCommand is one of { Planning.PlanModel or
Planning.DiscardPlan }`** — the two the saga tells, with a boundary relay
clause for each.

**The two lowering functions**, which are what make the catalogue
self-enforcing (spec §4.5) and what call `Naming`:

```riddl
  record ParadigmSelection is {
    profileTarget: String(1,64) with {
      briefly "Target"
      described as {
        |The target whose profile decides.
      }
    }
    selectionKind: DefinitionKind with {
      briefly "Kind"
      described as {
        |The definition kind being lowered.
      }
    }
  } with {
    briefly "Input to paradigm selection"
    described as {
      |What SelectParadigm needs to consult a profile.
    }
  }
  record SelectedParadigm is {
    chosenParadigm: Paradigm with {
      briefly "Paradigm"
      described as {
        |The highest-precedence paradigm this target supplies for this kind.
      }
    }
  } with {
    briefly "Result of paradigm selection"
    described as {
      |What the catalogue is then keyed on.
    }
  }
  function SelectParadigm is {
    requires record ParadigmSelection
    returns record SelectedParadigm
    return prompt("the selectedParadigm recorded in TargetProfileData.profiles for profileTarget and selectionKind")
  } with {
    briefly "Choose the paradigm for a kind on a target"
    described as {
      |Half of the two-step selection: profile gives paradigm, then
      |catalogue gives rule. Keying the catalogue on paradigm rather than
      |on target is what stops it carrying one near-duplicate copy per
      |target — adding a target adds a profile, not forty rules.
    }
  }
```

`LowerDefinition` takes a `DefinitionKind` and a `Paradigm` and returns the
planned artifact's package, calling **both** `Naming.DerivePackage` and
`Naming.Sanitize` — which is what makes those functions used:

```riddl
  function LowerDefinition is {
    requires record LoweringRequest
    returns record PlannedArtifact
    let derived = call function Naming.DerivePackage(hierarchyPath = LoweringRequest.definitionPath, basePackage = LoweringRequest.basePackage)
    let safe = call function Naming.Sanitize(sourceName = LoweringRequest.definitionName)
    return prompt("a planned artifact in package derived.packageName named safe.safeName, per the catalogue rule for this kind and paradigm")
  } with {
    briefly "Lower one definition to a planned artifact"
    described as {
      |Consults the catalogue rather than hard-coding its rule. That is what
      |makes an unused rule visible as a `usage` finding, which this
      |corpus's zero standard turns into a build failure. It does not make a
      |MISSING rule visible; that gap is real and is stated in the spec.
    }
  }
```

Declare `record LoweringRequest` (fields `definitionPath`,
`definitionName`, `basePackage`, `requestKind: DefinitionKind`,
`requestParadigm: Paradigm`) and `record PlannedArtifact` (fields
`artifactPackage`, `artifactName`) alongside.

- [ ] **Step 4: Add the driver outlet and connector**

In `GeneratorDriver.riddl`, add `outlet PlanningCommands is type
Planning.PlanningCommand` with `briefly` and `described as`. In
`code-generator.riddl`, add the includes and:

```riddl
  persistent connector 'PlanningCommand Stream' is from outlet GeneratorDriver.PlanningCommands to inlet Planning.PlanningCommandsIn with {
    briefly "Planning commands from the driver"
    described as {
      |Carries planning commands from the driver to the Planning boundary,
      |which is what makes the saga's step to this context deliverable.
    }
  }
```

- [ ] **Step 5: Validate, prettify, commit**

```bash
RIDDLC=~/.cache/riddlc/2.0.0-rc.26/bin/riddlc
$RIDDLC --no-ansi-messages validate tooling/code-generator/code-generator.riddl 2>&1 | tail -30
```

Expected `0 errors, 0 warnings  [style, usage, missing, completeness on]`.

Two findings specific to this task:
- `use-unused-definition` naming a **Naming function** means Step 3's
  `LowerDefinition` does not actually call it. This is the whole reason the
  two contexts ship together — fix the call, do not delete the function.
- A parse error listing every statement keyword at a `call` line means the
  `let` is missing: `call` is a value, not a statement.

Then prettify, `sbt v && sbt pc`, and commit as in Task 2 Step 7.

---
## Task 4: SpecEmission

The suite derived from the model. **It is necessarily red** — it states what
the filled code must do and nothing has filled it yet. Red here is the
design, not a regression (spec §4.6). This context is stateless: no
aggregate, no repository, so no `context-entities-without-repository`.

**Files:**
- Create: `tooling/code-generator/SpecEmissionContext.riddl`
- Modify: `GeneratorDriver.riddl` — add `outlet SpecEmissionCommands`
- Modify: `code-generator.riddl` — include + persistent connector

**Interfaces:**
- Consumes: `type DefinitionKind`, `type ModelRef` (Tasks 2, 3).
- Produces: `context SpecEmission` with `type SpecEmissionCommand is one of
  { SpecEmission.EmitSpecs or SpecEmission.DiscardSpecs }`, addressed by
  Task 8's saga.

- [ ] **Step 1: Write the context**

**`SpecEmission` is stateless, so it takes the inlet-only shape** — `context
SpecEmission as sink`, an inlet, no relay outlet, and a boundary handler that
does the work directly. Copy the verified instance in
`docs/superpowers/reference/verified-stateless-context.riddl`. Following
Task 2's relay shape here would leave the relay outlet unconnected.

Distinctive content:

- `type SpecEmissionCommand is one of { SpecEmission.EmitSpecs or
  SpecEmission.DiscardSpecs }`
- `command EmitSpecs` — fields `specRunId: Intake.GenerationRunId`,
  `specSubject: ModelRef`. No `yields`: this context has no aggregate, so
  nothing records new entity state.
- `command DiscardSpecs` — field `specRunId`, for the saga's compensation.
- `handler SpecEmissionBoundary` — **one `on command <Cmd> is { do "…" }`
  clause per command, doing the work directly rather than forwarding**, plus
  `on other is { error "Unexpected message at the SpecEmission boundary" }`.
  A stateless context has nothing to forward to. The `described as` on this handler is where the CM aspects this
  emission preserves are stated (spec §5.2): they are acceptance criteria
  for the output, and their home in the model is a sentence here.

The `described as` on the context must say why the suite is red:

```riddl
} with {
  briefly "Emission of the derived test suite"
  described as {
    |Emits the suite derived from the model: what the generated code must
    |do, stated before anything does it. The suite is NECESSARILY RED on
    |emission — it asserts behaviour that only hole filling supplies — and
    |that is the design rather than a regression. It is why the two
    |emissions are separate contexts with different acceptance: the pass-1
    |gate cannot assert behaviour, and this is what it would have asserted.
  }
}
```

- [ ] **Step 2: Driver outlet, connector, validate, prettify, commit**

As Task 3 Step 4–5, with `'SpecEmissionCommand Stream'`. Expect
`0 errors, 0 warnings`.

---

## Task 5: CodeEmission

Structure and headers with `[[AI FILL]]` holes, plus a `Decision` record
wherever a non-obvious choice was made and why. `Artifact` is an aggregate:
a file identified by path, moving **Planned → Emitted → Filled → Verified**.

**Files:**
- Create: `tooling/code-generator/CodeEmissionContext.riddl`
- Create: `tooling/code-generator/Artifact.riddl`
- Modify: `GeneratorDriver.riddl`, `code-generator.riddl`

**Interfaces:**
- Consumes: `type DefinitionKind`, `type Paradigm` (Task 3).
- Produces: `entity CodeEmission.Artifact`; `type CodeEmission.ArtifactId is
  Id(Artifact)` at **context** scope beside the entity; and events `ArtifactPlanned`, `ArtifactEmitted`,
  `ArtifactFilled`, `ArtifactVerified`; `repository
  CodeEmission.DecisionLog`. Task 6 consumes `ArtifactId`; Task 7 consumes
  `event ArtifactFilled`.

- [ ] **Step 1: Write `Artifact.riddl`**

Four states, following Task 2's `GenerationRun` shape exactly. Commands
`PlanArtifact`, `EmitArtifact`, `FillArtifact`, `VerifyArtifact`, each
`yields` its past-tense event, each event with an `on <binding>: event`
clause that `send`s to the outlet and `morph`s to the next state.

State record `ArtifactData`: `artifactId: ArtifactId`, `artifactPath:
String(1,1024)`, `artifactParadigm: Paradigm`, `openHoleCount: Natural`.

`openHoleCount` is the terminating condition of Task 7's retry cycle — a
count reaching zero (spec §4.8) — so it is state, not a derived value.

Binding names: `plannedEvent`, `emittedEvent`, `filledEvent`,
`verifiedEvent`. **Not** `artifactPath` or `openHoleCount`, which are
fields.

- [ ] **Step 2: Write `CodeEmissionContext.riddl`**

Task 2's context shape, plus:

- `repository DecisionLog as sink` — `record StoredDecision` with fields
  `decisionArtifactId: CodeEmission.ArtifactId`, `decisionSubject:
  String(1,256)`, `decisionRationale: String(1,2048)`; a schema indexed on
  `decisionArtifactId`; `command PersistDecision` (no `yields`) and its
  handler clause.
- The projector that turns `Artifact` events into `Persist…` commands for
  an `ArtifactRepository`, exactly as Task 2 does for `GenerationRun`.
  `DecisionLog` is a **second** repository, written by the emission handler
  rather than by the projector — that is why it exists separately.
- The emission handler's `do` prose must name the header rule: the nearest
  scope's copyright, verbatim, in each artifact's comment syntax.

`described as` on the context states the split's reason:

```riddl
} with {
  briefly "Emission of framework, structure and headers"
  described as {
    |Emits what can be derived deterministically — structure, signatures,
    |headers, imports — and marks with a hole everything that cannot. A
    |generated artifact is not correct because it compiles; it is correct
    |because it ships with the means to prove itself, which is what
    |SpecEmission emitted and Proving runs.
    |
    |Every non-obvious choice is recorded in the decision log with its
    |reason. A generator that silently picks is one nobody can review.
  }
}
```

- [ ] **Step 3: Driver outlet, connector, validate, prettify, commit**

`type CodeEmissionCommand is one of { CodeEmission.EmitCode or
CodeEmission.DiscardCode }` for the saga. Expect `0 errors, 0 warnings`.

---

## Task 6: HoleFilling

A context of its own because holes arise in different places and at
different phases, and because filling one depends on a **local** slice of
context rather than the whole model (spec §4.7). `Hole` carries not just its
prompt but its fill context — the enclosing processor, the artifact's code
so far, and the declarations in scope. Assembling that slice is a modelled
responsibility, because the difference between a fill that works and one
that hallucinates is what got sent.

**Files:**
- Create: `tooling/code-generator/HoleFillingContext.riddl`
- Create: `tooling/code-generator/Hole.riddl`
- Modify: `GeneratorDriver.riddl`, `code-generator.riddl`

**Interfaces:**
- Consumes: `CodeEmission.ArtifactId`, `event CodeEmission.Artifact.ArtifactFilled` (Task 5).
- Produces: `entity HoleFilling.Hole`; `type HoleFilling.HoleId is Id(Hole)`
  at **context** scope beside the entity;
  `command HoleFilling.ReopenHoles`, which **Task 7's `Proving` context
  tells** to close the retry cycle.

- [ ] **Step 1: Write `Hole.riddl`**

Three states: **Open → Filled → Proven**. Commands `OpenHole`, `FillHole`,
`ProveHole`, `ReopenHole`, each yielding its event.

State record `HoleData`:
- `holeId: HoleId`
- `holeArtifactId: CodeEmission.ArtifactId`
- `holePrompt: String(1,4096)` — the `do`/`prompt` text the hole came from
- `enclosingProcessor: String(1,256)` — the fill context's first component
- `codeSoFar: String(1,65535)` — the artifact's code at the point of the
  hole
- `declarationsInScope: String(1,65535)` — what the AI may draw on
- `fillAttempts: Natural` — the retry cap's counter

**The attempt cap is an invariant, not a loop.** Declare on the `Open`
state:

```riddl
    invariant AttemptsBounded is "HoleData.fillAttempts <= 5" with {
      briefly "Fill attempts are capped"
      described as {
        |An unbounded fill-and-prove cycle against an AI backend is a
        |runaway. The cap is what makes the cycle terminate on failure; the
        |normal termination is the artifact's open hole count reaching zero.
      }
    }
```

and `require invariant AttemptsBounded` in the `on command FillHole` clause,
as `LoyaltyAccount`'s `SufficientBalance` does.

**Holes come only from prose the language deliberately leaves vague** — the
`do`/`prompt` statement, which grammar shows is a single production
(`prompt_statement = ("do" | "prompt") literal_string_block`). Conditions
and branching are **not** holes: 2.0 shipped typed holes, a closed boolean
expression grammar and structured match patterns, which moved that work into
the deterministic tier. State this in the entity's `described as`; a
generator still routing conditions through AI FILL is doing work the
language now does for it.

- [ ] **Step 2: Write `HoleFillingContext.riddl`**

Task 2's context shape, with a repository for `Hole` and a projector. Plus
the fill-context assembly function:

```riddl
  function AssembleFillContext is {
    requires record FillContextRequest
    returns record FillContext
    return prompt("the enclosing processor, the artifact's code so far, and the declarations in scope for this hole — not the whole model")
  } with {
    briefly "Assemble the local slice a hole is filled against"
    described as {
      |Filling depends on a lot of context but NOT the entire context of
      |the model being generated for. The local resources of the processor
      |being worked on, and the code written so far, are what the AI should
      |draw from. Sending more is not more accurate — it is what makes a
      |fill hallucinate.
    }
  }
```

Declare `record FillContextRequest` (fields `requestHoleId: HoleFilling.HoleId`,
`requestArtifactId: CodeEmission.ArtifactId`) and `record FillContext` (fields
`contextProcessor`, `contextCodeSoFar`, `contextDeclarations`).

- [ ] **Step 3: Driver outlet, connector, validate, prettify, commit**

`type HoleFillingCommand is one of { HoleFilling.FillHoles or
HoleFilling.ReopenHoles or HoleFilling.DiscardFills }`. Expect
`0 errors, 0 warnings`.

---

## Task 7: Proving, and the retry event cycle

Two gates, matching riddlg's: **pass-1** compiles, augments and boots,
behaviour not asserted; **pass-2** the generated suite goes green.

**There is no loop construct, and that is the correct shape.** Retry-until-
green is an **event cycle**: `Proving` emits `ProofFailed`, `HoleFilling`
reopens the named holes and refills. That is what a reactive system does
instead of looping. It terminates two ways — the artifact's open hole count
reaching zero, or `Hole`'s attempt cap (Task 6).

**Files:**
- Create: `tooling/code-generator/ProvingContext.riddl`
- Modify: `tooling/code-generator/HoleFillingContext.riddl` — Step 2 adds the
  proof-failure inlet, a boundary clause, and a re-derived shape ascription
- Modify: `GeneratorDriver.riddl`, `code-generator.riddl`

**Interfaces:**
- Consumes: `CodeEmission.ArtifactId` (Task 5); `command
  HoleFilling.ReopenHoles` (Task 6).
- Produces: `context Proving` with `type ProvingCommand is one of {
  Proving.RunBootGate or Proving.RunGreenGate }`; `event Proving.ProofFailed`
  and its outlet, which feeds `HoleFilling`.

- [ ] **Step 1: Write the context**

Stateless — the gates hold no identity — so no aggregate and no repository,
and therefore the **inlet-only** shape: no relay outlet, and a boundary
handler that does the work directly. `Proving` is nonetheless `as flow`, not
`as sink`, because it declares the `ProofFailures` outlet below — one inlet,
one outlet. See `docs/superpowers/reference/verified-stateless-context.riddl`.

Distinctive content:

- `command RunBootGate` — pass-1. Its `do` prose must say that it runs with
  tests skipped precisely because behaviour is not yet assertable.
- `command RunGreenGate` — pass-2. Fields `gateArtifactId:
  CodeEmission.ArtifactId` and `gateRunId:
  Intake.GenerationRunId`. `RunBootGate` carries the same
  two.
- `event ProofFailed` — fields `failedArtifactId: CodeEmission.ArtifactId`,
  `failureDetail: String(1,4096)`.
- `outlet ProofFailures is type ProofFailed`.
- The handler clause that publishes it:

```riddl
      on command RunGreenGate is {
        yield event ProofFailed(failedArtifactId = RunGreenGate.gateArtifactId, failureDetail = prompt("what the generated suite reported when it did not go green"))
      }
      on failureEvent: event ProofFailed is {
        send failureEvent to outlet Proving.ProofFailures
      }
```

- [ ] **Step 2: Close the cycle**

`HoleFilling` gains an inlet for proof failures, and the entry file gains
the cross-context connector — **persistent**, because it crosses a boundary:

```riddl
  persistent connector 'ProofFailure Feedback' is from outlet Proving.ProofFailures to inlet HoleFilling.ProofFailuresIn with {
    briefly "Failed proofs on their way back to hole filling"
    described as {
      |The retry cycle, closed. A failed proof re-enters hole filling rather
      |than spinning in a loop, which is what a reactive system does instead
      |of looping. It terminates when the artifact's open hole count reaches
      |zero, or when a hole hits its attempt cap.
    }
  }
```

`HoleFilling`'s boundary handler gains `on failureEvent: event
Proving.ProofFailed is { … }` telling `ReopenHoles`. Adding an inlet
changes `HoleFilling`'s arity, so **re-derive its shape ascription** — run
`riddlc --provide-tips validate` and take the suggestion rather than
guessing.

- [ ] **Step 3: Validate, prettify, commit**

Expect `0 errors, 0 warnings`. If a shape ascription now contradicts the
arity that is a hard **error**, and the tip names the correct one.

---
## Task 8: The GenerationPipeline saga

Declared at **domain** level, with every step telling a command **to a
context**. This is the payoff of the whole structure: each message-driven
context now has a declared API — a command alternation, an inlet, an outlet
and a boundary handler — and the saga is written against those APIs. A
generator builder reading the model sees six named service surfaces and the
orchestration over them.

**Six, not seven:** `Naming` is reached by function call, declares no ports,
and the saga never addresses it.

**Files:**
- Modify: `tooling/code-generator/code-generator.riddl` — add the saga

**Interfaces:**
- Consumes: the command alternation of each of the six message-driven
  contexts (Tasks 2–7).
- Produces: nothing later tasks consume.

- [ ] **Step 1: Write the saga into the entry file**

Six steps, one per message-driven context, each with a compensation. The
form, per step:

```riddl
  saga GenerationPipeline is {
    step StepAdmitModel is {
      do "Load the model and apply the generability bar"
      let admitModel: type Intake.GenerationRun.AdmitModel = prompt("the admit model command for this run")
      tell admitModel to context Intake
    }
    reverted by {
      do "Refuse the model, which is the only way back from admission"
      let refuseModel: type Intake.GenerationRun.RefuseModel = prompt("the refuse model command for this run")
      tell refuseModel to context Intake
    } with {
      briefly "Admit the model"
      described as {
        |The bar is operational, not advisory: a model with any warning
        |other than Style is refused, because code cannot be generated from
        |unstated intent. Compensating means refusing outright — there is
        |no state between admitted and never-started.
      }
    }
```

Then, in order: `StepPlan` → `context Planning`, `StepEmitSpecs` →
`context SpecEmission`, `StepEmitCode` → `context CodeEmission`,
`StepFillHoles` → `context HoleFilling`, `StepProve` → `context Proving`.
Each `reverted by` tells that context's `Discard…` command.

Close with the mandatory timeout and the ruling that shaped it:

```riddl
  } with {
    option timeout("PT30M")
    briefly "The generation pipeline"
    described as {
      |Orchestrates the six message-driven contexts, addressing each context
      |rather than reaching into it. Reaching past a context into one of its
      |entities, streamlets or repositories is an encapsulation violation:
      |the sender binds itself to the context's internal design, which is
      |what the context exists to prevent.
      |
      |riddlc does not yet enforce this — both forms validate identically —
      |so the rule is adopted here ahead of the check. Filed upstream as
      |2026-08-26-saga-tell-must-not-reach-into-a-context.
    }
  }
```

- [ ] **Step 2: Validate — the reachability check**

```bash
RIDDLC=~/.cache/riddlc/2.0.0-rc.26/bin/riddlc
$RIDDLC --no-ansi-messages validate tooling/code-generator/code-generator.riddl 2>&1 | tail -30
```

Expected `0 errors, 0 warnings  [style, usage, missing, completeness on]`.

**A `msg-tell-target-unreachable` here means a context is missing its
driver connector.** Every context the saga addresses needs a persistent
connector from a `GeneratorDriver` outlet to its inlet — Tasks 2–7 each add
one, and this is the task where a missed one surfaces. A `tell` does not
itself count for reachability.

`saga-too-few-steps` or `saga-step-names-not-distinct` mean a step is
malformed; both fire against the saga's own line, not the step's.

- [ ] **Step 3: Confirm the encapsulation criterion**

```bash
grep -n "tell .* to entity\|tell .* to repository\|tell .* to streamlet" tooling/code-generator/code-generator.riddl
```

Expected: **no output**. Spec criterion 6 — no saga step names any
definition inside a context. (A `tell … to repository` inside a *projector*
is correct and expected; this grep is scoped to the entry file, which holds
only the saga.)

- [ ] **Step 4: Prettify, `sbt v && sbt pc`, commit**

---

## Task 9: Fill the lowering catalogue to full coverage

The bulk of the content, deferred to here so the structure was proven first.
Spec criterion 7: **every RIDDL definition kind a generator must lower has a
`LoweringRule` for each paradigm it can land on, and every lowering function
consults one.**

**Files:**
- Modify: `tooling/code-generator/PlanningContext.riddl`

**Interfaces:**
- Consumes: `type DefinitionKind`, `type Paradigm`, `type Capability`,
  `repository Planning.LoweringCatalogue`, `repository
  Planning.TargetProfiles` (Task 3).
- Produces: nothing new — this task adds rows, not definitions.

- [ ] **Step 1: Enumerate the rules**

The catalogue is data, held as the `do` prose of the
`PersistLoweringRule` handler and as the rules the `described as` on
`LoweringCatalogue` enumerates. One rule per `(DefinitionKind, Paradigm)`
pair that can actually occur — not the full cross product, since a
`TypeKind` does not land on an `Actor`.

Work from the CM, one kind at a time, recording for each:
- the **capability** the construct requires
- the **artifact** it plans
- the **guarantee** that must survive lowering

The three rules that are genuine **two-outcome decisions** (spec §2.2)
become `invariant`s on `LoweringCatalogue` rather than prose, because a
generated invariant check is real code. The first of them, and the one
riddlg currently gets wrong:

```riddl
    invariant CrossContextConnectorIsPersistent is "StoredLoweringRule.ruleDefinitionKind == ConnectorKind implies StoredLoweringRule.requiredCapability == DurableJournal" with {
      briefly "A cross-context connector lowers to a persistent channel"
      described as {
        |Durability across a context boundary can be required for model
        |correctness, not merely a deployment concern. riddlg currently
        |defaults this the other way — riddl-generator BACKLOG item 6 — so
        |it is stated as an invariant rather than as prose.
      }
    }
```

- [ ] **Step 2: Add at least two TargetProfile rows**

Spec criterion 8: one actor-tier and one bean-tier, **so the paradigm
indirection is exercised rather than asserted**. Pekko/Scala selects
`Actor` for `EntityKind` and owes nothing; Quarkus/Java selects `Component`
and owes `SerialExecution`, `ChannelInteraction` and `DurableJournal`.

Record both in the `PersistTargetProfile` handler's `do` prose and in the
repository's `described as`. TypeScript/Effect is worth adding as a third:
it selects `Actor` via `@effect/cluster` and owes `DurableJournal`, which is
the case that proves owing a capability does not disqualify a target — the
generator emits the journal.

- [ ] **Step 3: Validate — watch the usage class**

Expect `0 errors, 0 warnings`. A `use-unused-definition` naming a rule
means nothing consults it, which is exactly the self-enforcement the
catalogue is built for (spec §4.5). Fix the consultation; do not delete the
rule and do not suppress the class.

- [ ] **Step 4: Prettify, `sbt v && sbt pc`, commit**

---

## Task 10: The model README

**Files:**
- Create: `tooling/code-generator/README.md`

- [ ] **Step 1: Write it for a generator builder**

Spec criterion 12. Its reader is someone building a *new* generator, so it
explains what each context is for and what each stage owes — not what
riddlg-the-product does. Sections:

1. What this model is, and the dogfooding claim: if RIDDL cannot express
   the design of a RIDDL code generator, that is a finding about RIDDL.
2. The seven contexts, one paragraph each, in pipeline order.
3. **The precedence of representations** — actor, bean, object, and why the
   actor is first: a RIDDL processor already is one.
4. How to add a target: write a `TargetProfile`, not a model.
5. What is deliberately absent: riddlg's product surface, per-target
   models, a generated-source domain.

**No `## NAICS Code` section** — Reid's ruling of 2026-08-26. Every other
model README carries one; this is a recorded exception for `tooling/`,
whose models describe our own toolchain and have no industry
classification. Task 11 records the exception in `CLAUDE.md` so the
omission does not read as an oversight.

80-column limit.

- [ ] **Step 2: Commit**

---

## Task 11: Census and convention edits

Spec criteria 9 and 10.

**Files:**
- Modify: `CLAUDE.md` — three edits
- Modify: `README.md` — one edit, one optional

- [ ] **Step 1: `CLAUDE.md` line 66 — 18 sectors becomes 19**

```
The repository organizes models into **18 top-level sectors** covering
```
becomes `**19 top-level sectors**`.

- [ ] **Step 2: `CLAUDE.md` sector table — add the `tooling` row**

After the `professional-services` row (line 93):

```markdown
| `tooling` | Our Own Toolchain | code-generation |
```

- [ ] **Step 3: `CLAUDE.md` NAICS paragraph — record the exception**

The paragraph at line 114 (`### NAICS Codes in READMEs`) gains:

```markdown
**Exception — `tooling/`.** Models under `tooling/` carry **no** NAICS
code. They describe our own toolchain rather than an industry, so there is
no classification to give. Reid's ruling, 2026-08-26.
```

- [ ] **Step 4: `README.md` repository tree — add `tooling/`**

The tree at lines 16–27ff lists sectors. Add, in the same alignment:

```
├── tooling/            # Our own toolchain (code generation)
```

README carries a **directory tree, not a sector table** — checked
2026-08-26, so there is no second place to edit.

- [ ] **Step 5 (optional, flag to Reid): `README.md` line 41**

It reads `All 187 models are classified by`. The corpus is at 190 before
this work and 191 after. **This is a pre-existing inaccuracy, not caused by
this plan** — fix it to 191 only if Reid wants the drift closed in this
commit; otherwise leave it and note it in `BACKLOG.md`.

- [ ] **Step 6: Commit**

Documentation only — a separate commit from the model.

---

## Task 12: Apply Appendix A to the Computational Model

Spec criterion 11. Reid approved the design **including Appendix A's
changes to the CM**, 2026-08-26.

**Files:**
- Modify: `../RIDDL-Computational-Model.md` — replace one paragraph

**This file lives at `ossuminc/` level, above every project.** It is a
cross-repository artifact and is not in this repository's git history —
commit it from the `ossuminc/` directory, separately.

- [ ] **Step 1: Locate the paragraph**

`../RIDDL-Computational-Model.md` line 1036, in `### **4.1 Conceptual
meaning**`. It begins `**Implementation reality:** some computing systems do
not support Actors.` It is **one paragraph**; the preceding paragraph (the
DDD/Akka mental model) is untouched.

```bash
sed -n '1030,1040p' ../RIDDL-Computational-Model.md
```

- [ ] **Step 2: Replace it with Appendix A's text**

The replacement is in the spec's **Appendix A**, between the `---` and the
end of the appendix. It keeps everything the original said — actors where a
library supplies them, an Actor facade where not, mailbox order and no
concurrent processing per identity — and adds the precedence table, the
admission test, the two exclusions and the runtime tenets.

Copy it verbatim from the spec. Do not paraphrase: it was reviewed and
approved as written.

- [ ] **Step 3: Verify the surrounding structure survived**

```bash
grep -n '^### \*\*4\.' ../RIDDL-Computational-Model.md
```

Expected: `4.1` through `4.8` all still present, in order. The CM's headings
carry `{#anchors}` used by its table of contents — confirm 4.2's anchor line
is intact and that no heading was absorbed into the replaced paragraph.

- [ ] **Step 4: Commit from `ossuminc/`**

Message via file. This is a different repository's working tree — confirm
with `git -C .. status --short` that only the CM changed.

---

## Task 13: BAST, final gates, and the notebook

**Files:**
- Create: `tooling/code-generator/code-generator.bast` (generated)
- Modify: `NOTEBOOK.md`, `BACKLOG.md`, `CLAUDE.md` (Step 5)

- [ ] **Step 1: Generate the `.bast`**

```bash
sbt b
ls -la tooling/code-generator/code-generator.bast
```

`sbt b` regenerates every model's `.bast`. **Check `git status` afterwards:
if other models' `.bast` files changed, they were already stale** — that is
a separate finding and a separate commit, not something to fold in here.

- [ ] **Step 2: Round-trip verification**

```bash
./scripts/verify-bast-roundtrip.sh
```

All 191 must pass. This diffs the unbastified tree against the source
**byte for byte**, so it only holds while the corpus is exactly what
prettify emits. **A failure naming the `.bast` usually means the source
drifted from canonical** — re-run `sbt r` and diff, rather than relaxing the
script.

Never run `riddlc unbastify <f>.bast` without `-o`: it overwrites the
sources beside it, and nothing warns.

- [ ] **Step 3: The full gate set**

```bash
RIDDLC=~/.cache/riddlc/2.0.0-rc.26/bin/riddlc
$RIDDLC info                                   # must report 2.0.0-rc.26
$RIDDLC validate --corpus . 2>&1 | tail -3     # 191 models, 0 failed, 191 ok
RIDDLC=$RIDDLC ./scripts/collect-warnings.py   # 0 findings, 191 swept
sbt v
sbt pc
sbt checkAll
```

**Canary `collect-warnings.py` before believing its zero.** Inject one
unused type into the new model, confirm the sweep reports it, revert. A
zero from a harness that cannot see is the failure this repository keeps
re-learning — and check the **denominator** too: the script prints nothing
at all on an empty run, so "0 findings" and "swept 0 models" look alike.

Confirm the sweep count moved 188 → 189 (it counts models with a `.conf`
outside `patterns/`; `--corpus` counts differently, hence 191).

- [ ] **Step 4: Update `NOTEBOOK.md` and `BACKLOG.md`**

- `NOTEBOOK.md` § HANDOFF: replace the "Reid owes a review" block — that
  question is answered. Record the new corpus census, the verified skeleton
  file and what it proves, and the one trap this work found: **a context a
  saga addresses needs a driver connector, because `tell` does not count for
  reachability.**
- `NOTEBOOK.md` body: what this taught. The graduation pattern — durable
  facts to `CLAUDE.md`, lessons here.
- `BACKLOG.md`: remove item #0 (the in-flight project). Add the
  `code_statement`-has-no-TypeScript task if it has not been filed
  upstream yet, and the README-187 drift if Task 11 Step 5 was deferred.

- [ ] **Step 5: Graduate durable facts to `CLAUDE.md`**

Two are durable and belong in `CLAUDE.md`, not just the notebook:

1. **The driver-connector rule** — a context a saga addresses needs an
   inbound connector to one of its inlets; `tell` does not count for
   reachability. This is general to the corpus, not specific to this model.
2. **The `.conf` lever** — a `.conf` carrying only `input-file` makes
   `sbt v` enforce every severity for that model. `CLAUDE.md` already says
   `language-coverage.conf` is the lone example; it now has a second, and
   the technique is worth stating as a choice rather than an accident.

- [ ] **Step 6: Final commit and push**

```bash
git status --short
git add -A
git commit -F /tmp/commit-msg.txt
git log -1 --format=%B
```

---

## Self-review notes

**Spec coverage.** Every acceptance criterion maps to a task: 1 → T1,
2 → T1/T13, 3 → every task's gate and T13, 4 → T13, 5 → T13, 6 → T8 Step 3,
7 → T9, 8 → T9 Step 2, 9 → T11, 10 → T11 Step 3, 11 → T12, 12 → T10. Every
architecture section §4.1–4.8 maps to T2–T8.

**Two ordering constraints are forced, not chosen.**
`Naming` ships with `Planning` (T3) because a function nothing calls is a
usage finding. The lowering catalogue's content (T9) comes after the saga
(T8) because the saga's reachability check is the cheaper failure to
diagnose, and catching a missing driver connector before adding forty rules
is worth the reordering.

**Known risk carried from the spec.** This is a large model, comparable to
reactive-bbq. Criterion 3 is a bar to converge on within each task, not a
first-run expectation. If the retry cycle (T7) proves clumsy to express
without a loop construct, that is the dogfooding finding the model exists to
produce — file it upstream rather than working around it.
