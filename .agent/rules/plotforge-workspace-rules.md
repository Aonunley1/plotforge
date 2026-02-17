---
trigger: always_on
---

# PlotForge Workspace Rules

## 🎯 PROJECT CONTEXT
**Project Name**: PlotForge  
**Description**: Desktop GUI application for generating publication-quality scientific plots.  
**Stack**: Python 3.10+, PyQt5, Pandas, Seaborn, Matplotlib, Statsmodels.  
**IDE**: PyCharm with MCP server integration.

---

## 🏗️ ARCHITECTURE OVERVIEW

### Core Pattern
- **MVC Architecture**: Separate data logic (`Pandas`), plotting logic (`engine.py`), and view logic (`gui/`).
- **Template Method**: Engines must inherit from `BasePlotEngine` and implement `draw_core()`.
- **Dataclass Configs**: All plot parameters are passed via dataclasses in `config.py`.

### File Structure
```
plotforge/
├── config.py          # Dataclass configuration models
├── engine.py          # Base and specialized plot engines
├── main.py            # App entry point
└── gui/               # PyQt5 GUI Components
    ├── controller.py       # Coordinates Config -> Engine
    ├── config_panel.py     # Main sidebar (to be modularized)
    ├── plot_canvas.py      # Matplotlib integration
    └── artifact_table.py   # Statistical output display
```

---

## 🎨 UI & UX STANDARDS (PREMIUM AESTHETICS)
- **Responsive Layouts**: Use `QLayout` managers exclusively.
- **Modern Styling**: Use standardized color palettes from the Seaborn/Matplotlib themes.
- **Collapsible UI**: Preserve and use the `CollapsibleBox` pattern for dense configuration forms.
- **User Feedback**: provide status updates in the `statusBar` for all long-running operations.

---

## ⚙️ PROJECT-SPECIFIC CONSTRAINTS
1. **Data Safety**: No in-place modification of user DataFrames. Use copies.
2. **Engine Preservation**: When adding new overlays, ensure they are implemented in the `BasePlotEngine` if they apply to multiple plot types.
3. **GUI Refactor**: The next major goal is splitting `config_panel.py` into a modular `ConfigOrchestrator` system.

---

## 🛠️ TEST ORGANIZATION
- **Dedicated Outputs**: All tests must save to `tests/output/<test_name>/`.
- **Git Ignore**: The `tests/` directory is strictly for local development and is ignored by Git.

---

## ✅ VALIDATION CHECKLIST
- [ ] Check `mcp_pycharm...get_file_problems` after every sidebar or engine change.
- [ ] Ensure all new GUI widgets are added to layouts, never absolutely positioned.
- [ ] Verify that `build_config()` in the sidebar matches the current `dataclass` structure.
