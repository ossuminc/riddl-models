#!/usr/bin/env python3
"""BACKLOG #43 step 3 (c), group 2d (Reid, 2026-11-19: case 1 A, case 2 A).

Four commands nothing issues because each is an OUTCOME of, or a step
inside, a clause that already runs:

  * FailReport (client-reporting, marketing-analytics): failure is the
    conditional outcome of composing / completing the report, per the
    2026-10-28 ruling ("conditional outcomes -> when prompt(...) then tell
    event X ... end in the existing clause").
  * usage-rating's ValidateUsageRecord and CalculateCharges: folded into
    the clause before them (submission validates; applying the rate plan
    calculates the charges).

The commands, their alternation membership, the entity clauses and the
context relays are deleted. Exact-text edits; each must match once.

Usage:  apply-c-2d.py [--apply]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TEXT = {}


def get(f):
    if f not in TEXT:
        TEXT[f] = (ROOT / f).read_text()
    return TEXT[f]


def sub(f, old, new):
    t = get(f)
    if t.count(old) != 1:
        sys.exit(f"STOP {f}: {t.count(old)} matches for {old[:90]!r}")
    TEXT[f] = t.replace(old, new)


def drop_definition(f, head):
    """delete `head ... }` and a following ` with { ... }`, whole lines"""
    t = get(f)
    if t.count(head) != 1:
        sys.exit(f"STOP {f}: {t.count(head)} matches for {head!r}")
    s = t.index(head)
    s = t.rindex("\n", 0, s) + 1

    def close(i):
        d = 0
        for j in range(t.index("{", i), len(t)):
            d += {"{": 1, "}": -1}.get(t[j], 0)
            if d == 0:
                return j + 1
    e = close(s)
    if t[e:].startswith(" with {"):
        e = close(e)
    e = t.index("\n", e) + 1
    TEXT[f] = t[:s] + t[e:]


def drop_clause(f, head):
    drop_definition(f, head)


def drop_member(f, member):
    """remove one member from a `one of { a or b or c }` line"""
    t = get(f)
    for old, new in ((f" or {member} or ", " or "), (f"    {member} or ", "    "), (f" or {member}\n", "\n")):
        if t.count(old) == 1:
            TEXT[f] = t.replace(old, new)
            return
    sys.exit(f"STOP {f}: alternation member {member} not found once")


# --- Case 1: FailReport -> a conditional outcome of the generating step
cr = "investment/asset-management/client-reporting/"
sub(cr + "ClientReport.riddl",
    "    on composeReport: command ComposeReport is {\n"
    "      tell event ReportComposed(reportId = composeReport.reportId, composedAt = prompt(\"the composed at of this report composed\")) to entity ReportingContext.ClientReport\n    }\n",
    "    on composeReport: command ComposeReport is {\n"
    "      when prompt(\"the report cannot be composed from the data attached\") then\n"
    "        tell event ReportFailed(reportId = composeReport.reportId, reason = prompt(\"why the report could not be composed\"), failedAt = prompt(\"the failed at of this report failed\")) to entity ReportingContext.ClientReport\n"
    "      else\n"
    "        tell event ReportComposed(reportId = composeReport.reportId, composedAt = prompt(\"the composed at of this report composed\")) to entity ReportingContext.ClientReport\n"
    "      end\n    }\n")
drop_clause(cr + "ClientReport.riddl", "    on failReport: command FailReport is {")
drop_definition(cr + "ClientReport.riddl", "  command FailReport is {")
drop_member(cr + "ClientReport.riddl", "ClientReport.FailReport")
drop_clause(cr + "ReportingContext.riddl", "    on failReport: command ClientReport.FailReport is {")

ma = "marketing/analytics/marketing-analytics/"
sub(ma + "AnalyticsReport.riddl",
    "    on completeReport: command CompleteReport is {\n"
    "      tell event ReportCompleted(reportId = completeReport.reportId, summary = completeReport.summary, completedAt = completeReport.completedAt) to entity AnalyticsContext.AnalyticsReport\n    }\n",
    "    on completeReport: command CompleteReport is {\n"
    "      when prompt(\"the report cannot be completed from the metrics gathered\") then\n"
    "        tell event ReportFailed(reportId = completeReport.reportId, reason = prompt(\"why the report could not be completed\"), failedAt = completeReport.completedAt) to entity AnalyticsContext.AnalyticsReport\n"
    "      else\n"
    "        tell event ReportCompleted(reportId = completeReport.reportId, summary = completeReport.summary, completedAt = completeReport.completedAt) to entity AnalyticsContext.AnalyticsReport\n"
    "      end\n    }\n")
drop_clause(ma + "AnalyticsReport.riddl", "    on failReport: command FailReport is {")
drop_definition(ma + "AnalyticsReport.riddl", "  command FailReport is {")
drop_member(ma + "AnalyticsReport.riddl", "AnalyticsReport.FailReport")
drop_clause(ma + "AnalyticsContext.riddl", "    on failReport: command AnalyticsReport.FailReport is {")

# --- Case 2: usage-rating's two pipeline steps fold into the step before
ur = "telecommunications/billing/usage-rating/"
sub(ur + "UsageRecord.riddl",
    "      tell event UsageRecordSubmitted(usageRecordId = self.id, accountId = accountId, submittedAt = prompt(\"the submitted at of this usage record submitted\")) to entity RatingContext.UsageRecord\n    }\n",
    "      tell event UsageRecordSubmitted(usageRecordId = self.id, accountId = accountId, submittedAt = prompt(\"the submitted at of this usage record submitted\")) to entity RatingContext.UsageRecord\n"
    "      when prompt(\"the call detail record passes validation\") then\n"
    "        tell event UsageRecordValidated(usageRecordId = self.id, validatedAt = prompt(\"the validated at of this usage record validated\")) to entity RatingContext.UsageRecord\n"
    "      end\n    }\n")
sub(ur + "UsageRecord.riddl",
    "      tell event RatePlanApplied(usageRecordId = applyRatePlan.usageRecordId, ratePlanId = prompt(\"the rate plan id of this rate plan applied\"), appliedAt = prompt(\"the applied at of this rate plan applied\")) to entity RatingContext.UsageRecord\n    }\n",
    "      tell event RatePlanApplied(usageRecordId = applyRatePlan.usageRecordId, ratePlanId = prompt(\"the rate plan id of this rate plan applied\"), appliedAt = prompt(\"the applied at of this rate plan applied\")) to entity RatingContext.UsageRecord\n"
    "      tell event ChargesCalculated(usageRecordId = applyRatePlan.usageRecordId, totalAmount = prompt(\"the charges the applied rate plan gives this record\"), chargeCount = prompt(\"the charge count of this charges calculated\"), calculatedAt = prompt(\"the calculated at of this charges calculated\")) to entity RatingContext.UsageRecord\n    }\n")
for cmd in ("ValidateUsageRecord", "CalculateCharges"):
    drop_clause(ur + "UsageRecord.riddl", f"    on {cmd[:1].lower() + cmd[1:]}: command {cmd} is {{")
    drop_definition(ur + "UsageRecord.riddl", f"  command {cmd} is {{")
    drop_member(ur + "UsageRecord.riddl", f"UsageRecord.{cmd}")
    drop_clause(ur + "RatingContext.riddl", f"    on {cmd[:1].lower() + cmd[1:]}: command UsageRecord.{cmd} is {{")

if __name__ == "__main__":
    print(f"{len(TEXT)} files planned")
    if "--apply" in sys.argv:
        for f, t in TEXT.items():
            (ROOT / f).write_text(t)
