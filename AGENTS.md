# Standing Agent Rules

All AI assistants working on this codebase must follow these standing rules:

1. **One Task at a Time**:
   - Work strictly on one task at a time as specified in `task.md`.
   - Never implement or start anything beyond the current requested task.

2. **Security & Secrets**:
   - Never open, read, print, cat, or log `.env`, API key values, or any GitHub token.
   - Never embed tokens or credentials in remote URLs or commit messages.

3. **Allowed Models**:
   - Only use allowed models: `gemini-3.1-flash-lite`, `gemini-3.5-flash-lite`, `gpt-4.1-mini`, `gpt-5-mini`, `claude-haiku-4-5`.
   - Always read the model name dynamically from the `MODEL_NAME` environment variable without hardcoded fallback.

4. **File Deletion Restriction**:
   - Never delete files or folders without asking me first.

5. **Task Completion & Git Workflow**:
   - After each task is finished:
     1. Tick the task checkbox in `task.md`.
     2. Stage changes: `git add .`
     3. Check tracked files: `git ls-files`
     4. **CRITICAL ABORT CHECK**: If `.env`, `.venv`, `data/`, `cache/`, or any file containing `"AIza"` or a real `API_KEY` value appears in staged/tracked files, **ABORT IMMEDIATELY** and alert the user.
     5. If checks pass, commit with message format: `Txx: <title>`.
     6. Push to remote: `git push origin main`.
     7. Show the files changed and commit result.

6. **Push Failure Handling**:
   - If `git push` fails, display the error message without exposing any token or credential, and stop.

7. **User Verification**:
   - Always end each response with clear instructions on how the user can verify the task themselves.
