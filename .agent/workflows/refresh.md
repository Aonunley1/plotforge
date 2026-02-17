---
description: Summarize project state into .context/sync_state.md for context refresh
---
1.  **Analyze**: Review the conversation history and the current state of the codebase (active branch, last modified files, implemented features).
2.  **Summarize**: Create or update `.context/sync_state.md` with:
    -   **Active Objective**: The primary goal of the current development phase.
    -   **Architecture Status**: Summary of the current project structure and any recent refactors.
    -   **Pending Tasks**: A prioritized list of what needs to be done next.
    -   **Active Bugs**: Any known issues or edge cases being addressed.
    -   **Technical Decisions**: Rationale for major design choices made during the session.
3.  **Confirm**: Notify the user that the state has been synchronized and provide a brief summary of the contents.
4.  **Instructions for Next Session**: Remind the user (and the next AI session) to read `.context/sync_state.md` immediately upon starting.
