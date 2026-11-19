#!/usr/bin/env python3
"""BACKLOG #43 step 3 (c), group 2a: 13 commands whose source system is
wired in through an inbound adaptor but never publishes the event that
triggers them (Reid, 2026-11-19, option A).

For each site:
  * the external context gains the event, carrying exactly the fields of
    the command it triggers (copied from the command's own source), joins
    the context's `<Ext>Event` alternation (created when its outlet named a
    single event), and its boundary handler publishes it from the clause it
    follows, inside `when prompt(...)` because it happens only sometimes
  * the inbound adaptor's inlet widens to that alternation, and a new clause
    sends the command, field for field, on the adaptor's outlet
  * the adaptor's outlet carries the command: a single-command outlet becomes
    a `<Adaptor>Command` alternation shared with its intake inlet, an
    existing alternation gains it, a sink gains outlet + intake inlet +
    connector (re-ascribe afterwards)

Facts (spans, fields, port types) come from `riddlc dump --json`; edits are
exact-text replacements that must match once, or nothing is written.

Usage:  apply-c-2a.py [--apply]
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RIDDLC = str(ROOT.parent / "bin" / "riddlc")

# model, external, new event, antecedent clause (in the external), guard,
# adaptor, command path (relative to the handling context), event brief
SITES = [
    ("commerce/e-commerce/order-management", "ShippingCarrier", "DeliveryFailedByCarrier",
     "on createShipment: command CreateShipment is {", "the delivery attempt fails",
     "ShippingAdapter", "Shipment.MarkFailed", "Delivery failed"),
    ("engineering/product-development/plm-integration", "PLMSystemService", "ProductChanged",
     "on command FetchProduct is {", "the product later changes in PLM",
     "FromPLMSystemService", "Integration.ProcessChangeEvent", "Product changed"),
    ("finance/banking/fund-transfer", "ACHNetworkService", "ACHReturnReceived",
     "on command SubmitACHTransaction is {", "the receiving bank returns the entry",
     "FromACHNetworkService", "Transfer.ReturnTransfer", "ACH return received"),
    ("finance/payments/payment-processing", "CardNetworkService", "ChargebackReceived",
     "on command SendAuthRequest is {", "the cardholder later disputes the charge",
     "FromCardNetworkService", "Payment.RecordDispute", "Chargeback received"),
    ("finance/payments/payment-processing", "SettlementService", "SettlementCompleted",
     "on command SubmitForSettlement is {", "the settlement completes",
     "FromSettlementService", "Payment.SettlePayment", "Settlement completed"),
    ("finance/trading/trade-settlement", "CustodianService", "PartialSettlementReported",
     "on command SendSettlementInstruction is {", "only part of the instruction settles",
     "FromCustodianService", "Settlement.RecordPartialSettlement", "Partial settlement reported"),
    ("logistics/fulfillment/order-fulfillment", "CarrierSystem", "DeliveryConfirmedByCarrier",
     "on command BookShipment is {", "the carrier delivers the shipment",
     "FromCarrierSystem", "FulfillmentOrder.ConfirmDelivery", "Delivery confirmed"),
    ("logistics/fulfillment/order-fulfillment", "CarrierSystem", "DeliveryFailedByCarrier",
     "on command BookShipment is {", "the carrier fails to deliver the shipment",
     "FromCarrierSystem", "FulfillmentOrder.FailDelivery", "Delivery failed"),
    ("logistics/supply-chain/demand-planning", "ERPIntegration", "ActualDemandReported",
     "on command PublishForecast is {", "the forecast period closes with actual demand recorded",
     "FromERPIntegration", "Forecast.RecordActuals", "Actual demand reported"),
    ("logistics/supply-chain/order-fulfillment", "ShippingCarrier", "ShipmentDelivered",
     "on command CreateShipment is {", "the carrier delivers the shipment",
     "FromShippingCarrier", "FulfillmentOrder.ConfirmDelivery", "Shipment delivered"),
    ("technology/devops/observability", "MetricsCollectionService", "ThresholdBreached",
     "on command IngestMetrics is {", "an ingested metric breaches an alert rule's threshold",
     "FromMetricsCollectionService", "CreateAlert", "Threshold breached"),
    ("transportation/freight/customs-brokerage", "CBPAceService", "EntryLiquidationPosted",
     "on command CBPAceService.SubmitEntry is {", "CBP later posts the entry's liquidation",
     "FromCBPAceService", "Entry.RecordLiquidation", "Entry liquidation posted"),
    ("utilities/metering/smart-metering", "HeadEndSystem", "MeterAlarmRaised",
     "on command PollMeter is {", "the meter reports an alarm",
     "FromHeadEndSystem", "Meter.RaiseAlert", "Meter alarm raised"),
]


def lc(s):
    return s[:1].lower() + s[1:]


def dump(md):
    conf = next(md.glob("*.conf"))
    entry = re.search(r'input-file\s*=\s*"([^"]+)"', conf.read_text()).group(1)
    p = subprocess.run([RIDDLC, "dump", entry, "--json"], cwd=md, capture_output=True, text=True)
    return json.loads(p.stdout)


def carried(byp, port):
    r = (port.get("type") or {}).get("resolved")
    out, stack = set(), [r]
    while stack:
        x = stack.pop()
        out.add(x)
        n = byp.get(x)
        if n and n.get("alternation"):
            stack += [a["resolved"] for a in n["alternation"]]
    return out


def body_of(text):
    """the `{ ... }` field block of a message definition's source text"""
    i = text.index("{")
    d = 0
    for j in range(i, len(text)):
        d += {"{": 1, "}": -1}.get(text[j], 0)
        if d == 0:
            return text[i:j + 1]
    raise ValueError("unbalanced")


