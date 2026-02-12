# PlotForge Tests Directory

This directory contains all test files, test data, and test outputs for PlotForge.

---

## 📁 Directory Structure

```
tests/
├── output/                          # Test output files (images, plots)
│   ├── test_line_plot.png
│   ├── test1_grouped_lines.png
│   ├── test2_single_line.png
│   └── ... (13 more test images)
│
├── test_data/                       # Generated test datasets
│   ├── normal_data.csv
│   ├── data_with_nans.csv
│   ├── insufficient_data.csv
│   └── ... (more test data files)
│
├── __pycache__/                     # Python bytecode cache
│
├── generate_test_data.py            # Script to generate test datasets
├── test_optimizations.py            # Unit tests for optimizations
├── test_lineplot.py                 # Basic line plot test
├── test_lineplot_comprehensive.py   # Comprehensive line plot tests
│
├── MANUAL_TESTING_GUIDE.md          # Manual testing procedures
├── TESTING_SUITE_SUMMARY.md         # Testing suite overview
└── README.md                        # This file
```

---

## 🧪 Test Scripts

### **1. generate_test_data.py**
Generates diverse test datasets for testing PlotForge functionality.

**Usage:**
```bash
python tests/generate_test_data.py
```

**Output:** Creates CSV/Excel files in `tests/test_data/`

---

### **2. test_optimizations.py**
Unit tests for PlotForge optimizations (color mapping, caching, error handling).

**Usage:**
```bash
pytest tests/test_optimizations.py
```

**Tests:**
- Color map handling
- Trendline error handling
- Color map caching
- Controller type safety
- Integration tests

---

### **3. test_lineplot.py**
Basic test for line plot functionality.

**Usage:**
```bash
python tests/test_lineplot.py
```

**Output:** Creates `tests/output/test_line_plot.png`

**Tests:**
- Grouped lines (3 groups)
- Markers enabled
- Basic configuration

---

### **4. test_lineplot_comprehensive.py**
Comprehensive test suite for all line plot features.

**Usage:**
```bash
python tests/test_lineplot_comprehensive.py
```

**Output:** Creates 13 PNG files in `tests/output/`

**Tests:**
- Grouped lines with markers
- Single line (no grouping)
- Different line styles (solid, dashed, dotted, dash-dot)
- Fill between line and x-axis
- Different marker styles (o, s, ^, D, v)
- Custom color palettes

---

## 📊 Test Output

All test outputs (images, plots) are saved to `tests/output/`.

### **Line Plot Test Images:**
- `test_line_plot.png` - Basic grouped line plot
- `test1_grouped_lines.png` - 3 groups with markers
- `test2_single_line.png` - Sine wave
- `test3_style_*.png` - Line style variations (4 files)
- `test4_fill_between.png` - Fill area under curve
- `test5_marker_*.png` - Marker style variations (5 files)
- `test6_custom_palette.png` - Custom color palette

**Total:** 14 test images

---

## 📝 Test Data

Test data files are stored in `tests/test_data/` and include:

- `normal_data.csv` - Normal operation data
- `data_with_nans.csv` - Data with missing values
- `insufficient_data.csv` - Minimal data points
- `collinear_data.csv` - Collinear features
- `multi_group_data.csv` - Multiple groups
- `excel_multisheet.xlsx` - Multi-sheet Excel file
- `large_dataset.csv` - Performance testing data
- `polynomial_data.csv` - Polynomial relationships

---

## 🚀 Running Tests

### **Run All Unit Tests:**
```bash
pytest tests/
```

### **Run Specific Test File:**
```bash
pytest tests/test_optimizations.py
```

### **Run Line Plot Tests:**
```bash
# Basic test
python tests/test_lineplot.py

# Comprehensive test
python tests/test_lineplot_comprehensive.py
```

### **Generate Test Data:**
```bash
python tests/generate_test_data.py
```

---

## 📋 Test Coverage

### **Unit Tests:**
- ✅ Color map generation
- ✅ Error handling (NaNs, insufficient data, collinearity)
- ✅ Performance optimizations (caching)
- ✅ Type safety
- ✅ Integration tests

### **Line Plot Tests:**
- ✅ Single and grouped lines
- ✅ Markers (toggle, styles)
- ✅ Line styles (solid, dashed, dotted, dash-dot)
- ✅ Fill between
- ✅ Custom palettes
- ✅ Data sorting
- ✅ Color mapping

### **Manual Tests:**
- ✅ GUI functionality
- ✅ Edge cases
- ✅ Export/save features
- ✅ User workflows

---

## 🔍 Test Guidelines

### **Adding New Tests:**

1. **Create test script** in `tests/`
2. **Save outputs** to `tests/output/`
3. **Use test data** from `tests/test_data/`
4. **Add path setup** for imports:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   ```

### **Test Script Template:**
```python
"""
Test script for [feature name]
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from plotforge.config import [ConfigClass]
from plotforge.engine import [EngineClass]

# Create output directory
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)

# Your test code here
# ...

# Save output
output_path = output_dir / 'test_output.png'
result.figure.savefig(output_path, dpi=300, bbox_inches='tight')
```

---

## 📁 .gitignore

The `tests/` directory is listed in `.gitignore`, so test data and outputs are not committed to the repository. This keeps the repository clean and focused on source code.

**Ignored:**
- `tests/` (entire directory)
- `tests/output/` (test outputs)
- `tests/test_data/` (test datasets)
- `tests/__pycache__/` (Python cache)

---

## ✅ Test Status

| Test Suite | Status | Files | Coverage |
|------------|--------|-------|----------|
| **Unit Tests** | ✅ PASSING | 1 | Optimizations, error handling |
| **Line Plot Tests** | ✅ PASSING | 2 | All line plot features |
| **Manual Tests** | ✅ DOCUMENTED | 1 | GUI workflows |
| **Test Data** | ✅ GENERATED | 8 | Diverse scenarios |

---

## 📝 Documentation

- **MANUAL_TESTING_GUIDE.md** - Step-by-step manual testing procedures
- **TESTING_SUITE_SUMMARY.md** - Overview of all testing phases
- **README.md** - This file

---

## 🎯 Next Steps

1. Add more unit tests for new plot types (bar, box, violin, heatmap)
2. Add integration tests for GUI components
3. Add performance benchmarks
4. Add regression tests

---

**Last Updated:** 2026-02-12  
**Test Coverage:** Optimizations, Line Plots  
**Total Test Files:** 4 scripts  
**Total Test Outputs:** 14 images
