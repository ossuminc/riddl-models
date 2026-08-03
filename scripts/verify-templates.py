#!/usr/bin/env python3
"""Verify that every pattern template still parses and validates.

The seven `patterns/**/template.riddl` files are parameterised: they carry
`{Placeholder}` names, and they are FRAGMENTS -- they begin at `entity`,
`repository`, `projector`, `saga` or `context`, not at `domain`. Neither
property survives riddlc on its own, so the templates were never checked by
anything, and they rotted through the whole RIDDL 2.0 migration while the 187
models were kept green.

This closes that hole. For each template it:

  1. substitutes the placeholders with the values below,
  2. wraps the fragment in the smallest scaffold that makes it a whole model --
     a domain, a context where the fragment needs one, plus the few definitions
     a real instantiation would supply (the entity a repository persists, the
     events a process manager reacts to),
  3. writes the result beside a generated `.conf` and runs riddlc.

The substitutions are deliberately ordinary -- Order, Cart, Item -- so a
failure reads as a defect in the template rather than an artifact of an exotic
name. The scaffold is kept minimal for the same reason: everything it adds is
something the template genuinely depends on and does not declare.

Two tiers. **Parsing is the gate** and all seven pass it. It is what these files actually failed -- they had
drifted to pre-2.0 syntax (`option event-sourced`, `briefly` outside a `with`
block, `state X is { fields }`, comma-separated fields) while every model in
the corpus was kept current. Full validation is available with `--validate`,
but it is not the bar: making a bare fragment validate as a whole model needs
a scaffold so large -- a sink, a repository, a source, and the connectors
between them -- that the exercise starts testing the scaffold instead of the
template. `--validate` therefore classifies its findings: anything naming a
scaffold definition is reported as scaffold-level and ignored, so what remains
is about the template itself. Some of those are inherent to being a fragment --
an entity template cannot declare its Id type in "the containing context" when
it has no context, and it cannot connect its own outlet -- so `--validate` is a
source of suggestions, not a gate.

Adding a new `{Placeholder}` to a template without adding it to TEMPLATES below
fails loudly rather than substituting nothing. That is the point: these files
are meant to be maintained, and this is what notices when they are not.

Usage:
    scripts/verify-templates.py               # parse all (the gate)
    scripts/verify-templates.py --validate    # also validate as whole models
    scripts/verify-templates.py --keep        # leave the generated models
    RIDDLC=/path/to/riddlc scripts/verify-templates.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RIDDLC = os.environ.get("RIDDLC", os.path.join(os.path.dirname(ROOT), "bin", "riddlc"))

CONF = """common {
  show-style-warnings   = false
  show-missing-warnings = true
  show-usage-warnings   = false
  no-ansi-messages = true
}

