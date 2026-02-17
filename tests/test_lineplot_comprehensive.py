"""
Comprehensive test suite for LinePlot functionality
Tests various features and configurations
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from plotforge.config import LinePlotConfig, StyleConfig, AxesConfig, LegendConfig
from plotforge.engine import LinePlotEngine

# Create output directory if it doesn't exist
output_dir = Path(__file__).parent / "output" / "lineplot_comprehensive"
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("PlotForge Line Plot Test Suite")
print(f"Output directory: {output_dir}")
print("=" * 60)

# Test 1: Basic grouped line plot with markers
print("\n📊 Test 1: Grouped Lines with Markers")
print("-" * 60)

np.random.seed(42)
x = np.linspace(0, 10, 50)

df1 = pd.DataFrame({
    'X': np.concatenate([x, x, x]),
    'Y': np.concatenate([
        2 * x + np.random.normal(0, 1, 50),
        3 * x + 5 + np.random.normal(0, 1.5, 50),
        1.5 * x - 2 + np.random.normal(0, 0.8, 50)
    ]),
    'Group': ['A'] * 50 + ['B'] * 50 + ['C'] * 50
})

config1 = LinePlotConfig(
    x='X',
    y='Y',
    group_by='Group',
    title='Test 1: Grouped Lines with Markers',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=True,
    marker_size=6.0,
    marker_style='o'
)

engine = LinePlotEngine()
result1 = engine.execute(df1, config1)
result1.figure.savefig(output_dir / 'test1_grouped_lines.png', dpi=300, bbox_inches='tight')
print("✅ Created: test1_grouped_lines.png")
print(f"   Groups: {df1['Group'].unique().tolist()}")
print(f"   Data points per group: {len(df1) // 3}")

# Test 2: Single line without markers
print("\n📊 Test 2: Single Line (No Grouping, No Markers)")
print("-" * 60)

x2 = np.linspace(0, 2*np.pi, 100)
df2 = pd.DataFrame({
    'X': x2,
    'Y': np.sin(x2)
})

config2 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 2: Sine Wave',
    x_label='Angle (radians)',
    y_label='sin(x)',
    linewidth=3.0,
    linestyle='-',
    show_markers=False,
    alpha=0.9
)

result2 = engine.execute(df2, config2)
result2.figure.savefig(output_dir / 'test2_single_line.png', dpi=300, bbox_inches='tight')
print("✅ Created: test2_single_line.png")
print(f"   Data points: {len(df2)}")
print(f"   Line style: Solid, no markers")

# Test 3: Different line styles
print("\n📊 Test 3: Different Line Styles")
print("-" * 60)

x3 = np.linspace(0, 10, 30)
df3 = pd.DataFrame({
    'X': np.concatenate([x3, x3, x3, x3]),
    'Y': np.concatenate([
        x3 + 2,
        x3 + 4,
        x3 + 6,
        x3 + 8
    ]),
    'Style': ['Solid'] * 30 + ['Dashed'] * 30 + ['Dotted'] * 30 + ['Dash-Dot'] * 30
})

# Note: Currently linestyle is global, but we can test different plots
for style_name, style_code in [('Solid', '-'), ('Dashed', '--'), ('Dotted', ':'), ('Dash-Dot', '-.')]:
    df_subset = df3[df3['Style'] == style_name]
    config = LinePlotConfig(
        x='X',
        y='Y',
        title=f'Line Style: {style_name}',
        x_label='X',
        y_label='Y',
        linewidth=2.5,
        linestyle=style_code,
        show_markers=True,
        marker_size=5.0
    )
    result = engine.execute(df_subset, config)
    filename = f'test3_style_{style_name.lower()}.png'
    result.figure.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
    print(f"✅ Created: {filename} (style: {style_code})")

# Test 4: Fill between
print("\n📊 Test 4: Fill Between Line and X-Axis")
print("-" * 60)

x4 = np.linspace(0, 10, 50)
df4 = pd.DataFrame({
    'X': x4,
    'Y': np.sin(x4) * np.exp(-x4/10) + 2
})

config4 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 4: Fill Between',
    x_label='X',
    y_label='Y',
    linewidth=2.0,
    show_markers=False,
    fill_between=True,
    fill_alpha=0.3
)

result4 = engine.execute(df4, config4)
result4.figure.savefig(output_dir / 'test4_fill_between.png', dpi=300, bbox_inches='tight')
print("✅ Created: test4_fill_between.png")
print(f"   Fill alpha: {config4.fill_alpha}")

# Test 5: Multiple lines with different markers
print("\n📊 Test 5: Different Marker Styles")
print("-" * 60)

x5 = np.linspace(0, 10, 20)
marker_styles = ['o', 's', '^', 'D', 'v']

for i, marker in enumerate(marker_styles):
    df5 = pd.DataFrame({
        'X': x5,
        'Y': x5 + i * 2
    })
    
    config5 = LinePlotConfig(
        x='X',
        y='Y',
        title=f'Marker Style: {marker}',
        x_label='X',
        y_label='Y',
        linewidth=2.0,
        show_markers=True,
        marker_style=marker,
        marker_size=8.0
    )
    
    result5 = engine.execute(df5, config5)
    filename = f'test5_marker_{marker}.png'
    result5.figure.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
    print(f"✅ Created: {filename} (marker: {marker})")

# Test 6: Color palette test
print("\n📊 Test 6: Custom Color Palette")
print("-" * 60)

x6 = np.linspace(0, 10, 40)
df6 = pd.DataFrame({
    'X': np.concatenate([x6, x6, x6, x6]),
    'Y': np.concatenate([
        x6,
        x6 + 3,
        x6 + 6,
        x6 + 9
    ]),
    'Group': ['Alpha'] * 40 + ['Beta'] * 40 + ['Gamma'] * 40 + ['Delta'] * 40
})

config6 = LinePlotConfig(
    x='X',
    y='Y',
    group_by='Group',
    title='Test 6: Custom Palette',
    x_label='X',
    y_label='Y',
    linewidth=2.5,
    show_markers=True,
    marker_size=5.0,
    palette=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']  # Custom colors
)

result6 = engine.execute(df6, config6)
result6.figure.savefig(output_dir / 'test6_custom_palette.png', dpi=300, bbox_inches='tight')
print("✅ Created: test6_custom_palette.png")
print(f"   Groups: {df6['Group'].unique().tolist()}")
print(f"   Custom colors: {config6.palette}")

# Summary
print("\n" + "=" * 60)
print("📊 Test Summary")
print("=" * 60)
print("✅ All tests completed successfully!")
print("\nGenerated files:")
print("  1. test1_grouped_lines.png - Grouped lines with markers")
print("  2. test2_single_line.png - Single sine wave")
print("  3. test3_style_*.png - Different line styles (4 files)")
print("  4. test4_fill_between.png - Fill between line and axis")
print("  5. test5_marker_*.png - Different marker styles (5 files)")
print("  6. test6_custom_palette.png - Custom color palette")
print("\nTotal: 13 test images created")
print("=" * 60)
