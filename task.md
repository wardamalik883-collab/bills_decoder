# Task Tracker

Work top to bottom. Tick a box when the task's **Done when** is satisfied. Details for each task are in `tasks/`.
Legend: `[ ]` todo, `[~]` in progress, `[x]` done. Time = rough estimate.

## Phase A: Setup (10:30 - 11:00)
- [x] [T01 - API key and test call](tasks/T01-api-key-and-test-call.md) (10 min)
- [x] [T02 - Project skeleton and config](tasks/T02-project-skeleton.md) (15 min)
- [x] [T03 - Study training bills and build ground truth](tasks/T03-study-training-bills.md) (20 min)

## Phase B: Level 1 Extraction (11:00 - 11:50)
- [x] [T04 - LLM client abstraction](tasks/T04-llm-client.md) (15 min)
- [x] [T05 - Schema and extraction prompt](tasks/T05-schema-and-prompt.md) (20 min)
- [x] [T06 - Extractor](tasks/T06-extractor.md) (15 min)
- [x] [T07 - Validator, retry and evaluation](tasks/T07-validator-and-eval.md) (25 min)

## Phase C: Level 2 Q&A (11:50 - 12:15)
- [x] [T08 - Context extraction and calc tools](tasks/T08-context-and-calc-tools.md) (15 min)
- [x] [T09 - Q&A module](tasks/T09-qa-module.md) (20 min)

## Phase D: Pipeline (12:15 - 12:30)
- [x] [T10 - CSV I/O](tasks/T10-csv-io.md) (10 min)
- [x] [T11 - Pipeline CLI and error handling](tasks/T11-pipeline-cli.md) (15 min)
- [x] [T12 - Dry run on training bills](tasks/T12-dry-run.md) (10 min)

## Phase E: Delivery prep (can overlap with Phase D)
- [x] [T13 - README, .env.example, requirements](tasks/T13-docs.md) (15 min)
- [x] [T14 - Code freeze and packaging script](tasks/T14-packaging-script.md) (10 min)

## Phase F: Test day (12:30 - 1:30)
- [ ] [T15 - Run on test data](tasks/T15-run-on-test-data.md) (20 min)
- [ ] [T16 - Review outputs and fix critical issues](tasks/T16-review-outputs.md) (15 min)
- [ ] [T17 - Final ZIP check and upload](tasks/T17-final-zip-and-upload.md) (10 min)

## Bonus
- [ ] [T18 - Demo video (max 3 min)](tasks/T18-demo-video.md) (10 min, +5 pts)

## Current status
- Last completed task: T14 - Code freeze and packaging script
- Currently blocked on: _T15 needs the 10 test bills + 2 CSV templates from the challenge link_
- Notes: T08-T14 implemented and verified; dry run passes on KESC_0008 with 1 L1 row / 12 L2 rows, no fallbacks.
