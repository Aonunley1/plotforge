"""
Test script for LinePlot functionality
"""
import pandas as pd
import numpy as np
from plotforge.config import LinePlotConfig, StyleConfig, AxesConfig, LegendConfig, SaveConfig
from plotforge.engine import LinePlotEngine

# Create test data
np.random.seed(42)
x = np.linspace(0, 10, 50)

# Create grouped data
df = pd.DataFrame({
    'X': np.concatenate([x, x, x]),
    'Y': np.concatenate([
        2 * x + np.random.normal(0, 1, 50),  # Group A
        3 * x + 5 + np.random.normal(0, 1.5, 50),  # Group B
        1.5 * x - 2 + np.random.normal(0, 0.8, 50)  # Group C
    ]),
    'Group': ['A'] * 50 + ['B'] * 50 + ['C'] * 50
})

# Create line plot config
config = LinePlotConfig(
    x='X',
    y='Y',
    group_by='Group',
    title='Test Line Plot',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    linestyle='-',
    show_markers=True,
    marker_size=6.0,
    marker_style='o',
    alpha=0.9
)

# Create engine and execute
engine = LinePlotEngine()
result = engine.execute(df, config)

# Save the plot
result.figure.savefig('test_line_plot.png', dpi=300, bbox_inches='tight')
print("✅ Line plot created successfully!")
print(f"   Saved to: test_line_plot.png")
print(f"   Warnings: {result.warnings}")
print(f"   Artifacts: {list(result.artifacts.keys())}")
