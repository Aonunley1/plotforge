"""
Test script for Line Plot Confidence Intervals
Tests CI functionality with various configurations
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from plotforge.config import LinePlotConfig, LineCIConfig, StatisticalOverlayConfig
from plotforge.engine import LinePlotEngine

# Create output directory
output_dir = Path(__file__).parent / "output" / "line_ci"
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Line Plot Confidence Interval Test Suite")
print(f"Output directory: {output_dir}")
print("=" * 60)

# Test 1: Basic CI with Standard Error Method
print("\n📊 Test 1: Standard Error CI (95%)")
print("-" * 60)

np.random.seed(42)
x = np.linspace(0, 10, 50)

# Create data with multiple observations per X value
x_repeated = np.repeat(x, 5)  # 5 observations per X
df1 = pd.DataFrame({
    'X': x_repeated,
    'Y': 2 * x_repeated + np.random.normal(0, 1.5, len(x_repeated))
})

config1 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 1: Standard Error CI (95%)',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    overlays=StatisticalOverlayConfig(
        line_ci=LineCIConfig(
            enabled=True,
            level=0.95,
            method='stderr',
            alpha=0.2
        )
    )
)

engine = LinePlotEngine()
result1 = engine.execute(df1, config1)
output_path1 = output_dir / 'test1_stderr_ci_95.png'
result1.figure.savefig(output_path1, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path1.name}")
print(f"   Method: Standard Error")
print(f"   Confidence Level: 95%")
print(f"   Observations per X: 5")

# Test 2: Different Confidence Levels
print("\n📊 Test 2: Different Confidence Levels")
print("-" * 60)

# 90% CI
config2a = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 2a: 90% Confidence Interval',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    overlays=StatisticalOverlayConfig(
        line_ci=LineCIConfig(
            enabled=True,
            level=0.90,
            method='stderr',
            alpha=0.25
        )
    )
)

result2a = engine.execute(df1, config2a)
output_path2a = output_dir / 'test2a_ci_90.png'
result2a.figure.savefig(output_path2a, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path2a.name} (90% CI)")

# 99% CI
config2b = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 2b: 99% Confidence Interval',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    overlays=StatisticalOverlayConfig(
        line_ci=LineCIConfig(
            enabled=True,
            level=0.99,
            method='stderr',
            alpha=0.15
        )
    )
)

result2b = engine.execute(df1, config2b)
output_path2b = output_dir / 'test2b_ci_99.png'
result2b.figure.savefig(output_path2b, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path2b.name} (99% CI)")

# Test 3: Bootstrap Method
print("\n📊 Test 3: Bootstrap CI")
print("-" * 60)

config3 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 3: Bootstrap CI (95%, 1000 iterations)',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    overlays=StatisticalOverlayConfig(
        line_ci=LineCIConfig(
            enabled=True,
            level=0.95,
            method='bootstrap',
            n_bootstrap=1000,
            alpha=0.2
        )
    )
)

result3 = engine.execute(df1, config3)
output_path3 = output_dir / 'test3_bootstrap_ci.png'
result3.figure.savefig(output_path3, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path3.name}")
print(f"   Method: Bootstrap")
print(f"   Bootstrap iterations: 1000")

# Test 4: Grouped Lines with CI
print("\n📊 Test 4: Grouped Lines with CI")
print("-" * 60)

x4 = np.linspace(0, 10, 30)
x4_repeated = np.repeat(x4, 3)  # 3 observations per X

df4 = pd.DataFrame({
    'X': np.concatenate([x4_repeated, x4_repeated, x4_repeated]),
    'Y': np.concatenate([
        2 * x4_repeated + np.random.normal(0, 1, len(x4_repeated)),
        3 * x4_repeated + 5 + np.random.normal(0, 1.2, len(x4_repeated)),
        1.5 * x4_repeated - 2 + np.random.normal(0, 0.8, len(x4_repeated))
    ]),
    'Group': ['A'] * len(x4_repeated) + ['B'] * len(x4_repeated) + ['C'] * len(x4_repeated)
})

config4 = LinePlotConfig(
    x='X',
    y='Y',
    group_by='Group',
    title='Test 4: Grouped Lines with CI',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    overlays=StatisticalOverlayConfig(
        line_ci=LineCIConfig(
            enabled=True,
            level=0.95,
            method='stderr',
            alpha=0.15
        )
    )
)

result4 = engine.execute(df4, config4)
output_path4 = output_dir / 'test4_grouped_ci.png'
result4.figure.savefig(output_path4, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path4.name}")
print(f"   Groups: {df4['Group'].unique().tolist()}")
print(f"   CI for each group")

# Test 5: CI with Markers
print("\n📊 Test 5: CI with Markers")
print("-" * 60)

config5 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 5: CI with Markers',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=True,
    marker_size=6.0,
    marker_style='o',
    overlays=StatisticalOverlayConfig(
        line_ci=LineCIConfig(
            enabled=True,
            level=0.95,
            method='stderr',
            alpha=0.2
        )
    )
)

result5 = engine.execute(df1, config5)
output_path5 = output_dir / 'test5_ci_with_markers.png'
result5.figure.savefig(output_path5, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path5.name}")
print(f"   Markers: Enabled")

# Test 6: CI with Custom Styling
print("\n📊 Test 6: Custom CI Styling")
print("-" * 60)

config6 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 6: Custom CI Color and Alpha',
    x_label='X Values',
    y_label='Y Values',
    linewidth=3.0,
    show_markers=False,
    palette=['darkblue'],
    overlays=StatisticalOverlayConfig(
        line_ci=LineCIConfig(
            enabled=True,
            level=0.95,
            method='stderr',
            alpha=0.4,  # More opaque
            color='lightblue'  # Custom color
        )
    )
)

result6 = engine.execute(df1, config6)
output_path6 = output_dir / 'test6_custom_ci_style.png'
result6.figure.savefig(output_path6, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path6.name}")
print(f"   Custom CI color: lightblue")
print(f"   Custom alpha: 0.4")

# Summary
print("\n" + "=" * 60)
print("📊 Test Summary")
print("=" * 60)
print("✅ All confidence interval tests completed successfully!")
print("\nGenerated files:")
print("  1. test1_stderr_ci_95.png - Standard error CI (95%)")
print("  2. test2a_ci_90.png - 90% confidence interval")
print("  3. test2b_ci_99.png - 99% confidence interval")
print("  4. test3_bootstrap_ci.png - Bootstrap method")
print("  5. test4_grouped_ci.png - Grouped lines with CI")
print("  6. test5_ci_with_markers.png - CI with markers")
print("  7. test6_custom_ci_style.png - Custom styling")
print("\nTotal: 7 test images created")
print("=" * 60)
