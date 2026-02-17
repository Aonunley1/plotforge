---
trigger: always_on
---

# Global AI Coding Rules

These rules apply to ALL projects handled by this AI.

---

## 🏗️ CODING STANDARDS

### Type Hints
- Always use strict type hints for function signatures.
- Example: `def process_data(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:`
- Use `Optional[T]` for nullable types and `Union[T1, T2]` for multiple possible types.

### Code Formatting
- Use Python black formatting style.
- Line length: 100 characters.
- Follow PEP 8 conventions strictly.

### Import Organization
Group imports in this order:
1. Standard Library imports
2. Third-party imports
3. Local application imports

### Error Handling
- Use specific exception types (avoid bare `except:`).
- Provide meaningful error messages and log errors for debugging.
- Don't silence errors without handling them.

---

## 🤖 AI RESPONSE STANDARDS

### Code Quality
- **NO PLACEHOLDERS**: Never use `// ... rest of code ...` or `<<< content truncated >>>`.
- **COMPLETE CODE**: Always provide complete, working code within context.
- **NO LAZY REFACTORING**: Don't suggest "just add this line" without context.

### Communication
- **EXPLAIN ARCHITECTURE**: Explain architecture changes BEFORE implementing.
- **CONFIRM BEFORE EDITING**: Get user confirmation before making any file changes.
- **MARSDOWN FORMATTING**: Use markdown for explanations and code blocks with language tags.

---

## 🔄 CONTEXT REFRESH PROTOCOL

### Triggers
- **Refersh**: Suggest `/refresh` when the conversation exceeds 15-20 messages OR after major architectural changes.
- **Onboard**: The AI MUST run `/onboard` (or equivalent read actions) as the FIRST step in every new session.
- **Status**: Suggest `/status` if a command fails (build/test) OR if the conversation objective feels disconnected from the "Pending Tasks".

### Procedures
- **Save State**: Always update `.context/sync_state.md` at the end of a milestone.
- **Audit**: Use `/status` to verify that the "Save State" and "Live Code" have not drifted.

---

## 🛠️ TOOL USAGE & VALIDATION

### MCP Integration
- Prefer `mcp_pycharm` tools over generic commands for reading/editing files.
- **VALIDATE ALWAYS**: After every edit, run `mcp_pycharm-native_get_file_problems` to ensure no syntax/lint errors were introduced.
- **BUILD CHECK**: Run `build_project` after significant changes to verify compilation.

---

## ❌ ANTI-PATTERNS TO AVOID
- ❌ Global mutable state.
- ❌ Circular imports.
- ❌ Deep nesting (> 3 levels).
- ❌ Mixing business logic with UI code.
