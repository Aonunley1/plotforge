"""
Generate comprehensive test datasets for PlotForge testing.

This script creates various CSV and Excel files to test:
- Normal operation
- Edge cases (NaN, insufficient data, singular matrices)
- Multi-group scenarios
- Color mapping consistency
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Create test_data directory
test_data_dir = Path(__file__).parent / "test_data"
test_data_dir.mkdir(parents=True, exist_ok=True)

# Set random seed for reproducibility
np.random.seed(42)


# ============================================================================
# Test Dataset 1: Normal Data - Standard Scatter with Groups
# ============================================================================
def create_normal_data():
    """Standard dataset with two groups, linear relationship + noise"""
    n_points = 50
    
    # Group A: Positive correlation
    x_a = np.linspace(0, 100, n_points // 2)
    y_a = 2 * x_a + 10 + np.random.normal(0, 8, n_points // 2)
    
    # Group B: Different slope
    x_b = np.linspace(0, 100, n_points // 2)
    y_b = 1.5 * x_b + 20 + np.random.normal(0, 6, n_points // 2)
    
    df = pd.DataFrame({
        'X': np.concatenate([x_a, x_b]),
        'Y': np.concatenate([y_a, y_b]),
        'Group': ['A'] * (n_points // 2) + ['B'] * (n_points // 2)
    })
    
    df.to_csv(test_data_dir / "01_normal_data.csv", index=False)
    print("✅ Created: 01_normal_data.csv")
    return df


# ============================================================================
# Test Dataset 2: Edge Case - NaN Values
# ============================================================================
def create_nan_data():
    """Dataset with NaN values in various columns"""
    df = pd.DataFrame({
        'X': [1, 2, 3, np.nan, 5, 6, 7, 8, 9, 10],
        'Y': [2, 4, np.nan, 8, 10, 12, 14, 16, 18, 20],
        'Group': ['A', 'A', 'B', 'B', np.nan, 'A', 'B', 'A', 'B', 'A'],
        'Value': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    })
    
    df.to_csv(test_data_dir / "02_nan_values.csv", index=False)
    print("✅ Created: 02_nan_values.csv")
    return df


# ============================================================================
# Test Dataset 3: Edge Case - Insufficient Data
# ============================================================================
def create_insufficient_data():
    """Dataset where one group has < 2 points (can't fit trendline)"""
    df = pd.DataFrame({
        'X': [1, 2, 3, 4, 5, 100],
        'Y': [2, 4, 6, 8, 10, 50],
        'Group': ['A', 'A', 'A', 'A', 'A', 'B'],  # Group B has only 1 point
        'Category': ['Low', 'Low', 'Medium', 'Medium', 'High', 'High']
    })
    
    df.to_csv(test_data_dir / "03_insufficient_data.csv", index=False)
    print("✅ Created: 03_insufficient_data.csv")
    return df


# ============================================================================
# Test Dataset 4: Edge Case - Perfectly Collinear Data
# ============================================================================
def create_collinear_data():
    """Perfectly collinear data (no noise) - tests numerical stability"""
    x = np.linspace(0, 100, 20)
    y = 2 * x + 5  # Perfect line, no noise
    
    df = pd.DataFrame({
        'X': x,
        'Y': y,
        'Group': ['Perfect'] * 20
    })
    
    df.to_csv(test_data_dir / "04_collinear_data.csv", index=False)
    print("✅ Created: 04_collinear_data.csv")
    return df


# ============================================================================
# Test Dataset 5: Multi-Group with Many Categories
# ============================================================================
def create_multigroup_data():
    """Dataset with 4 groups to test color palette handling"""
    n_per_group = 15
    groups = ['Alpha', 'Beta', 'Gamma', 'Delta']
    
    data = []
    for i, group in enumerate(groups):
        x = np.linspace(0, 100, n_per_group)
        y = (i + 1) * x + (i * 10) + np.random.normal(0, 5, n_per_group)
        
        for j in range(n_per_group):
            data.append({
                'X': x[j],
                'Y': y[j],
                'Group': group,
                'Measurement': f'M{j+1}'
            })
    
    df = pd.DataFrame(data)
    df.to_csv(test_data_dir / "05_multigroup_data.csv", index=False)
    print("✅ Created: 05_multigroup_data.csv")
    return df


# ============================================================================
# Test Dataset 6: Excel Multi-Sheet
# ============================================================================
def create_excel_multisheet():
    """Excel file with multiple sheets to test sheet selection"""
    
    # Sheet 1: Experiment A
    df_exp_a = pd.DataFrame({
        'Time': np.linspace(0, 10, 30),
        'Temperature': 20 + 5 * np.sin(np.linspace(0, 10, 30)) + np.random.normal(0, 0.5, 30),
        'Pressure': 100 + 10 * np.cos(np.linspace(0, 10, 30)) + np.random.normal(0, 1, 30),
        'Condition': ['Control'] * 15 + ['Treatment'] * 15
    })
    
    # Sheet 2: Experiment B
    df_exp_b = pd.DataFrame({
        'Dose': np.array([0, 10, 20, 30, 40, 50] * 5),
        'Response': np.array([5, 15, 30, 50, 70, 85] * 5) + np.random.normal(0, 5, 30),
        'Replicate': [f'R{i}' for i in range(1, 6)] * 6
    })
    
    # Sheet 3: Experiment C
    df_exp_c = pd.DataFrame({
        'X': np.random.uniform(0, 100, 40),
        'Y': np.random.uniform(0, 100, 40),
        'Cluster': np.random.choice(['C1', 'C2', 'C3'], 40)
    })
    
    excel_path = test_data_dir / "06_multisheet_data.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_exp_a.to_excel(writer, sheet_name='Experiment_A', index=False)
        df_exp_b.to_excel(writer, sheet_name='Experiment_B', index=False)
        df_exp_c.to_excel(writer, sheet_name='Experiment_C', index=False)
    
    print("✅ Created: 06_multisheet_data.xlsx (3 sheets)")
    return df_exp_a, df_exp_b, df_exp_c


# ============================================================================
# Test Dataset 7: Large Dataset (Performance Test)
# ============================================================================
def create_large_data():
    """Large dataset to test performance"""
    n_points = 1000
    
    df = pd.DataFrame({
        'X': np.random.uniform(0, 1000, n_points),
        'Y': np.random.uniform(0, 500, n_points),
        'Group': np.random.choice(['G1', 'G2', 'G3', 'G4', 'G5'], n_points),
        'Value': np.random.normal(100, 20, n_points)
    })
    
    df.to_csv(test_data_dir / "07_large_dataset.csv", index=False)
    print("✅ Created: 07_large_dataset.csv (1000 points)")
    return df


# ============================================================================
# Test Dataset 8: Polynomial Relationship
# ============================================================================
def create_polynomial_data():
    """Dataset with quadratic relationship for testing higher-order fits"""
    x = np.linspace(-10, 10, 50)
    y = 0.5 * x**2 - 2 * x + 5 + np.random.normal(0, 3, 50)
    
    df = pd.DataFrame({
        'X': x,
        'Y': y,
        'Type': ['Quadratic'] * 50
    })
    
    df.to_csv(test_data_dir / "08_polynomial_data.csv", index=False)
    print("✅ Created: 08_polynomial_data.csv")
    return df


# ============================================================================
# Main Execution
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Generating PlotForge Test Datasets")
    print("=" * 60)
    print()
    
    create_normal_data()
    create_nan_data()
    create_insufficient_data()
    create_collinear_data()
    create_multigroup_data()
    create_excel_multisheet()
    create_large_data()
    create_polynomial_data()
    
    print()
    print("=" * 60)
    print("✅ All test datasets created successfully!")
    print(f"📁 Location: {test_data_dir.absolute()}")
    print("=" * 60)
    print()
    print("Test Datasets Summary:")
    print("  1. 01_normal_data.csv         - Standard 2-group scatter")
    print("  2. 02_nan_values.csv          - Tests NaN handling")
    print("  3. 03_insufficient_data.csv   - Group with < 2 points")
    print("  4. 04_collinear_data.csv      - Perfect linear data")
    print("  5. 05_multigroup_data.csv     - 4 groups (color palette)")
    print("  6. 06_multisheet_data.xlsx    - Excel with 3 sheets")
    print("  7. 07_large_dataset.csv       - 1000 points (performance)")
    print("  8. 08_polynomial_data.csv     - Quadratic relationship")
