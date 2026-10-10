# T16 - Review outputs and fix critical issues
**Phase F | ~15 min | Depends on: T15**

## Steps
- [ ] Spot-check each of the 10 Level 1 JSONs against its bill image: provider, dates, readings, totals, payable amounts, signs on credits.
- [ ] Check no identifiers appear in any output.
- [ ] Read all answers to the 3-4 most numeric questions per bill; verify numbers.
- [ ] Fix only **critical** issues (wrong provider, missing fields, crash fallbacks). Rerun just affected bills with `--only`.
- [ ] Avoid last-minute refactors. Regenerate CSVs **with the code**, not by editing them manually (manual edits are not accepted).

## Done when
You are confident the CSVs are valid and reasonable. Stop improving at 1:10 PM.
