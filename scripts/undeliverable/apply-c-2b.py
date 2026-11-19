#!/usr/bin/env python3
"""BACKLOG #43 step 3 (c), group 2b: 25 commands first filed as "no adaptor
receives them". Re-read with sink adaptors in view (the reviewers' briefs
left sinks out), they split three ways, each applied under Reid's ruling of
2026-11-19:

  * B_SITES (5): a sink adaptor already receives the trigger -- rule (b).
    The sink gains an outlet (an `<Adaptor>Command` alternation when it
    carries more than one), an intake inlet and connector on its context,
    and sends from the clause.
  * A2_SITES (3): the system is wired in but never publishes the trigger --
    group 2a's treatment, run by apply-c-2a.py's `run`.
  * NEW_SOURCES (17 sites, 7 systems): the source is not in the model.
    Option A with Reid's rider, fewest external contexts: ONE new
    `external context <X> as source` per model, publishing every event its
    commands need (carrying exactly the command's fields) on an `<X>Event`
    alternation; a domain connector to a new inbound adaptor `From<X>`,
    which sends each command field for field into its context's intake.

Edits are exact-text and must match once, or nothing is written.
Re-ascribe afterwards (`scripts/reascribe.py`).

Usage:  apply-c-2b.py [--apply]
"""
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("c2a", HERE / "apply-c-2a.py")
c2a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c2a)
ROOT, Files, dump, body_of, lc = c2a.ROOT, c2a.Files, c2a.dump, c2a.body_of, c2a.lc

# model, adaptor, [(event clause head, command rel path, why, guard or None)]
B_SITES = [
    ("commerce/retail/inventory-management", "OrderAdapter", [
        ("on event OrderService.OrderPlaced is {", "StockItem.ReserveStock",
         "the reservation the placed order's items need", None),
        ("on event OrderService.OrderCancelled is {", "StockItem.ReleaseReservation",
         "the reservation the cancelled order releases", None),
        ("on event OrderService.OrderFulfilled is {", "StockItem.DeductStock",
         "the stock the fulfilled order took", None),
    ]),
    ("telecommunications/billing/usage-rating", "FromNetworkMediationSystem", [
        ("on callDetailRecordReceived: event NetworkMediationSystem.CallDetailRecordReceived is {",
         "SubmitUsageRecord", "the usage record this call detail record is", None),
    ]),
    ("technology/saas/usage-metering", "FromEventIngestionService", [
        ("on rawUsageReceived: event EventIngestionService.RawUsageReceived is {",
         "Meter.RecordBatchEvents", "the batch of usage events attributed to the meter",
         "the raw usage has been attributed to a meter"),
    ]),
]

A2_SITES = [
    ("natural-resources/oil-gas/pipeline-operations", "SCADASystem", "FlowReadingReported",
     "on command SendControlSignal is {", "the segment's sensors report the resulting flow",
     "FromSCADASystem", "PipelineSegment.RecordFlowReading", "Flow reading reported"),
    ("marketing/analytics/attribution", "WebAnalytics", "FirstTouchTracked",
     "on command TrackEvent is {", "the tracked event is a visitor's first touch",
     "FromWebAnalytics", "CreateConversionPath", "First touch tracked"),
    ("marketing/analytics/attribution", "WebAnalytics", "ConversionTracked",
     "on command TrackEvent is {", "the tracked event is a conversion",
     "FromWebAnalytics", "ConversionPath.RecordConversion", "Conversion tracked"),
]

