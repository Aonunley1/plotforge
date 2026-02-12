"""
Unit tests for PlotForge optimization changes.

Tests specifically target the optimizations made:
1. Type hints correctness
2. Error handling in trendline fitting
3. Color map caching efficiency
4. Code quality improvements
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from plotforge.engine import ScatterPlotEngine, BasePlotEngine
from plotforge.config import ScatterPlotConfig, TrendlineConfig, StatisticalOverlayConfig
from plotforge.gui.controller import PlotController


# ============================================================================
# Test 1: Color Map Generation with NaN Values
# ============================================================================
class TestColorMapHandling:
    """Test that color mapping correctly handles NaN values"""
    
    def test_color_map_excludes_nan(self):
        """Verify that NaN values in group column are excluded from color map"""
        engine = ScatterPlotEngine()
        df = pd.DataFrame({
            'X': [1, 2, 3, 4, 5],
            'Y': [1, 2, 3, 4, 5],
            'Group': ['A', 'B', np.nan, 'A', 'B']
        })
        config = ScatterPlotConfig(x='X', y='Y', group_by='Group')
        
        color_map = engine._generate_color_map(df, config)
        
        # Should only have colors for A and B, not NaN
        assert len(color_map) == 2
        assert 'A' in color_map
        assert 'B' in color_map
        assert np.nan not in color_map
        assert None not in color_map
    
    def test_color_map_single_group(self):
        """Test color map with no grouping"""
        engine = ScatterPlotEngine()
        df = pd.DataFrame({
            'X': [1, 2, 3],
            'Y': [1, 2, 3]
        })
        config = ScatterPlotConfig(x='X', y='Y', group_by=None)
        
        color_map = engine._generate_color_map(df, config)
        
        # Should have single color for ungrouped data
        assert len(color_map) == 1
        assert '_SINGLE_' in color_map


# ============================================================================
# Test 2: Trendline Error Handling
# ============================================================================
class TestTrendlineErrorHandling:
    """Test that trendline fitting handles edge cases gracefully"""
    
    def test_insufficient_data_per_group(self):
        """Test trendline with group having < 2 points"""
        engine = ScatterPlotEngine()
        df = pd.DataFrame({
            'X': [1, 2, 3, 100],
            'Y': [1, 2, 3, 50],
            'Group': ['A', 'A', 'A', 'B']  # Group B has only 1 point
        })
        config = ScatterPlotConfig(
            x='X', y='Y', group_by='Group',
            overlays=StatisticalOverlayConfig(
                trendline=TrendlineConfig(enabled=True)
            )
        )
        
        # Create a mock axes object
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        
        color_map = engine._generate_color_map(df, config)
        
        # Should not crash, should skip group B
        results = engine._calculate_and_draw_trendlines(ax, df, config, color_map)
        
        # Should only have trendline for group A
        assert len(results) == 1
        assert results[0]['group'] == 'A'
        
        plt.close(fig)
    
    def test_collinear_data_stability(self):
        """Test that perfectly collinear data doesn't cause numerical issues"""
        engine = ScatterPlotEngine()
        x = np.linspace(0, 100, 20)
        y = 2 * x + 5  # Perfect line
        
        df = pd.DataFrame({'X': x, 'Y': y})
        config = ScatterPlotConfig(
            x='X', y='Y',
            overlays=StatisticalOverlayConfig(
                trendline=TrendlineConfig(enabled=True)
            )
        )
        
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        
        color_map = engine._generate_color_map(df, config)
        
        # Should handle perfectly collinear data
        results = engine._calculate_and_draw_trendlines(ax, df, config, color_map)
        
        assert len(results) == 1
        assert results[0]['r2'] > 0.99  # Should be near-perfect fit
        
        plt.close(fig)


