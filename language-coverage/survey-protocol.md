# Terrain Survey Protocol

This file exists to be referenced from RIDDL, in two different ways, by
`language-coverage/SurveyContext.riddl`:

- as the context's **description**, via `described in file "survey-protocol.md"`
- as an **attachment**, via `attachment SurveyProtocol is text/markdown in file
  "survey-protocol.md"`

Both forms name a path relative to the `.riddl` file that references them.

## The protocol itself

A survey station is commissioned into exactly one region, takes elevation
readings against the national vertical datum, and is retired when it is
damaged or when the grid no longer needs its sheet. Readings accumulate in
replicated tallies because field devices record while out of contact and
reconcile when they return, so no central arbiter orders them.

Elevations are published to two decimal places. The instruments resolve to a
centimetre and any further precision would be invented.