# model, context, external, its brief, its description, [(event, command rel path, event brief)]
NEW_SOURCES = [
    ("entertainment/media/advertising-delivery", "AdContext", "VideoPlayer", "Video player",
     "The player that renders ads and fires their tracking beacons.", [
        ("AdRequested", "AdImpression.OpenImpressionOpportunity", "Ad requested"),
        ("StartBeaconFired", "AdImpression.RecordStart", "Start beacon fired"),
        ("QuartileBeaconFired", "AdImpression.RecordQuartile", "Quartile beacon fired"),
        ("CompleteBeaconFired", "AdImpression.RecordComplete", "Complete beacon fired"),
        ("SkipBeaconFired", "AdImpression.RecordSkip", "Skip beacon fired"),
        ("ClickBeaconFired", "AdImpression.RecordClick", "Click beacon fired"),
        ("ErrorBeaconFired", "AdImpression.RecordError", "Error beacon fired"),
    ]),
    ("entertainment/media/streaming-platform", "StreamContext", "VideoPlayer", "Video player",
     "The viewer's player, which reports playback errors and metrics.", [
        ("PlaybackErrored", "Stream.ReportError", "Playback errored"),
        ("PlaybackMetricsReported", "Stream.ReportMetrics", "Playback metrics reported"),
    ]),
    ("marketing/advertising/ad-serving", "AdContext", "ClickTracker", "Click tracker",
     "The redirect that records a viewer's click on an ad.", [
        ("AdClicked", "Advertisement.RecordClick", "Ad clicked"),
    ]),
    ("entertainment/gaming/matchmaking", "MatchContext", "GameServer", "Game server",
     "The server that hosts a match and reports how it goes.", [
        ("GameStarted", "Match.StartMatch", "Game started"),
        ("ScoreReported", "Match.UpdateScore", "Score reported"),
        ("GameEnded", "Match.EndMatch", "Game ended"),
    ]),
    ("utilities/water/water-distribution", "WaterContext", "SCADASystem", "SCADA system",
     "The supervisory control system whose sensors read the network.", [
        ("PressureMeasured", "DistributionZone.RecordPressure", "Pressure measured"),
        ("ReservoirLevelMeasured", "DistributionZone.UpdateReservoirLevel", "Reservoir level measured"),
    ]),
    ("transportation/passenger/transit-operations", "VehicleContext", "PassengerCounter",
     "Passenger counter", "The automatic counters that count riders boarding and alighting.", [
        ("PassengerCountReported", "Vehicle.UpdatePassengerLoad", "Passenger count reported"),
    ]),
    ("technology/saas/multi-tenant", "TenantContext", "UsageCollector", "Usage collector",
     "The platform agent that meters what each tenant uses.", [
        ("UsageCollected", "Tenant.RecordUsage", "Usage collected"),
    ]),
]


def command_of(nodes, kids, cmdrel):
    c = [n for n in nodes if n["kind"] == "command" and n["path"].endswith("." + cmdrel)]
    assert len(c) == 1, (cmdrel, len(c))
    return c[0], [f["id"] for f in kids[c[0]["path"]] if f["kind"] == "field"]


def source_of(F, node):
    src = F.get(node["file"])
    off = sum(len(l) + 1 for l in src.split("\n")[:node["span"]["start"]["line"] - 1])
    return body_of(src[off:])


def alt(name, members, brief):
    return (f"  type {name} is one of {{\n    {' or '.join(members)}\n  }} with {{\n"
            f"    briefly \"{brief}\"\n  }}\n")


def intake(ctx, adaptor, outlet, iname, cmdtype):
    return (f"  inlet {iname} is {cmdtype} with {{\n"
            f"    briefly \"What {adaptor} makes of that service's news\"\n  }}\n"
            f"  connector '{adaptor} Intake' is from outlet {ctx}.{adaptor}.{outlet} to inlet {ctx}.{iname} with {{\n"
            f"    briefly \"What {adaptor} makes of that news, on its way in\"\n  }}\n")


def b_sites(pending):
    n = 0
    for model, adaptor, clauses in B_SITES:
        md = ROOT / model
        nodes = dump(md)
        byp = {x["path"]: x for x in nodes if "path" in x}
        ad = [x for x in nodes if x["kind"] == "adaptor" and x["id"] == adaptor]
        assert len(ad) == 1
        ad = ad[0]
        ctx = byp[ad["parent"]]["id"]
        F = Files(md)
        f = ad["file"]
        ahead = f"  adaptor {adaptor} from context "
        inl = [p for p in nodes if p.get("parent") == ad["path"] and p["kind"] == "inlet"]
        assert len(inl) == 1 and not [p for p in nodes if p.get("parent") == ad["path"] and p["kind"] == "outlet"]
        out = f"{adaptor}To{ctx}"
        iname = f"{ctx}From{adaptor.removeprefix('From')}"
        cmds = [c for _, c, _, _ in clauses]
        if len(cmds) > 1:
            ty = f"type {ctx}.{adaptor}Command"
            pre = alt(f"{adaptor}Command", cmds, f"What {adaptor} turns that service's news into")
        else:
            ty, pre = f"command {cmds[0]}", ""
        F.after(f, f"    inlet {inl[0]['id']} is ", ahead, f"    outlet {out} is {ty}\n")
        F.before(f, ahead.strip(), ahead, pre + intake(ctx, adaptor, out, iname, ty))
        for head, cmd, why, guard in clauses:
            b = lc(cmd.split(".")[-1])
            body = [f"let {b}: type {cmd} = prompt(\"{why}\")", f"send {b} to outlet {ctx}.{adaptor}.{out}"]
            if guard:
                body = [f"when prompt(\"{guard}\") then"] + ["  " + x for x in body] + ["end"]
            F.end_of_clause(f, head, ahead, "".join("        " + x + "\n" for x in body))
            n += 1
        pending.append(F)
    return n


