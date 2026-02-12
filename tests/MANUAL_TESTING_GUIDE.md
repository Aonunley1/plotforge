# PlotForge Manual Testing Guide

## Overview
This guide walks you through manually testing PlotForge to verify the optimization changes.

---

## Test Scenarios

### ✅ Scenario 1: Normal Operation (Baseline)
**File**: `tests/test_data/01_normal_data.csv`

**Steps**:
1. Launch PlotForge
2. File → Load Data → Select `01_normal_data.csv`
3. Configure plot:
   - X Column: `X`
   - Y Column: `Y`
   - Group By: `Group`
4. Enable Trendline
5. Click "Update Plot"

**Expected Result**:
- Scatter plot with 2 groups (A and B) in different colors
- Trendline for each group matching the scatter colors
- Artifact table shows trendline statistics (slope, R², etc.)

---

### ✅ Scenario 2: NaN Handling
**File**: `tests/test_data/02_nan_values.csv`

**Steps**:
1. Load `02_nan_values.csv`
2. Configure:
   - X: `X`
   - Y: `Y`
   - Group By: `Group`
3. Enable Trendline
4. Update Plot

**Expected Result**:
- Plot renders without errors
- NaN values are excluded from plot
- Only groups A and B appear (no NaN group)
- Colors are consistent

**Verification**:
- ✅ No crashes
- ✅ Warning messages handled gracefully
- ✅ Color map excludes NaN

---

### ✅ Scenario 3: Insufficient Data (Error Handling Test)
**File**: `tests/test_data/03_insufficient_data.csv`

**Steps**:
1. Load `03_insufficient_data.csv`
2. Configure:
   - X: `X`
   - Y: `Y`
   - Group By: `Group`
3. Enable Trendline
4. Update Plot

**Expected Result**:
- Plot renders successfully
- Group A has trendline (5 points)
- Group B has NO trendline (only 1 point - insufficient)
- Console shows warning: "Warning: Trendline fitting failed for group 'B'"
- Application does NOT crash

**Verification**:
- ✅ Error handling works
- ✅ Application continues gracefully
- ✅ Only valid trendlines are shown

---

### ✅ Scenario 4: Color Consistency (Optimization Verification)
**File**: `tests/test_data/05_multigroup_data.csv`

**Steps**:
1. Load `05_multigroup_data.csv`
2. Configure:
   - X: `X`
   - Y: `Y`
   - Group By: `Group`
3. Enable BOTH:
   - Trendline
   - KDE Overlay
4. Update Plot

**Expected Result**:
- 4 groups (Alpha, Beta, Gamma, Delta) each with unique color
- Scatter points, trendlines, and KDE contours ALL use matching colors per group
- No color mismatches

**Verification**:
- ✅ Color map is cached (single generation)
- ✅ All overlays use consistent colors
- ✅ Performance is good (no lag)

---

### ✅ Scenario 5: Excel Multi-Sheet
**File**: `tests/test_data/06_multisheet_data.xlsx`

**Steps**:
1. Load `06_multisheet_data.xlsx`
2. Sheet selection dialog appears
3. Select "Experiment_A"
4. Configure:
   - X: `Time`
   - Y: `Temperature`
   - Group By: `Condition`
5. Update Plot

**Expected Result**:
- Sheet selection works
- Plot renders with 2 groups (Control, Treatment)

---

### ✅ Scenario 6: Performance Test
**File**: `tests/test_data/07_large_dataset.csv`

**Steps**:
1. Load `07_large_dataset.csv` (1000 points)
2. Configure:
   - X: `X`
   - Y: `Y`
   - Group By: `Group`
3. Enable Trendline
4. Update Plot

**Expected Result**:
- Plot renders in < 3 seconds
- 5 groups with trendlines
- No performance issues

**Verification**:
- ✅ Color map caching improves performance
- ✅ No lag or freezing

---

### ✅ Scenario 7: Polynomial Fit
**File**: `tests/test_data/08_polynomial_data.csv`

**Steps**:
1. Load `08_polynomial_data.csv`
2. Configure:
   - X: `X`
   - Y: `Y`
3. Enable Trendline
4. Set Polynomial Order: 2 (quadratic)
5. Update Plot

**Expected Result**:
- Quadratic trendline fits the curved data
- R² is high (> 0.9)

---

## Optimization-Specific Tests

### Test A: Type Hints (Code Quality)
**Verification**: Run mypy or check IDE warnings
```bash
# Should show no type errors in main_window.py lines 32-33
```

### Test B: Error Handling
**Scenario 3** above specifically tests this.

### Test C: Color Map Caching
**Scenario 4** above tests this. You can also:
1. Add a print statement in `engine.py` line 213
2. Verify it's called only once per plot update

### Test D: Constants Usage
**Verification**: Check `main_window.py` lines 28-29
- Constants are defined
- Used in lines 196-197

---

## Export and Save Tests

### Test: Artifact Export
1. Generate any plot with trendlines
2. Verify artifact table shows statistics
3. Copy data from table (Ctrl+C)
4. Paste into Excel - should work

### Test: Figure Save
1. Generate any plot
2. File → Save Figure
3. Save as PNG
4. Verify image quality

---

## Checklist

After running all tests, verify:

- [ ] No crashes or unhandled exceptions
- [ ] NaN values handled gracefully
- [ ] Insufficient data doesn't crash trendline fitting
- [ ] Colors are consistent across scatter/trendline/KDE
- [ ] Excel multi-sheet selection works
- [ ] Large datasets render quickly
- [ ] Polynomial fits work correctly
- [ ] Artifacts export correctly
- [ ] Figures save correctly

---

## Notes

- All test data is in `tests/test_data/`
- Console output may show warnings - this is expected for edge cases
- Performance should be noticeably better with color map caching

---

## Reporting Issues

If you find any issues:
1. Note the test scenario
2. Copy error messages from console
3. Note expected vs actual behavior
4. Save the configuration that caused the issue
