# inbound-events — tooling for BACKLOG #36

Turns the bulk-generated `do "the model receives ..."` placeholders into real
inbound conversations. **BACKLOG #36 is the specification** — Reid ruled the
decision per FAMILY so batches need no spot-checking. Apply that table; do not
re-derive it per site.

## Use

```bash
python3 scripts/inbound-events/digest.py 0 12      # models 0..11, by index
python3 scripts/inbound-events/apply.py rows.txt   # apply placements
```

`rows.txt` is one site per line:

```
model|Ctx.Event|cause|action|payload
```

- `cause` — our command or query whose handler emits the event, or `-` for an
  external context that declares only events (Reid: the real system fires those
  and we do not model how a foreign system generates anything)
- `action` — `prose` or `tell`
- `payload` — the prose text, or `LocalCommand::reason`

`apply.py` validates each model after editing it and REVERTS that model on any
finding, so a bad row costs one model, not the corpus. `KEEP=1` suppresses the
revert when you need to inspect the wreckage.

## Why it is shaped the way it is

**One dump per pass, every edit applied in DESCENDING span order.** The first
version re-dumped per external context and silently lost two adaptor inlets out
of four — the model stayed valid, so only a later error revealed it.

**Never edit by line anchor.** prettify jams declarations together, so an adaptor
is routinely not at the start of its line. All header edits use span offsets.

**Never delete by line range** for the same reason: an adaptor's opening line
routinely carries two connectors, and a line-wise prune took them with it.

**The inbound adaptor MUST declare its inlet.** `isStreamTail` opens
`if proc.inlets.isEmpty then false` over DECLARED ports, so an adaptor relying on
A103's implied inlet can never end a chain and its upstream source reports
`stream-source-reaches-no-sink`. This is the OPPOSITE of an ASKING adaptor, which
must declare none. See CLAUDE.md § A103.

**Two adaptors are refused by design** (shopping-cart `InventoryService`,
`PricingService`): they already declare ports, and merging with existing wiring is
what corrupted four models in the outbound campaign before refusal replaced it.

## Characterising what is left

```bash
python3 scripts/inbound-events/characterise.py   # ownership + act-word census
python3 scripts/inbound-events/families.py       # group into BACKLOG #36's families
```

`characterise.py` writes `remaining.json`, which `families.py` reads. Both take
their paths from a scratchpad constant — retarget it before use.