def new_sources(pending):
    n = 0
    for model, ctx, ext, ebrief, edesc, events in NEW_SOURCES:
        md = ROOT / model
        nodes = dump(md)
        kids = defaultdict(list)
        for x in nodes:
            kids[x.get("parent")].append(x)
        F = Files(md)
        ctxn = [x for x in nodes if x["kind"] == "context" and x["id"] == ctx]
        assert len(ctxn) == 1
        cf = ctxn[0]["file"]
        adaptor, out, iname = f"From{ext}", f"From{ext}To{ctx}", f"{ctx}From{ext}"
        ev_defs, clauses, cmds = [], [], []
        for ev, cmdrel, brief in events:
            cmd, fields = command_of(nodes, kids, cmdrel)
            body = source_of(F, cmd).replace("\n  ", "\n")
            ev_defs.append(f"  event {ev} is {body} with {{\n    briefly \"{brief}\"\n"
                           f"    described as {{\n      |Published by {ext}.\n    }}\n  }}\n")
            b = lc(ev)
            args = ", ".join(f"{x} = {b}.{x}" for x in fields)
            clauses.append(f"      on {b}: event {ext}.{ev} is {{\n"
                           f"        send command {cmdrel}({args}) to outlet {ctx}.{adaptor}.{out}\n      }}\n")
            cmds.append(cmdrel)
        evs = [e for e, _, _ in events]
        if len(evs) > 1:
            xin = f"type {ext}.{ext}Event"
            xout = f"type {ext}Event"
            xalt = alt(f"{ext}Event", evs, f"Everything {ext} tells the model, unasked")
        else:
            xin, xout, xalt = f"event {ext}.{evs[0]}", f"event {evs[0]}", ""
        external = (f"// {ebrief}\nexternal context {ext} as source is {{\n{xalt}"
                    f"  outlet {ext}EventsOut is {xout} with {{\n"
                    f"    briefly \"What this service tells the model, unasked\"\n  }}\n"
                    + "".join(ev_defs) +
                    f"}} with {{\n  briefly \"{ebrief}\"\n  described as {{\n    |{edesc}\n  }}\n}}\n")
        xf = "external-contexts.riddl"
        t = F.get(xf)
        F.text[xf] = t.rstrip("\n") + "\n" + external
        if len(cmds) > 1:
            cty = f"type {ctx}.{adaptor}Command"
            pre = alt(f"{adaptor}Command", cmds, f"What {adaptor} turns that service's news into")
        else:
            cty, pre = f"command {cmds[0]}", ""
        adaptor_text = (f"  adaptor {adaptor} from context {ext} as flow is {{\n"
                        f"    inlet {adaptor}In is {xin}\n"
                        f"    outlet {out} is {cty}\n"
                        f"    handler {adaptor}Handler is {{\n" + "".join(clauses) +
                        f"      on other is {{\n        error \"Unexpected message for adaptor {adaptor}\"\n      }}\n"
                        f"    }} with {{\n      briefly \"from {ebrief.lower()}\"\n      described as {{\n"
                        f"        |Carries messages from the external {ext}.\n      }}\n    }}\n"
                        f"  }} with {{\n    briefly \"{ext} integration\"\n    described as {{\n"
                        f"      |The model's side of the {ext} conversation.\n    }}\n  }}\n")
        # place the adaptor (and its intake) before the context's first adaptor
        F.before(cf, "  adaptor ", f"context {ctx} ", pre + intake(ctx, adaptor, out, iname, cty) + adaptor_text)
        # the domain connector, beside the model's other persistent connectors
        entry = next(md.glob("*.conf")).read_text().split('"')[1]
        F.before(entry, "  persistent connector ", "", f"  persistent connector '{ext}Event Stream' is from outlet "
                 f"{ext}.{ext}EventsOut to inlet {ctx}.{adaptor}.{adaptor}In with {{\n"
                 f"    briefly \"What {ext} tells {ctx}, unasked\"\n  }}\n")
        n += len(events)
        pending.append(F)
    return n


def main():
    apply = "--apply" in sys.argv
    pending = []
    nb = b_sites(pending)
    nn = new_sources(pending)
    print(f"(b): {nb} sites; new sources: {nn} sites in {len(NEW_SOURCES)} models")
    if apply:
        for F in pending:
            for f, t in F.text.items():
                (F.md / f).write_text(t)
    c2a.run(A2_SITES, apply)


if __name__ == "__main__":
    main()