# ============================================================================
# Test 3: Color Map Caching (Performance)
# ============================================================================
class TestColorMapCaching:
    """Test that color map is generated once and reused"""
    
    def test_color_map_called_once(self, monkeypatch):
        """Verify _generate_color_map is called only once in apply_overlays"""
        engine = ScatterPlotEngine()
        df = pd.DataFrame({
            'X': np.linspace(0, 10, 20),
            'Y': np.linspace(0, 10, 20) + np.random.normal(0, 1, 20),
            'Group': ['A'] * 10 + ['B'] * 10
        })
        config = ScatterPlotConfig(
            x='X', y='Y', group_by='Group',
            overlays=StatisticalOverlayConfig(
                trendline=TrendlineConfig(enabled=True)
            )
        )
        
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        
        # Track how many times _generate_color_map is called
        call_count = {'count': 0}
        original_method = engine._generate_color_map
        
        def tracked_generate_color_map(*args, **kwargs):
            call_count['count'] += 1
            return original_method(*args, **kwargs)
        
        monkeypatch.setattr(engine, '_generate_color_map', tracked_generate_color_map)
        
        # Call apply_overlays (which calls both trendline and potentially KDE)
        engine.apply_overlays(ax, df, config)
        
        # Should be called exactly once (cached)
        assert call_count['count'] == 1
        
        plt.close(fig)


# ============================================================================
# Test 4: Controller Type Safety
# ============================================================================
class TestControllerTypeSafety:
    """Test that controller handles config types correctly"""
    
    def test_scatter_config_execution(self):
        """Test that ScatterPlotConfig is handled correctly"""
        controller = PlotController()
        df = pd.DataFrame({
            'X': [1, 2, 3],
            'Y': [1, 2, 3]
        })
        config = ScatterPlotConfig(x='X', y='Y')
        
        # Should execute without error
        result = controller.execute(df, config)
        
        assert result is not None
        assert result.figure is not None
    
    def test_unsupported_config_raises_error(self):
        """Test that unsupported config types raise ValueError"""
        from plotforge.config import BasePlotConfig
        
        controller = PlotController()
        df = pd.DataFrame({'X': [1, 2, 3], 'Y': [1, 2, 3]})
        
        # Create a mock unsupported config
        class UnsupportedConfig(BasePlotConfig):
            pass
        
        config = UnsupportedConfig()
        
        with pytest.raises(ValueError, match="Unsupported configuration type"):
            controller.execute(df, config)


# ============================================================================
# Test 5: Integration Test - Full Workflow
# ============================================================================
class TestFullWorkflow:
    """Integration tests for complete plotting workflow"""
    
    def test_normal_data_workflow(self):
        """Test complete workflow with normal data"""
        # Load test data
        test_data_path = Path(__file__).parent / "test_data" / "01_normal_data.csv"
        
        if not test_data_path.exists():
            pytest.skip("Test data not generated yet")
        
        df = pd.read_csv(test_data_path)
        
        config = ScatterPlotConfig(
            x='X', y='Y', group_by='Group',
            overlays=StatisticalOverlayConfig(
                trendline=TrendlineConfig(enabled=True)
            )
        )
        
        controller = PlotController()
        result = controller.execute(df, config)
        
        assert result is not None
        assert result.figure is not None
        assert 'trendlines' in result.artifacts
        assert len(result.artifacts['trendlines']) == 2  # Two groups
    
    def test_nan_data_workflow(self):
        """Test workflow with NaN values"""
        test_data_path = Path(__file__).parent / "test_data" / "02_nan_values.csv"
        
        if not test_data_path.exists():
            pytest.skip("Test data not generated yet")
        
        df = pd.read_csv(test_data_path)
        
        config = ScatterPlotConfig(
            x='X', y='Y', group_by='Group',
            overlays=StatisticalOverlayConfig(
                trendline=TrendlineConfig(enabled=True)
            )
        )
        
        controller = PlotController()
        
        # Should handle NaN gracefully
        result = controller.execute(df, config)
        
        assert result is not None
        assert result.figure is not None


# ============================================================================
# Run Tests
# ============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
