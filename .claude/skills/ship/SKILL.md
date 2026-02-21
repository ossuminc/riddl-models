# Ship Skill

Reformats, validates, and pushes all RIDDL models. Follow each
step in order. **STOP immediately** if any step fails and
report the problem.

## Pre-Flight Checks

1. Assert current branch is `main`:
   ```
   git branch --show-current
   ```
   If not on `main`, ask the user before switching.

2. Assert working tree is clean:
   ```
   git status --porcelain
   ```
   If dirty, list the uncommitted files and ask the user how
   to proceed.

3. Pull latest from origin:
   ```
   git pull
   ```

## Ship Steps

4. Reformat all RIDDL models in-place using riddlc prettify:
   ```
   sbt reformat
   ```
   This runs `riddlc prettify` on all 187+ models, ensuring
   consistent formatting across the repository.

5. Validate all models to confirm they parse and pass
   semantic checks:
   ```
   sbt validate
   ```
   Reformat first, then validate — formatting changes can
   affect line numbers in error messages.

6. Check if reformatting produced any changes:
   ```
   git status --porcelain
   ```

7. If files changed, commit the reformatted models:
   ```
   git add -A
   git commit -m "Reformat all RIDDL models"
   ```

8. Push to origin:
   ```
   git push origin main
   ```

## Post-Ship Verification

9. Run `git status` to confirm the working tree is clean.

10. Report: number of models reformatted, validation results,
    and commit SHA (if any changes were committed).

## If Something Fails

- If `sbt reformat` fails in step 4: check that riddlc is
  available (it auto-downloads on first use). Individual model
  failures will be reported with file paths.
- If `sbt validate` fails in step 5: fix the failing models.
  Validation errors include file path and line number.
- If push fails in step 8: pull and resolve conflicts first.
