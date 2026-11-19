#!/usr/bin/env python3
"""BACKLOG #43 step 3, rule (b): the 17 commands another system triggers,
wired through that system's existing inbound adaptor (Reid, 2026-11-19,
option A: guarded sends where one generic event carries several facts).

Hand-written, one entry per adaptor, because each site was read first
(`step3-verdicts.tsv`). Every edit is an exact-text replacement that must
match once, or the script stops before writing anything. Per adaptor:

  * a single-command outlet becomes an alternation `From<X>Command`,
    declared beside the context's intake inlet, and the inlet takes it too
  * a sink adaptor (no outlet) gains an outlet, a context inlet and an
    intake connector; `reascribe.py` re-derives both shapes afterwards
  * the trigger clause gains `let`/`send` (inside `when prompt(...)` where
    the event only sometimes means the command)

Usage:  apply-b-sites.py [--apply]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def alt_type(ctx, adaptor, members):
    body = " or ".join(members)
    return (f"  type {adaptor}Command is one of {{\n    {body}\n  }} with {{\n"
            f"    briefly \"What {adaptor} turns that service's news into\"\n  }}\n")


def send(ty, why, outlet, ind, guard=None, name=None):
    # The binding is named for the command it holds (`calculateScore`): a
    # name for its meaning (`score`, `location`) shadowed a definition in 5
    # of 11 models (`name-shadows-definition`). The `name` argument below is
    # ignored and kept only so each call still reads as written.
    c = ty.split(".")[-1]
    name = c[:1].lower() + c[1:]
    lines =[f"let {name}: type {ty} = prompt(\"{why}\")", f"send {name} to outlet {outlet}"]
    if guard:
        lines = [f"when prompt(\"{guard}\") then"] + ["  " + l for l in lines] + ["end"]
    return "".join(ind + l + "\n" for l in lines)


I6 = "        "
EDITS = {}


def edit(f, old, new):
    EDITS.setdefault(f, []).append((old, new))


def retype(f, ctx, adaptor, single, members, inlet):
    """single-command outlet and intake inlet -> a From<X>Command alternation"""
    edit(f, f"    outlet {adaptor}To{ctx} is command {single}\n",
         f"    outlet {adaptor}To{ctx} is type {ctx}.{adaptor}Command\n")
    old = f"  inlet {inlet} is command {single} with {{\n"
    edit(f, old, alt_type(ctx, adaptor, members) + f"  inlet {inlet} is type {ctx}.{adaptor}Command with {{\n")


def after_clause(f, head, last, extra):
    """append `extra` after the clause whose head and last body line are given"""
    edit(f, head + last, head + last + extra)


# --- credit-decisioning: two adaptors, each already sending one command
f = "finance/banking/credit-decisioning/DecisionContext.riddl"
retype(f, "DecisionContext", "FromCreditBureauService", "Decision.AddBureauData",
       ["Decision.AddBureauData", "Decision.CalculateScore"], "DecisionContextFromCreditBureauService")
retype(f, "DecisionContext", "FromPolicyEngineService", "Decision.RenderDecision",
       ["Decision.ApplyPolicy", "Decision.RenderDecision"], "DecisionContextFromPolicyEngineService")
o = "DecisionContext.FromCreditBureauService.FromCreditBureauServiceToDecisionContext"
edit(f, f"        send item0 to outlet {o}\n",
     f"        send item0 to outlet {o}\n"
     + send("Decision.CalculateScore", "the score the decision computes once the bureau's report is in", o, I6, name="score"))
o = "DecisionContext.FromPolicyEngineService.FromPolicyEngineServiceToDecisionContext"
edit(f, "      on policyEvaluated: event PolicyEngineService.PolicyEvaluated is {\n",
     "      on policyEvaluated: event PolicyEngineService.PolicyEvaluated is {\n"
     + send("Decision.ApplyPolicy", "the policy rules the engine evaluated, recorded on the decision before it is rendered", o, I6, name="policy"))

# --- trading order-management
f = "finance/trading/order-management/OrderContext.riddl"
retype(f, "OrderContext", "FromExecutionVenueService", "TradingOrder.FillOrder",
       ["TradingOrder.ReportExecution", "TradingOrder.FillOrder"], "OrderContextFromExecutionVenueService")
o = "OrderContext.FromExecutionVenueService.FromExecutionVenueServiceToOrderContext"
edit(f, "      on venueExecution: event ExecutionVenueService.VenueExecution is {\n",
     "      on venueExecution: event ExecutionVenueService.VenueExecution is {\n"
     + send("TradingOrder.ReportExecution", "the execution report this venue execution is", o, I6, name="report"))

# --- trade-settlement: the alternation already exists
f = "finance/trading/trade-settlement/SettlementContext.riddl"
edit(f, "    Settlement.HoldSettlement or Settlement.MatchTrade\n",
     "    Settlement.HoldSettlement or Settlement.MatchTrade or Settlement.AffirmTrade\n")
o = "SettlementContext.FromTradeMatchingService.FromTradeMatchingServiceToSettlementContext"
edit(f, "matched state records\")\n        send item0 to outlet " + o + "\n",
     "matched state records\")\n        send item0 to outlet " + o + "\n"
     + send("Settlement.AffirmTrade", "the affirmation that follows a confirmed match", o, I6, name="affirm"))

# --- event-registration
f = "hospitality/events/event-registration/RegistrationContext.riddl"
retype(f, "RegistrationContext", "FromPaymentProcessingService", "Registration.ConfirmRegistration",
       ["Registration.ProcessPayment", "Registration.ConfirmRegistration", "Registration.ProcessRefund"],
       "RegistrationContextFromPaymentProcessingService")
o = "RegistrationContext.FromPaymentProcessingService.FromPaymentProcessingServiceToRegistrationContext"
edit(f, "      on paymentSucceeded: event PaymentProcessingService.PaymentSucceeded is {\n",
     "      on paymentSucceeded: event PaymentProcessingService.PaymentSucceeded is {\n"
     + send("Registration.ProcessPayment", "the payment the processor took, with its transaction", o, I6, name="payment"))
edit(f, "        do \"the refund has gone; cancelling the registration was recorded here\"\n",
     "        do \"the refund has gone; cancelling the registration was recorded here\"\n"
     + send("Registration.ProcessRefund", "the refund the processor returned", o, I6, name="refund"))

# --- shipment-tracking: one generic update, five guarded facts
f = "logistics/freight/shipment-tracking/TrackingContext.riddl"
retype(f, "TrackingContext", "FromCarrierIntegration", "Shipment.AddTrackingEvent",
       ["Shipment.AddTrackingEvent", "Shipment.RecordPickup", "Shipment.MarkOutForDelivery",
        "Shipment.RecordDelivery", "Shipment.UpdateETA", "Shipment.UpdateLocation"],
       "TrackingContextFromCarrierIntegration")
o = "TrackingContext.FromCarrierIntegration.FromCarrierIntegrationToTrackingContext"
extra = "".join([
    send("Shipment.RecordPickup", "the pickup the carrier scanned", o, I6, "the update includes a pickup scan", "pickup"),
    send("Shipment.MarkOutForDelivery", "the out-for-delivery the carrier scanned", o, I6, "the update includes an out-for-delivery scan", "outForDelivery"),
    send("Shipment.RecordDelivery", "the delivery the carrier scanned", o, I6, "the update includes a delivery scan", "delivery"),
    send("Shipment.UpdateETA", "the arrival time the carrier revised", o, I6, "the update revises the estimated arrival", "eta"),
    send("Shipment.UpdateLocation", "where the latest scan places the shipment", o, I6, "the update reports a location", "location"),
])
edit(f, "tracking history the shipment shows\")\n        send item0 to outlet " + o + "\n",
     "tracking history the shipment shows\")\n        send item0 to outlet " + o + "\n" + extra)

# --- deployment-pipeline
f = "technology/devops/deployment-pipeline/DeploymentContext.riddl"
retype(f, "DeploymentContext", "FromInfrastructureService", "Deployment.FailDeployment",
       ["Deployment.FailDeployment", "Environment.UpdateEnvironmentArtifact"],
       "DeploymentContextFromInfrastructureService")
o = "DeploymentContext.FromInfrastructureService.FromInfrastructureServiceToDeploymentContext"
edit(f, "        do \"the rollout is on the infrastructure; verification follows the health check\"\n",
     "        do \"the rollout is on the infrastructure; verification follows the health check\"\n"
     + send("Environment.UpdateEnvironmentArtifact", "the artifact now deployed to the environment the rollout landed on", o, I6, name="artifact"))

# --- smart-metering
f = "utilities/metering/smart-metering/MeteringContext.riddl"
retype(f, "MeteringContext", "FromHeadEndSystem", "Meter.RecordReading",
       ["Meter.RecordReading", "Meter.RecordIntervalData"], "MeteringContextFromHeadEndSystem")
o = "MeteringContext.FromHeadEndSystem.FromHeadEndSystemToMeteringContext"
edit(f, "answered the poll with is the one it records\")\n        send item0 to outlet " + o + "\n",
     "answered the poll with is the one it records\")\n        send item0 to outlet " + o + "\n"
     + send("Meter.RecordIntervalData", "the interval reads the head-end system delivered with the response", o, I6,
            "the response carries interval data", "intervals"))

# --- e-commerce order-management: OrderRequest already carries Order.OrderCommand
f = "commerce/e-commerce/order-management/OrderContext.riddl"
edit(f, "      on shipmentPickedUp: event ShippingCarrier.ShipmentPickedUp is {\n",
     "      on shipmentPickedUp: event ShippingCarrier.ShipmentPickedUp is {\n"
     + send("Order.ShipOrder", "the order the carrier has now picked up, with its tracking number", "OrderContext.ShippingAdapter.ShippingAdapterToOrderContext", I6, name="shipOrder"))

# --- incident-management: IncidentRequest already carries Incident.IncidentCommand
f = "technology/devops/incident-management/IncidentContext.riddl"
edit(f, "        do \"Check if incident should be auto-resolved\"\n",
     "        do \"Check if incident should be auto-resolved\"\n"
     + send("Incident.ResolveIncident", "the resolution the cleared alert implies", "IncidentContext.AlertAdapter.AlertAdapterToIncidentContext", I6,
            "the incident should be auto-resolved", "resolve"))

# --- two sinks gain an outlet, a context inlet and an intake connector
def sink(f, ctx, adaptor, inlet_line, cmd, clause_old, guard, why, name):
    out = f"{adaptor}To{ctx}"
    o = f"{ctx}.{adaptor}.{out}"
    edit(f, inlet_line, inlet_line + f"    outlet {out} is command {cmd}\n")
    edit(f, clause_old, clause_old + send(cmd, why, o, I6, guard, name))
    edit(f, f"  adaptor {adaptor} from context",
         f"  inlet {ctx}From{adaptor} is command {cmd} with {{\n"
         f"    briefly \"What {adaptor} makes of that service's news\"\n  }}\n"
         f"  connector '{adaptor} Intake' is from outlet {o} to inlet {ctx}.{ctx}From{adaptor} with {{\n"
         f"    briefly \"What {adaptor} makes of that news, on its way in\"\n  }}\n"
         f"  adaptor {adaptor} from context")

sink("construction/field-operations/equipment-tracking/EquipmentContext.riddl", "EquipmentContext", "GPSAdapter",
     "    inlet GPSAdapterIn is event GPSTrackingService.LocationPing\n", "Equipment.UpdateLocation",
     "        do \"Update equipment location from GPS\"\n", None,
     "the equipment location this GPS ping reports", "location")
sink("finance/payments/payment-processing/PaymentContext.riddl", "PaymentContext", "FromCardNetworkService",
     "    inlet FromCardNetworkServiceIn is event CardNetworkService.AuthResponseReceived\n", "Payment.DeclinePayment",
     "        do \"the network has answered; authorising or declining follows from what it says\"\n",
     "the network declined the authorisation", "the decline the network's answer records", "decline")


def main():
    apply = "--apply" in sys.argv
    out = {}
    for f, eds in EDITS.items():
        text = (ROOT / f).read_text()
        for old, new in eds:
            n = text.count(old)
            if n != 1:
                sys.exit(f"STOP {f}: {n} matches for {old[:90]!r}")
            text = text.replace(old, new)
        out[f] = text
    print(f"{sum(len(e) for e in EDITS.values())} edits in {len(EDITS)} files")
    if apply:
        for f, text in out.items():
            (ROOT / f).write_text(text)


if __name__ == "__main__":
    main()