class Files:
    def __init__(self, md):
        self.md, self.text = md, {}

    def get(self, f):
        if f not in self.text:
            self.text[f] = (self.md / f).read_text()
        return self.text[f]

    def sub(self, f, old, new):
        t = self.get(f)
        n = t.count(old)
        if n != 1:
            sys.exit(f"STOP {self.md.name}/{f}: {n} matches for {old[:100]!r}")
        self.text[f] = t.replace(old, new)

    def after(self, f, anchor, start, new):
        """insert `new` after the first line containing `anchor` at or after `start`"""
        t = self.get(f)
        i = t.index(start)
        k = t.index(anchor, i)
        e = t.index("\n", k) + 1
        self.text[f] = t[:e] + new + t[e:]

    def end_of_clause(self, f, head, start, new):
        """insert `new` as the last statements of the clause opened by `head`"""
        t = self.get(f)
        k = t.index(head, t.index(start))
        d, j = 0, t.index("{", k)
        while True:
            d += {"{": 1, "}": -1}.get(t[j], 0)
            if d == 0:
                break
            j += 1
        e = t.rindex("\n", 0, j) + 1
        self.text[f] = t[:e] + new + t[e:]

    def before(self, f, anchor, start, new):
        t = self.get(f)
        i = t.index(start)
        k = t.rindex("\n", 0, t.index(anchor, i)) + 1
        self.text[f] = t[:k] + new + t[k:]


