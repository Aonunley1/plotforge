# .agent Directory

This directory contains AI agent configuration and workspace-specific rules for PlotForge development.

## Files

### `workspace_rules.md`
Project-specific rules and architecture documentation for PlotForge:
- Project context and tech stack
- Architecture overview
- PyQt5-specific coding standards
- Development workflow
- Validation requirements

**When to reference**: When working on PlotForge features, refactoring, or making architectural decisions.

### `global_rules.md`
General Python coding standards that apply to all projects:
- Type hints and formatting
- Import organization
- Error handling best practices
- AI response standards
- General design principles

**When to reference**: For general Python development guidance across any project.

## Usage

When starting work on PlotForge:
1. AI agents should read `workspace_rules.md` to understand project-specific context
2. Follow `global_rules.md` for general Python best practices
3. Both sets of rules work together to ensure consistent, high-quality code

## Note

This directory is excluded from version control (`.gitignore`) as it contains local development preferences and AI-specific context that may vary between developers.
