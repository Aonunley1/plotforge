"""
PlotForge Design System & Stylesheets (QSS)
Defines the premium look and feel for the application.
"""

# Color Palette
COLORS = {
    "primary": "#0078d4",      # Windows-style accent blue
    "primary_hover": "#005a9e",
    "bg_main": "#ffffff",
    "bg_sidebar": "#f3f3f3",
    "border_light": "#dcdcdc",
    "text_main": "#333333",
    "text_muted": "#666666",
    "success": "#107c10",
    "error": "#a4262c",
}

# Global Stylesheet
MAIN_STYLESHEET = f"""
    QMainWindow {{
        background-color: {COLORS["bg_main"]};
    }}

    /* Global Typography */
    QWidget {{
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        font-size: 10pt;
        color: {COLORS["text_main"]};
    }}

    /* Sidebar and Header Styling */
    QFrame#sidebarHeader {{
        background-color: {COLORS["bg_sidebar"]};
        border-bottom: 1px solid {COLORS["border_light"]};
    }}

    QLabel#headerLabel {{
        font-weight: bold;
        font-size: 11pt;
    }}

    /* Scroll Area Styling */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    /* Custom SpinBoxes, ComboBoxes, and LineEdits */
    QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {{
        border: 1px solid {COLORS["border_light"]};
        border-radius: 4px;
        padding: 5px;
        background-color: white;
    }}

    QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
        border: 1px solid {COLORS["primary"]};
    }}

    QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 2px solid {COLORS["primary"]};
    }}

    /* Dropdown Arrow */
    QComboBox::drop-down {{
        border: none;
    }}

    /* Group Box / Section Containers */
    QWidget#sectionContent {{
        border: 1px solid {COLORS["border_light"]};
        border-radius: 6px;
        background-color: #fafafa;
    }}

    /* Premium Buttons */
    QPushButton {{
        background-color: {COLORS["primary"]};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }}

    QPushButton:hover {{
        background-color: {COLORS["primary_hover"]};
    }}

    QPushButton:pressed {{
        background-color: #004578;
    }}

    QPushButton:disabled {{
        background-color: #cccccc;
        color: #666666;
    }}

    /* Checkbox Styling */
    QCheckBox {{
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {COLORS["border_light"]};
        border-radius: 3px;
    }}

    QCheckBox::indicator:checked {{
        background-color: {COLORS["primary"]};
        border: 1px solid {COLORS["primary"]};
        /* Note: In a real app we'd use an image for the checkmark */
    }}

    /* Tool Buttons (Collapsible Box Headers) */
    QToolButton {{
        border: none;
        padding: 8px;
        font-weight: 600;
        text-align: left;
        color: #444;
    }}

    QToolButton:hover {{
        background-color: #e0e0e0;
        border-radius: 4px;
    }}
"""