validate {
  input-file = "model.riddl"
}
"""

# An error sink is required of every leaf domain, so the scaffold carries one.
# It is not part of any pattern; it is the cost of being a whole model.
DOMAIN_OPEN = """domain PatternCheck is {
  author Scaffold is {
    name = "Ossum Inc."
    email = "info@ossuminc.com"
  } with {
    briefly "Author of the scaffold"
    described as {
      |Ossum Inc., who maintain these patterns.
    }
  }
  application context PatternCheckApp is {
    inlet ErrorSink is record Riddl.GeneratorError with {
      option error-sink()
      briefly "Hard error destination"
      described as {
        |Where hard errors raised while checking a pattern template go.
      }
    }
  } with {
    briefly "Scaffold application"
    described as {
      |Exists only to host the error sink the domain check requires.
    }
  }
  connector ErrorsToSink is from outlet Riddl.ForeverEmpty.void to inlet PatternCheckApp.ErrorSink with {
    briefly "Hard errors to the domain error sink"
    described as {
      |No modelled component emits a GeneratorError; generators do, at run time.
    }
  }
"""

DOMAIN_CLOSE = """} with {
  briefly "Pattern template check"
  described as {
    |A scaffold domain that exists only so a pattern template can be
    |parsed and validated as part of a whole model.
  }
}
"""


def context(name, body, prelude=""):
    """Wrap a fragment in a context inside the scaffold domain."""
    return (DOMAIN_OPEN
            + f"  context {name} is {{\n"
            + prelude
            + indent(body, 2)
            + f"\n  }} with {{\n    briefly \"Scaffold context\"\n"
            + "    described as {\n      |Hosts the pattern template under test.\n    }\n  }\n"
            + DOMAIN_CLOSE)


def bare(body, prelude=""):
    """Wrap a fragment that is itself a context directly in the domain."""
    return DOMAIN_OPEN + prelude + indent(body, 2) + "\n" + DOMAIN_CLOSE


def indent(text, n):
    pad = " " * n
    return "\n".join(pad + line if line.strip() else line for line in text.split("\n"))


# What a real instantiation would supply around each fragment. Every entry here
# is a dependency the template references but does not declare -- keep it that
# way, so the scaffold never hides a defect in the template itself.
# Events a projector or process manager reacts to, which a real instantiation
# would get from the entity it follows.
ORDER_EVENTS = """    type {EntityName}Event is one of {
      {EntityName}Created or {EntityName}Updated or {EntityName}Deleted
    } with {
      briefly "Source entity event alternation"
      described as {
        |What the source entity publishes.
      }
    }
    processor {EntityName}EventSource as source is {
      outlet {EntityName}Events is type {EntityName}Event
      handler {EntityName}EventEmitter is {
        on other is {
          send event {EntityName}Created to outlet {EntityName}Events
        }
      } with {
        briefly "Scaffold event source"
        described as {
          |Stands in for whatever publishes the source entity's events.
        }
      }
    } with {
      briefly "Scaffold source"
      described as {
        |Gives the repository an upstream, which A6 reachability requires.
      }
    }
    connector {EntityName}EventsToStore is from outlet {EntityName}EventSource.{EntityName}Events to inlet {ViewName}Store.Incoming{EntityName}Events with {
      briefly "Events to the projection store"
      described as {
        |Instantiation wiring, not part of the pattern.
      }
    }
    repository {ViewName}Store is {
      inlet Incoming{EntityName}Events is type {EntityName}Event
      record Stored{ViewName} is {
        orderId: String with {
          briefly "Key"
          described as {
            |The key of the stored view row.
          }
        }
      } with {
        briefly "Stored view row"
        described as {
          |The persistence shape of the read model.
        }
      }
      schema {ViewName}Data is relational
        of rows as type Stored{ViewName}
          index on field Stored{ViewName}.orderId
        with {
        briefly "View data schema"
        described as {
          |Where the projection is kept.
        }
      }
      command Persist{ViewName} is {
        orderId: String with {
          briefly "Key"
          described as {
            |The row to write.
          }
        }
      } with {
        briefly "Persist a view row"
        described as {
          |A persistence command; it declares no `yields`.
        }
      }
      handler {ViewName}Persistence is {
        on command Persist{ViewName} is {
          set field Stored{ViewName}.orderId to "the key from the view row"
        }
      } with {
        briefly "View persistence"
        described as {
          |Stores projected rows.
        }
      }
    } with {
      briefly "{ViewName} store"
      described as {
        |Holds the projection this pattern maintains.
      }
    }
    event {EntityName}Created is {
      orderId: String with {
        briefly "Key"
        described as {
          |Identifies the order.
        }
      }
    } with {
      briefly "An order was created"
      described as {
        |Scaffold event standing in for the source entity's own.
      }
    }
    event {EntityName}Updated is {
      orderId: String with {
        briefly "Key"
        described as {
          |Identifies the order.
        }
      }
    } with {
      briefly "An order was updated"
      described as {
        |Scaffold event standing in for the source entity's own.
      }
    }
    event {EntityName}Deleted is {
      orderId: String with {
        briefly "Key"
        described as {
          |Identifies the order.
        }
      }
    } with {
      briefly "An order was deleted"
      described as {
        |Scaffold event standing in for the source entity's own.
      }
    }
