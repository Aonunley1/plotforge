"""
Test script for Line Plot Error Bars
Tests error bar functionality with various configurations
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from plotforge.config import LinePlotConfig, ErrorBarConfig, StatisticalOverlayConfig
from plotforge.engine import LinePlotEngine

# Create output directory
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)

print("=" * 60)
print("Line Plot Error Bar Test Suite")
print(f"Output directory: {output_dir}")
print("=" * 60)

# Test 1: Y Error Bars with Fixed Values
print("\n📊 Test 1: Fixed Y Error Bars")
print("-" * 60)

np.random.seed(42)
x = np.linspace(0, 10, 20)
df1 = pd.DataFrame({
    'X': x,
    'Y': 2 * x + np.random.normal(0, 1, 20)
})

config1 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 1: Fixed Y Error Bars',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=True,
    marker_size=8.0,
    overlays=StatisticalOverlayConfig(
        error_bars=ErrorBarConfig(
            enabled=True,
            y_error=0.5,  # Fixed error value
            linewidth=1.5,
            capsize=4.0,
            alpha=0.6
        )
    )
)

engine = LinePlotEngine()
result1 = engine.execute(df1, config1)
output_path1 = output_dir / 'test1_fixed_y_error.png'
result1.figure.savefig(output_path1, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path1.name}")
print(f"   Fixed Y error: ±0.5")

# Test 2: Y Error Bars from DataFrame Column
print("\n📊 Test 2: Y Error Bars from Column")
print("-" * 60)

df2 = pd.DataFrame({
    'X': x,
    'Y': 3 * x + 5,
    'Y_Error': np.random.uniform(0.5, 1.5, 20)  # Variable error
})

config2 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 2: Variable Y Error Bars',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=True,
    marker_size=8.0,
    overlays=StatisticalOverlayConfig(
        error_bars=ErrorBarConfig(
            enabled=True,
            y_error_column='Y_Error',  # Column name
            linewidth=1.5,
            capsize=4.0,
            alpha=0.6
        )
    )
)

result2 = engine.execute(df2, config2)
output_path2 = output_dir / 'test2_column_y_error.png'
result2.figure.savefig(output_path2, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path2.name}")
print(f"   Y error from column: 'Y_Error'")

# Test 3: Grouped Lines with Error Bars
print("\n📊 Test 3: Grouped Lines with Error Bars")
print("-" * 60)

x3 = np.linspace(0, 10, 15)
df3 = pd.DataFrame({
    'X': np.concatenate([x3, x3, x3]),
    'Y': np.concatenate([
        2 * x3 + np.random.normal(0, 0.5, 15),
        3 * x3 + 5 + np.random.normal(0, 0.5, 15),
        1.5 * x3 - 2 + np.random.normal(0, 0.5, 15)
    ]),
    'Group': ['A'] * 15 + ['B'] * 15 + ['C'] * 15
})

config3 = LinePlotConfig(
    x='X',
    y='Y',
    group_by='Group',
    title='Test 3: Grouped Lines with Error Bars',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=True,
    marker_size=6.0,
    overlays=StatisticalOverlayConfig(
        error_bars=ErrorBarConfig(
            enabled=True,
            y_error=0.3,  # Fixed error for all groups
            linewidth=1.5,
            capsize=3.0,
            alpha=0.5
        )
    )
)

result3 = engine.execute(df3, config3)
output_path3 = output_dir / 'test3_grouped_error_bars.png'
result3.figure.savefig(output_path3, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path3.name}")
print(f"   Groups: {df3['Group'].unique().tolist()}")
print(f"   Fixed Y error: ±0.3 for all groups")

# Test 4: Both X and Y Error Bars
print("\n📊 Test 4: Both X and Y Error Bars")
print("-" * 60)

df4 = pd.DataFrame({
    'X': x,
    'Y': np.sin(x) * 5,
    'X_Error': np.random.uniform(0.1, 0.3, 20),
    'Y_Error': np.random.uniform(0.2, 0.5, 20)
})

config4 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 4: X and Y Error Bars',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=True,
    marker_size=8.0,
    overlays=StatisticalOverlayConfig(
        error_bars=ErrorBarConfig(
            enabled=True,
            x_error_column='X_Error',
            y_error_column='Y_Error',
            linewidth=1.5,
            capsize=4.0,
            alpha=0.6
        )
    )
)

result4 = engine.execute(df4, config4)
output_path4 = output_dir / 'test4_xy_error_bars.png'
result4.figure.savefig(output_path4, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path4.name}")
print(f"   X error from column: 'X_Error'")
print(f"   Y error from column: 'Y_Error'")

# Test 5: Error Bars with Fill Between
print("\n📊 Test 5: Error Bars + Fill Between")
print("-" * 60)

df5 = pd.DataFrame({
    'X': x,
    'Y': np.exp(-x/5) * np.sin(x) + 3
})

config5 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 5: Error Bars with Fill',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    fill_between=True,
    fill_alpha=0.2,
    overlays=StatisticalOverlayConfig(
        error_bars=ErrorBarConfig(
            enabled=True,
            y_error=0.4,
            linewidth=1.5,
            capsize=3.0,
            alpha=0.6
        )
    )
)

result5 = engine.execute(df5, config5)
output_path5 = output_dir / 'test5_error_bars_fill.png'
result5.figure.savefig(output_path5, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path5.name}")
print(f"   Fill between: Enabled")
print(f"   Y error: ±0.4")

# Test 6: Custom Error Bar Styling
print("\n📊 Test 6: Custom Error Bar Styling")
print("-" * 60)

df6 = pd.DataFrame({
    'X': x,
    'Y': x ** 1.5
})

config6 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 6: Custom Error Bar Style',
    x_label='X Values',
    y_label='Y Values',
    linewidth=3.0,
    show_markers=True,
    marker_size=10.0,
    overlays=StatisticalOverlayConfig(
        error_bars=ErrorBarConfig(
            enabled=True,
            y_error=1.0,
            linewidth=2.5,  # Thick error bars
            capsize=6.0,    # Large caps
            capthick=2.0,   # Thick caps
            alpha=0.8,      # More opaque
            color='red'     # Custom color
        )
    )
)

result6 = engine.execute(df6, config6)
output_path6 = output_dir / 'test6_custom_style.png'
result6.figure.savefig(output_path6, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path6.name}")
print(f"   Custom color: red")
print(f"   Thick error bars (linewidth=2.5)")
print(f"   Large caps (capsize=6.0)")

# Summary
print("\n" + "=" * 60)
print("📊 Test Summary")
print("=" * 60)
print("✅ All error bar tests completed successfully!")
print("\nGenerated files:")
print("  1. test1_fixed_y_error.png - Fixed Y error bars")
print("  2. test2_column_y_error.png - Variable Y error from column")
print("  3. test3_grouped_error_bars.png - Grouped lines with errors")
print("  4. test4_xy_error_bars.png - Both X and Y errors")
print("  5. test5_error_bars_fill.png - Error bars with fill")
print("  6. test6_custom_style.png - Custom error bar styling")
print("\nTotal: 6 test images created")
print("=" * 60)
