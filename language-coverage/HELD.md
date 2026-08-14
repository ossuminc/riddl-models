# HELD — not part of the corpus yet

This model is complete and validates clean (0 messages, riddlc 2.0.0-rc.14),
but it is deliberately NOT part of the repository's gates and is NOT committed.

**Why:** building it found six defects in riddlc's source emitter. Three of
them make `prettify` produce output that does not parse, and two silently
delete constructs this model exists to exercise. Running `sbt riddlcPrettify`
over this directory would corrupt it. Filed upstream as
`../../riddl/task/2026-08-14-prettify-emitter-drops-method-and-shown-by.md`.

**How it is held:** the riddlc gates (`sbt v`, `sbt r`, `sbt b`, the test
suite, `verify-bast-roundtrip.sh`) all enumerate `.conf` files, so
`language-coverage.conf` has been renamed to `language-coverage.conf.held`.
Nothing discovers this directory while that rename stands.

**To land it** once the emitter fixes ship:

1. `mv language-coverage.conf.held language-coverage.conf`
2. `../bin/riddlc validate language-coverage.riddl` — expect 0 messages
3. `sbt b` to generate `.bast`, then `./scripts/verify-bast-roundtrip.sh`
4. delete this file and commit

See BACKLOG.md § 1e.
