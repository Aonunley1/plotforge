"""
Test script for Line Plot Annotations
Tests annotation functionality with manual and automatic modes
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from plotforge.config import (
    LinePlotConfig, AnnotationsConfig, AnnotationConfig,
    StatisticalOverlayConfig
)
from plotforge.engine import LinePlotEngine

# Create output directory
output_dir = Path(__file__).parent / "output" / "annotations"
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Line Plot Annotation Test Suite")
print(f"Output directory: {output_dir}")
print("=" * 60)

# Test 1: Manual Annotations
print("\n📊 Test 1: Manual Annotations")
print("-" * 60)

np.random.seed(42)
x = np.linspace(0, 10, 50)
df1 = pd.DataFrame({
    'X': x,
    'Y': np.sin(x) * 3 + 5
})

config1 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 1: Manual Annotations',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    overlays=StatisticalOverlayConfig(
        annotations=AnnotationsConfig(
            enabled=True,
            annotations=[
                AnnotationConfig(
                    x=1.57,  # π/2
                    y=8.0,
                    text="Peak at π/2",
                    fontsize=11,
                    color="darkred",
                    arrow=True,
                    bbox=True
                ),
                AnnotationConfig(
                    x=4.71,  # 3π/2
                    y=2.0,
                    text="Trough at 3π/2",
                    fontsize=11,
                    color="darkblue",
                    arrow=True,
                    bbox=True,
                    xytext_offset=(10, -30)
                ),
                AnnotationConfig(
                    x=7.85,  # 5π/2
                    y=8.0,
                    text="Another Peak",
                    fontsize=10,
                    color="darkgreen",
                    arrow=True,
                    bbox=True
                )
            ]
        )
    )
)

engine = LinePlotEngine()
result1 = engine.execute(df1, config1)
output_path1 = output_dir / 'test1_manual_annotations.png'
result1.figure.savefig(output_path1, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path1.name}")
print(f"   Manual annotations: 3")

# Test 2: Automatic Annotations (Peaks and Troughs)
print("\n📊 Test 2: Auto Annotations (Peaks & Troughs)")
print("-" * 60)

df2 = pd.DataFrame({
    'X': x,
    'Y': np.sin(x) * 2 + np.cos(x * 2) + 5
})

config2 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 2: Auto-Annotate Peaks and Troughs',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    overlays=StatisticalOverlayConfig(
        annotations=AnnotationsConfig(
            enabled=True,
            annotate_peaks=True,
            annotate_troughs=True,
            auto_fontsize=9,
            auto_color="purple",
            auto_arrow=True,
            auto_bbox=True
        )
    )
)

result2 = engine.execute(df2, config2)
output_path2 = output_dir / 'test2_auto_peaks_troughs.png'
result2.figure.savefig(output_path2, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path2.name}")
print(f"   Auto-detected peaks and troughs")

# Test 3: First and Last Point Annotations
print("\n📊 Test 3: First and Last Point Annotations")
print("-" * 60)

df3 = pd.DataFrame({
    'X': x,
    'Y': np.exp(-x/5) * np.sin(x) + 3
})

config3 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 3: Annotate Start and End Points',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=True,
    marker_size=6.0,
    overlays=StatisticalOverlayConfig(
        annotations=AnnotationsConfig(
            enabled=True,
            annotate_first=True,
            annotate_last=True,
            auto_fontsize=10,
            auto_color="darkgreen",
            auto_arrow=True,
            auto_bbox=True
        )
    )
)

result3 = engine.execute(df3, config3)
output_path3 = output_dir / 'test3_first_last.png'
result3.figure.savefig(output_path3, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path3.name}")
print(f"   Annotated first and last points")

# Test 4: Grouped Lines with Auto Annotations
print("\n📊 Test 4: Grouped Lines with Annotations")
print("-" * 60)

x4 = np.linspace(0, 10, 50)
df4 = pd.DataFrame({
    'X': np.concatenate([x4, x4]),
    'Y': np.concatenate([
        np.sin(x4) * 2 + 5,
        np.cos(x4) * 2 + 5
    ]),
    'Group': ['Sin'] * 50 + ['Cos'] * 50
})

config4 = LinePlotConfig(
    x='X',
    y='Y',
    group_by='Group',
    title='Test 4: Grouped Lines with Auto Annotations',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    overlays=StatisticalOverlayConfig(
        annotations=AnnotationsConfig(
            enabled=True,
            annotate_peaks=True,
            auto_fontsize=8,
            auto_arrow=True,
            auto_bbox=True
        )
    )
)

result4 = engine.execute(df4, config4)
output_path4 = output_dir / 'test4_grouped_annotations.png'
result4.figure.savefig(output_path4, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path4.name}")
print(f"   Groups: {df4['Group'].unique().tolist()}")
print(f"   Auto-annotated peaks for each group")

# Test 5: Mixed Manual and Auto Annotations
print("\n📊 Test 5: Mixed Manual + Auto Annotations")
print("-" * 60)

config5 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 5: Manual + Auto Annotations',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    overlays=StatisticalOverlayConfig(
        annotations=AnnotationsConfig(
            enabled=True,
            # Manual annotation
            annotations=[
                AnnotationConfig(
                    x=5.0,
                    y=5.0,
                    text="Midpoint",
                    fontsize=12,
                    color="red",
                    arrow=True,
                    bbox=True,
                    bbox_facecolor="yellow",
                    bbox_alpha=0.7
                )
            ],
            # Auto annotations
            annotate_first=True,
            annotate_last=True,
            auto_fontsize=9,
            auto_color="blue",
            auto_arrow=True,
            auto_bbox=True
        )
    )
)

result5 = engine.execute(df1, config5)
output_path5 = output_dir / 'test5_mixed_annotations.png'
result5.figure.savefig(output_path5, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path5.name}")
print(f"   Manual: 1, Auto: 2 (first + last)")

# Test 6: Custom Styling (No Arrows, No Boxes)
print("\n📊 Test 6: Custom Annotation Styling")
print("-" * 60)

config6 = LinePlotConfig(
    x='X',
    y='Y',
    title='Test 6: Custom Styling (No Arrows/Boxes)',
    x_label='X Values',
    y_label='Y Values',
    linewidth=2.5,
    show_markers=False,
    overlays=StatisticalOverlayConfig(
        annotations=AnnotationsConfig(
            enabled=True,
            annotations=[
                AnnotationConfig(
                    x=3.0,
                    y=7.0,
                    text="Simple Label",
                    fontsize=14,
                    color="darkviolet",
                    arrow=False,  # No arrow
                    bbox=False,   # No box
                    xytext_offset=(15, 15)
                )
            ],
            annotate_peaks=True,
            auto_fontsize=10,
            auto_color="orange",
            auto_arrow=False,  # No arrows
            auto_bbox=False    # No boxes
        )
    )
)

result6 = engine.execute(df1, config6)
output_path6 = output_dir / 'test6_custom_style.png'
result6.figure.savefig(output_path6, dpi=300, bbox_inches='tight')
print(f"✅ Created: {output_path6.name}")
print(f"   No arrows or boxes")

# Summary
print("\n" + "=" * 60)
print("📊 Test Summary")
print("=" * 60)
print("✅ All annotation tests completed successfully!")
print("\nGenerated files:")
print("  1. test1_manual_annotations.png - Manual annotations")
print("  2. test2_auto_peaks_troughs.png - Auto peaks/troughs")
print("  3. test3_first_last.png - First and last points")
print("  4. test4_grouped_annotations.png - Grouped with annotations")
print("  5. test5_mixed_annotations.png - Manual + auto")
print("  6. test6_custom_style.png - Custom styling")
print("\nTotal: 6 test images created")
print("=" * 60)
