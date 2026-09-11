#!/usr/bin/env python3
"""Group the remaining sites into decision FAMILIES.

The discriminator the first 157 actually turned on was not ack-vs-news, it was:
did the external system DO something that changes a fact we hold, or merely
confirm receipt of what we asked for?
"""
import json, re, collections
SP='scripts/inbound-events'
rows=json.load(open(SP+'/remaining.json'))
FAM=[
 ("A receipt-confirmed",   r"(Stored|Sent|Indexed|Published|Tracked|Fetched|Retrieved|Synced|Posted|Uploaded|Logged|Queued|Subscribed|Archived|Exported|Imported|Cached|Registered|Enqueued)$"),
 ("B record-changed",      r"(Created|Updated|Changed|Modified|Added|Removed|Deleted|Deactivated|Activated|Closed|Opened|Terminated|Hired|Onboarded)$"),
 ("C gate-passed",         r"(Verified|Validated|Approved|Cleared|Accepted|Succeeded|Granted|Authorized|Authenticated|Qualified|Eligible|Passed|Checked|Confirmed)$"),
 ("D gate-refused",        r"(Failed|Rejected|Declined|Denied|Unavailable|Expired|Cancelled|Canceled|Revoked|Suspended|Blocked|Returned|Bounced|Error|Errored)$"),
 ("E resource-booked",     r"(Reserved|Released|Allocated|Scheduled|Assigned|Provisioned|Dispatched|Booked|Deallocated|Unassigned|Freed)$"),
 ("F money-moved",         r"(Processed|Captured|Refunded|Paid|Disbursed|Settled|Charged|Credited|Debited|Invoiced|Billed|Received)$"),
 ("G work-finished",       r"(Completed|Complete|Delivered|Shipped|Finished|Done|Fulfilled|Executed|Performed|Rendered|Transcoded|Built)$"),
 ("H measured-or-told",    r"(Recorded|Reported|Calculated|Measured|Detected|Raised|Triggered|Alert|Alerted|Notification|Notified|Issued|Generated|Submitted|Requested|Started|Begun|Initiated)$"),
]
fam=collections.defaultdict(list)
for r in rows:
    for name,pat in FAM:
        if re.search(pat, r["event"]):
            fam[name].append(r); break
    else:
        fam["Z unclassified"].append(r)
tot=0
for name,_ in FAM+[("Z unclassified",None)]:
    rs=fam.get(name,[])
    if not rs: continue
    tot+=len(rs)
    own=collections.Counter('ack' if x['ack'] else ('asked' if x['asks'] else 'news') for x in rs)
    print(f"\n{name}: {len(rs)} sites   ownership {dict(own)}")
    seen=[]
    for x in rs:
        k=f"{x['ctx']}.{x['event']}"
        if k not in seen: seen.append(k)
    print("    e.g. "+", ".join(seen[:7]))
print(f"\ntotal classified: {tot} of {len(rows)}")
if fam.get("Z unclassified"):
    print("\nunclassified tails:", collections.Counter(
        re.findall(r"[A-Z][a-z]+|[A-Z]+(?![a-z])", x['event'])[-1]
        for x in fam["Z unclassified"]).most_common(25))
