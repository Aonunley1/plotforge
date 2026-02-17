---
description: Audit the project to ensure the live code matches the saved state
---
1.  **Read Sync File**: Read `.context/sync_state.md`.
2.  **Architecture Audit**: Run a quick directory tree check to see if files listed in the sync state actually exist.
3.  **Linter Check**: Run `get_file_problems` on the most recently modified file to check for hidden regressions.
4.  **Task Alignment**: Compare the user's latest requests with the "Pending Tasks" list.
5.  **State Verdict**: 
    -   If everything matches: Report "**STATUS: Sync Green**".
    -   If files are missing or tasks have drifted: Suggest a "**STATUS: Sync Red - /refresh recommended**".