def main():
    apply = "--apply" in sys.argv
    by_model = defaultdict(list)
    for s in SITES:
        by_model[s[0]].append(s)
    total = 0
    pending = []
    for model, sites in by_model.items():
        md = ROOT / model
        nodes = dump(md)
        byp = {n["path"]: n for n in nodes if "path" in n}
        kids = defaultdict(list)
        for n in nodes:
            kids[n.get("parent")].append(n)
        F = Files(md)
        alt_done, adaptor_done = set(), set()
        for (_, ext, ev, antecedent, guard, adaptor, cmdrel, brief) in sites:
            # the command, its fields and source
            cmd = [n for n in nodes if n["kind"] == "command" and n["path"].endswith("." + cmdrel)]
            assert len(cmd) == 1, (model, cmdrel, len(cmd))
            cmd = cmd[0]
            fields = [f["id"] for f in kids[cmd["path"]] if f["kind"] == "field"]
            src = F.get(cmd["file"])
            # locate the command by its span
            lines = src.split("\n")
            off = sum(len(l) + 1 for l in lines[:cmd["span"]["start"]["line"] - 1])
            block = body_of(src[off:])
            # 1. the external context: event, alternation, publication
            xn = [n for n in nodes if n["kind"] == "context" and n["id"] == ext]
            assert len(xn) == 1
            xf = xn[0]["file"]
            xhead = f"external context {ext} "
            event_text = (f"  event {ev} is {re.sub(chr(10) + '  ', chr(10), block)} with {{\n"
                          f"    briefly \"{brief}\"\n    described as {{\n"
                          f"      |Published by {ext} when {guard}.\n    }}\n  }}\n")
            # indent: the command lived one level deeper than the external's events
            F.before(xf, "  handler ", xhead, event_text)
            outlet = f"  outlet {ext}EventsOut is "
            t = F.get(xf)
            seg = t[t.index(xhead):]
            m = re.search(re.escape(outlet) + r"event (\w+)\n", seg)
            if m and ext not in alt_done:
                F.sub(xf, f"{outlet}event {m.group(1)}\n",
                      f"  type {ext}Event is one of {{\n    {m.group(1)} or {ev}\n  }} with {{\n"
                      f"    briefly \"What {ext} publishes\"\n  }}\n{outlet}type {ext}Event\n")
                alt_done.add(ext)
                single_in = m.group(1)
            else:
                am = re.search(r"  type " + ext + r"Event is one of \{\n    ([^\n]*)\n", F.get(xf))
                assert am, (model, ext, "no event alternation")
                F.sub(xf, am.group(0), am.group(0).replace(am.group(1), am.group(1) + " or " + ev))
                single_in = None
            pub = (f"      when prompt(\"{guard}\") then\n"
                   f"        let {lc(ev)}: type {ev} = prompt(\"the {brief.lower()} this produces\")\n"
                   f"        send {lc(ev)} to outlet {ext}.{ext}EventsOut\n      end\n")
            F.end_of_clause(xf, antecedent, xhead, pub)
            # 2. the adaptor: inlet, clause, outlet
            ad = [n for n in nodes if n["kind"] == "adaptor" and n["id"] == adaptor]
            assert len(ad) == 1
            ad = ad[0]
            af, ctxn = ad["file"], byp[ad["parent"]]
            ctx = ctxn["id"]
            ahead = f"  adaptor {adaptor} from context {ext} "
            ports = {p["id"]: p for p in kids[ad["path"]] if p["kind"] in ("inlet", "outlet")}
            inl = [p for p in ports.values() if p["kind"] == "inlet"]
            outs = [p for p in ports.values() if p["kind"] == "outlet"]
            if single_in and adaptor not in adaptor_done:
                F.sub(af, f"    inlet {inl[0]['id']} is event {ext}.{single_in}\n",
                      f"    inlet {inl[0]['id']} is type {ext}.{ext}Event\n")
            if not outs:  # a sink: give it an outlet, an intake inlet and a connector
                on = f"{adaptor}To{ctx}"
                iname = f"{ctx}From{adaptor.removeprefix('From')}"
                F.after(af, f"    inlet {inl[0]['id']} is ", ahead, f"    outlet {on} is command {cmdrel}\n")
                F.before(af, ahead.strip(), ahead,
                         f"  inlet {iname} is command {cmdrel} with {{\n"
                         f"    briefly \"What {adaptor} makes of that service's news\"\n  }}\n"
                         f"  connector '{adaptor} Intake' is from outlet {ctx}.{adaptor}.{on} to inlet {ctx}.{iname} with {{\n"
                         f"    briefly \"What {adaptor} makes of that news, on its way in\"\n  }}\n")
                outlet_id = on
            else:
                # the outlet connected to this context
                outlet_id = None
                for o in outs:
                    for c in nodes:
                        if c["kind"] == "connector" and c["from"]["resolved"] == o["path"]:
                            ip = byp[c["to"]["resolved"]]
                            if ip["parent"] == ctxn["path"]:
                                # prefer the outlet whose type already carries the command
                                if outlet_id is None or cmd["path"] in carried(byp, o):
                                    outlet_id, oport, iport = o["id"], o, ip
                assert outlet_id, (model, adaptor, "no outlet into the context")
                ot = oport["type"]["resolved"]
                target = cmd["path"]
                otn = byp.get(ot)
                if otn and otn["kind"] == "command":  # single command -> alternation
                    single = ot.split(ctxn["path"] + ".", 1)[1]
                    altname = f"{adaptor}Command"
                    if adaptor not in adaptor_done:
                        F.sub(af, f"    outlet {outlet_id} is command {single}\n",
                              f"    outlet {outlet_id} is type {ctx}.{altname}\n")
                        F.sub(iport["file"], f"  inlet {iport['id']} is command {single} with {{\n",
                              f"  type {altname} is one of {{\n    {single} or {cmdrel}\n  }} with {{\n"
                              f"    briefly \"What {adaptor} turns that service's news into\"\n  }}\n"
                              f"  inlet {iport['id']} is type {ctx}.{altname} with {{\n")
                    else:
                        F.sub(iport["file"], f"    {single} or ", f"    {single} or {cmdrel} or ")
                elif otn and otn.get("alternation"):
                    members = set()
                    stack = [a["resolved"] for a in otn["alternation"]]
                    while stack:
                        r = stack.pop()
                        members.add(r)
                        rn = byp.get(r)
                        if rn and rn.get("alternation"):
                            stack += [a["resolved"] for a in rn["alternation"]]
                    if target not in members:
                        tn = ot.split(".")[-1]
                        am = re.search(r"  type " + tn + r" is one of \{\n    ([^\n]*)\n", F.get(otn["file"]))
                        assert am, (model, tn)
                        F.sub(otn["file"], am.group(0), am.group(0).replace(am.group(1), am.group(1) + " or " + cmdrel))
                else:
                    sys.exit(f"STOP {model} {adaptor}: outlet type {ot} not understood")
            b = lc(ev)
            args = ", ".join(f"{f} = {b}.{f}" for f in fields)
            F.before(af, "      on other is {", ahead,
                     f"      on {b}: event {ext}.{ev} is {{\n"
                     f"        send command {cmdrel}({args}) to outlet {ctx}.{adaptor}.{outlet_id}\n      }}\n")
            adaptor_done.add(adaptor)
            total += 1
        pending.append(F)
    print(f"{total} sites planned in {len(by_model)} models")
    if apply:
        for F in pending:
            for f, t in F.text.items():
                (F.md / f).write_text(t)


if __name__ == "__main__":
    main()