"""

TEMPLATES = {
    "patterns/entity/event-sourced/template.riddl": {
        "subs": {"EntityName": "Order"},
        "wrap": "Sales",
    },
    "patterns/entity/aggregate-root/template.riddl": {
        "subs": {"AggregateName": "Cart", "ChildName": "Item"},
        "wrap": "Shopping",
    },
    "patterns/entity/repository/template.riddl": {
        "subs": {"RepositoryName": "OrderRepository", "EntityName": "Order"},
        "wrap": "Sales",
    },
    "patterns/gateway/api-gateway/template.riddl": {
        "subs": {"GatewayName": "Public"},
        "wrap": "bare",
    },
    "patterns/projection/read-model/template.riddl": {
        "subs": {"ProjectorName": "OrderSummaryView", "ViewName": "OrderSummary",
                 "EntityName": "Order"},
        "wrap": "Reporting",
        "prelude": ORDER_EVENTS,
    },
    "patterns/saga/distributed-transaction/template.riddl": {
        "subs": {"SagaName": "OrderFulfillment"},
        "wrap": "Fulfillment",
    },
    "patterns/workflow/process-manager/template.riddl": {
        "subs": {"ProcessName": "OrderFulfillment"},
        "wrap": "Fulfillment",
    },
}


def substitute(text, subs):
    def repl(m):
        name = m.group(1)
        if name not in subs:
            raise KeyError(f"no substitution for {{{name}}}")
        return subs[name]
    return re.sub(r"\{([A-Za-z][A-Za-z0-9]*)\}", repl, text)


def build(path, spec):
    src = open(os.path.join(ROOT, path)).read()
    body = substitute(src, spec["subs"])
    prelude = substitute(spec.get("prelude", ""), spec["subs"])
    if spec["wrap"] == "bare":
        return bare(body, prelude)
    return context(spec["wrap"], body, prelude)


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    out = re.sub(r"\x1b\[[0-9;]*m", "", p.stdout + p.stderr)
    return p.returncode, out


def main():
    parse_only = "--validate" not in sys.argv
    keep = "--keep" in sys.argv
    if not os.access(RIDDLC, os.X_OK):
        print(f"riddlc not found at {RIDDLC} (set RIDDLC=/path/to/riddlc)", file=sys.stderr)
        return 2

    tmp = tempfile.mkdtemp(prefix="riddl-templates-")
    failures = 0
    for path, spec in sorted(TEMPLATES.items()):
        name = path.split("/")[-2]
        d = os.path.join(tmp, name)
        os.makedirs(d, exist_ok=True)
        try:
            model = build(path, spec)
        except KeyError as e:
            print(f"FAIL  {path}  ({e})")
            failures += 1
            continue
        open(os.path.join(d, "model.riddl"), "w").write(model)
        open(os.path.join(d, "model.conf"), "w").write(CONF)

        rc, out = run([RIDDLC, "parse", "model.riddl"], d)
        findings = [l for l in out.split("\n") if re.match(r"^\[", l)]
        if rc != 0 or findings:
            print(f"FAIL  {path}  (parse)")
            for l in out.split("\n")[:6]:
                if l.strip():
                    print(f"        {l}")
            failures += 1
            continue
        if parse_only:
            print(f"ok    {path}  (parse)")
            continue

        rc, out = run([RIDDLC, "from", "model.conf", "validate"], d)
        # A finding that names a scaffold definition is about the wrapper, not
        # the template. `Context 'Sales' has entities but no Sink streamlet` is
        # true of the context this harness generated, and satisfying it would
        # mean building a sink, a repository and the connectors between them --
        # testing the scaffold instead of the pattern. Report those separately.
        scaffold = {"PatternCheck", "PatternCheckApp", "Scaffold", "ErrorSink",
                    "ErrorsToSink", spec["wrap"]}
        findings, scaffold_only = [], []
        lines = out.split("\n")
        for i, line in enumerate(lines):
            if not re.match(r"^\[", line):
                continue
            # riddlc puts the location on one line and the message on the next
            message = lines[i + 1] if i + 1 < len(lines) else ""
            named = set(re.findall(r"'([^']+)'", message))
            entry = f"{line} {message.strip()}"
            (scaffold_only if named & scaffold else findings).append(entry)
        if rc != 0 or findings:
            print(f"FAIL  {path}  (validate)")
            for l in findings[:6]:
                print(f"        {l}")
            failures += 1
            continue
        if scaffold_only:
            print(f"ok    {path}  ({len(scaffold_only)} scaffold-level finding(s) ignored)")
        else:
            print(f"ok    {path}")

    print()
    print(f"templates passing : {len(TEMPLATES) - failures}")
    print(f"templates failing : {failures}")
    if keep:
        print(f"generated models  : {tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return 1 if failures else 0


sys.exit(main())
