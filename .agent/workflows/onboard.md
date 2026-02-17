---
description: Start a new session by synchronizing with the latest saved state
---
1.  **Read Rules**: Immediately read all files in `.agent/rules/` to load project standards.
2.  **Sync State**: Read `.context/sync_state.md` to restore working memory (Active Objective, Tasks, Bugs).
3.  **Vitals Check**: 
    -   Check if the virtual environment is detected.
    -   Verify the last 2 modified files exist.
4.  **Briefing**: Provide a concise "Session Briefing" to the user:
    -   "Welcome back! Last we worked on [Active Objective]."
    -   "Pending tasks: [Task List]."
    -   "Shall we pick up with [Task 1]?"
