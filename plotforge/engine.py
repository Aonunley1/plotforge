import abc
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.ticker as ticker
import statsmodels.api as sm
from typing import Tuple, List, Dict, Any

from plotforge.config import BasePlotConfig, ScatterPlotConfig, LinePlotConfig, PlotResult


class PlotEngine(abc.ABC):
    @abc.abstractmethod
    def execute(self, df: pd.DataFrame, config: 'BasePlotConfig') -> 'PlotResult':
        pass


class BasePlotEngine(PlotEngine):
    """Ref: SPEC-1A Section 4"""

    def execute(self, df: pd.DataFrame, config: 'BasePlotConfig') -> 'PlotResult':
        # 1. Apply Style FIRST
        self.apply_style(config)

        # 2. Create Figure
        fig, ax = self.prepare_axes(config)

        # 3. Draw Plot
        self.draw_core(ax, df, config)

        # 4. Apply Labels
        if config.x_label: ax.set_xlabel(config.x_label)
        if config.y_label: ax.set_ylabel(config.y_label)

        if config.title:
            ax.set_title(config.title)
        else:
            ax.set_title(None)

        # 5. Overlays, Axes, Legend
        artifacts = self.apply_overlays(ax, df, config)
        self.apply_axes_config(ax, config.axes)
        self.apply_legend(ax, config.legend)

        # 6. Final Layout Adjustment
        fig.tight_layout()

        warnings = self.collect_warnings(df, config)
        return PlotResult(figure=fig, artifacts=artifacts, warnings=warnings)

    def prepare_axes(self, config: 'BasePlotConfig') -> Tuple[matplotlib.figure.Figure, plt.Axes]:
        # FIX: Use OO-Interface (Figure) instead of Pyplot (subplots)
        # This prevents the "More than 20 figures" memory warning because
        # these figures are not registered with the global pyplot state machine.
        fig = matplotlib.figure.Figure(figsize=config.save.figure_size)
        ax = fig.add_subplot(111)
        return fig, ax

    def apply_style(self, config: 'BasePlotConfig') -> None:
        sns.set_theme(
            style=config.style.theme,
            font_scale=config.style.font_scale,
            rc=config.style.rc_params
        )

    @abc.abstractmethod
    def draw_core(self, ax: plt.Axes, df: pd.DataFrame, config: 'BasePlotConfig') -> None:
        pass

    def apply_overlays(self, ax: plt.Axes, df: pd.DataFrame, config: 'BasePlotConfig') -> Dict[str, Any]:
        return {}

    # --- SHARED HELPER METHODS (Available to all plot engines) ---

    def _generate_color_map(self, df: pd.DataFrame, config: 'BasePlotConfig') -> Dict[Any, Any]:
        """
        Creates a SINGLE source of truth for color mapping.
        
        This method is shared by ALL plot types that support grouping.
        It handles both single-color and multi-group scenarios.
        
        Returns:
            Dict mapping group names to colors, or {"_SINGLE_": color} for ungrouped data
        """
        if not config.group_by:
            # Single color for ungrouped data
            if isinstance(config.palette, list) and len(config.palette) > 0:
                color = config.palette[0]
            else:
                color = sns.color_palette(config.palette, n_colors=1)[0]
            return {"_SINGLE_": color}

        # Multiple groups - create color mapping
        unique_groups = sorted(df[config.group_by].dropna().unique())
        palette_colors = sns.color_palette(config.palette, n_colors=len(unique_groups))
        return dict(zip(unique_groups, palette_colors))

    def _validate_columns(self, df: pd.DataFrame, required_columns: List[str]) -> None:
        """
        Validate that required columns exist in DataFrame.
        
        Args:
            df: DataFrame to validate
            required_columns: List of column names that must exist
            
        Raises:
            ValueError: If any required columns are missing
        """
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def _get_palette_colors(self, config: 'BasePlotConfig', n_colors: int) -> List:
        """
        Get palette colors - handles both list and string palettes.
        
        Args:
            config: Plot configuration with palette attribute
            n_colors: Number of colors needed
            
        Returns:
            List of colors
        """
        if isinstance(config.palette, list):
            return config.palette[:n_colors]
        else:
            return sns.color_palette(config.palette, n_colors=n_colors)

    def _add_error_bars(
        self, 
        ax: plt.Axes, 
        df: pd.DataFrame, 
        config: 'BasePlotConfig',
        color_map: Dict[Any, Any]
    ) -> None:
        """
        Add error bars to plot (works for scatter and line plots).
        
        Supports:
        - Y error bars (vertical)
        - X error bars (horizontal)
        - Error values from DataFrame columns or fixed values
        - Per-group coloring
        
        Args:
            ax: Matplotlib axes
            df: DataFrame with data
            config: Plot configuration with overlays.error_bars
            color_map: Color mapping for groups
        """
        if not config.overlays or not config.overlays.error_bars:
            return
        
        eb_config = config.overlays.error_bars
        if not eb_config.enabled:
            return
        
        # Determine error values
        yerr = None
        xerr = None
        
        if eb_config.y_error_column and eb_config.y_error_column in df.columns:
            yerr = df[eb_config.y_error_column]
        elif eb_config.y_error is not None:
            yerr = eb_config.y_error
        
        if eb_config.x_error_column and eb_config.x_error_column in df.columns:
            xerr = df[eb_config.x_error_column]
        elif eb_config.x_error is not None:
            xerr = eb_config.x_error
        
        # If no errors specified, return
        if yerr is None and xerr is None:
            return
        
        # Add error bars (grouped or ungrouped)
        if config.group_by:
            # Grouped error bars
            for group_name in sorted(df[config.group_by].dropna().unique()):
                group_df = df[df[config.group_by] == group_name]
                
                # Get error values for this group
                # Handle both Series (from column) and scalar (fixed value)
                if isinstance(yerr, pd.Series):
                    group_yerr = yerr.loc[group_df.index]
                else:
                    group_yerr = yerr  # Fixed value
                
                if isinstance(xerr, pd.Series):
                    group_xerr = xerr.loc[group_df.index]
                else:
                    group_xerr = xerr  # Fixed value
                
                # Get color for this group
                color = color_map.get(group_name, eb_config.color)
                
                ax.errorbar(
                    group_df[config.x],
                    group_df[config.y],
                    yerr=group_yerr,
                    xerr=group_xerr,
                    fmt='none',  # Don't draw markers (already drawn by plot)
                    ecolor=color if eb_config.color is None else eb_config.color,
                    elinewidth=eb_config.linewidth,
                    capsize=eb_config.capsize,
                    capthick=eb_config.capthick,
                    alpha=eb_config.alpha,
                    zorder=1  # Draw behind markers/lines
                )
        else:
            # Ungrouped error bars
            color = color_map.get("_SINGLE_", eb_config.color)
            
            ax.errorbar(
                df[config.x],
                df[config.y],
                yerr=yerr,
                xerr=xerr,
                fmt='none',
                ecolor=color if eb_config.color is None else eb_config.color,
                elinewidth=eb_config.linewidth,
                capsize=eb_config.capsize,
                capthick=eb_config.capthick,
                alpha=eb_config.alpha,
                zorder=1
            )


    def apply_axes_config(self, ax: plt.Axes, config) -> None:
        # 1. Bounds / Limits
        if config.x_min is not None and config.x_max is not None:
            ax.set_xbound(config.x_min, config.x_max)
        elif config.x_min is not None:
            ax.set_xlim(left=config.x_min)
        elif config.x_max is not None:
            ax.set_xlim(right=config.x_max)

        if config.y_min is not None and config.y_max is not None:
            ax.set_ybound(config.y_min, config.y_max)
        elif config.y_min is not None:
            ax.set_ylim(bottom=config.y_min)
        elif config.y_max is not None:
            ax.set_ylim(top=config.y_max)

        # 2. Ticks (Locators)
        if config.x_major_interval:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(config.x_major_interval))
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(config.x_major_interval / 2))

        if config.y_major_interval:
            ax.yaxis.set_major_locator(ticker.MultipleLocator(config.y_major_interval))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(config.y_major_interval / 2))

        # 3. Clean Origin (Prevent Double "0")
        if config.x_min is not None and config.y_min is not None:
            if abs(config.x_min - config.y_min) < 1e-9:
                # Force update ticks
                _ = ax.get_xticks()
                for tick in ax.xaxis.get_major_ticks():
                    if abs(tick.get_loc() - config.x_min) < 1e-9:
                        tick.label1.set_visible(False)

        # 4. Reference Lines
        if config.ref_lines:
            # Line 1
            if config.ref_lines.line1_enabled:
                ax.axvline(
                    x=config.ref_lines.x1,
                    color=config.ref_lines.color,
                    linewidth=config.ref_lines.linewidth,
                    linestyle=config.ref_lines.linestyle,
                    zorder=0
                )
            # Line 2
            if config.ref_lines.line2_enabled:
                ax.axvline(
                    x=config.ref_lines.x2,
                    color=config.ref_lines.color,
                    linewidth=config.ref_lines.linewidth,
                    linestyle=config.ref_lines.linestyle,
                    zorder=0
                )

    def apply_legend(self, ax: plt.Axes, config) -> None:
        if not config.enabled:
            legend = ax.get_legend()
            if legend: legend.remove()
            return

        # Ensure valid column count
        cols = config.ncol if (config.ncol and config.ncol > 0) else 1

        if config.bbox_to_anchor:
            sns.move_legend(
                ax, "center",
                bbox_to_anchor=config.bbox_to_anchor,
                ncol=cols,
                title=config.title,
                frameon=True
            )
        else:
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(
                    handles=handles,
                    labels=labels,
                    title=config.title,
                    loc=config.location,
                    ncol=cols
                )

    def collect_warnings(self, df: pd.DataFrame, config: 'BasePlotConfig') -> List[str]:
        return []


class ScatterPlotEngine(BasePlotEngine):
    """Ref: SPEC-1A Section 5"""

    # _generate_color_map is now inherited from BasePlotEngine

    def draw_core(self, ax, df: pd.DataFrame, config: 'ScatterPlotConfig') -> None:
        style_col = config.style_by
        color_map = self._generate_color_map(df, config)

        plot_kwargs = {
            "data": df,
            "x": config.x,
            "y": config.y,
            "hue": config.group_by,
            "style": style_col,
            "s": config.marker_size,
            "alpha": config.alpha,
            "edgecolor": config.edgecolor,
            "linewidth": config.linewidth,
            "ax": ax
        }

        if config.group_by:
            plot_kwargs["palette"] = color_map
        else:
            plot_kwargs["color"] = color_map["_SINGLE_"]

        if style_col:
            plot_kwargs["markers"] = config.markers
        else:
            # If no style column is selected, force all points to use the FIRST marker in the list
            if isinstance(config.markers, list) and len(config.markers) > 0:
                plot_kwargs["marker"] = config.markers[0]

        sns.scatterplot(**plot_kwargs)

    def apply_overlays(self, ax, df: pd.DataFrame, config: 'ScatterPlotConfig') -> Dict[str, Any]:
        artifacts = {}

        # Generate color map once and reuse (performance optimization)
        color_map = self._generate_color_map(df, config)

        # 1. Trendlines (Includes CI)
        if config.overlays.trendline and config.overlays.trendline.enabled:
            trendline_data = self._calculate_and_draw_trendlines(ax, df, config, color_map)
            artifacts["trendlines"] = pd.DataFrame(trendline_data)

        # 2. KDE
        if config.overlays.kde and config.overlays.kde.enabled:
            self._draw_kde(ax, df, config, color_map)

        return artifacts

    def _draw_kde(self, ax, df: pd.DataFrame, config: 'ScatterPlotConfig', color_map: Dict[Any, Any]) -> None:
        kde_conf = config.overlays.kde

        # Arguments valid for BOTH Line and Fill
        kde_kwargs = {
            "data": df,
            "x": config.x,
            "y": config.y,
            "fill": kde_conf.fill,
            "ax": ax,
            "zorder": 0,
            "warn_singular": False,
            "alpha": kde_conf.alpha,
        }

        # FIX 1: Pass PLURAL 'linewidths' if NOT filling
        # This fixes the "UserWarning: kwargs not used by contour"
        if not kde_conf.fill:
            kde_kwargs["linewidths"] = kde_conf.linewidth

        # FIX 2: Strict Exclusion (Hue vs Cmap)
        if config.group_by:
            # GROUPING ACTIVE: Must use hue/palette. Cmap is FORBIDDEN.
            kde_kwargs["hue"] = config.group_by
            kde_kwargs["palette"] = color_map
        else:
            # GROUPING INACTIVE: Can use Cmap OR Color.
            if kde_conf.cmap and kde_conf.cmap.lower() != "none":
                kde_kwargs["cmap"] = kde_conf.cmap
            else:
                kde_kwargs["color"] = color_map["_SINGLE_"]

        try:
            sns.kdeplot(**kde_kwargs)
        except Exception as e:
            print(f"Warning: KDE Plot failed - {e}")

    def _calculate_and_draw_trendlines(self, ax, df: pd.DataFrame, config: 'ScatterPlotConfig', color_map: Dict[Any, Any]) -> List[Dict[str, Any]]:
        results = []
        trend_config = config.overlays.trendline
        ci_config = config.overlays.ci

        if config.group_by:
            groups = df.groupby(config.group_by)
        else:
            groups = [("All", df)]

        for name, group_df in groups:
            clean_df = group_df[[config.x, config.y]].dropna()
            if clean_df.empty or len(clean_df) < 2:
                continue

            x = clean_df[config.x].values
            y = clean_df[config.y].values

            if trend_config.fit_range:
                x_min, x_max = trend_config.fit_range
                mask = (x >= x_min) & (x <= x_max)
                x_subset, y_subset = x[mask], y[mask]
            else:
                x_subset, y_subset = x, y

            if len(x_subset) < 2: continue

            try:
                X_des = np.vander(x_subset, trend_config.order + 1, increasing=True)
                model = sm.OLS(y_subset, X_des).fit()

                x_fit_grid = np.linspace(x_subset.min(), x_subset.max(), 100)
                X_fit_des = np.vander(x_fit_grid, trend_config.order + 1, increasing=True)

                y_fit_grid = model.predict(X_fit_des)
            except (np.linalg.LinAlgError, ValueError) as e:
                # Skip this group if fitting fails (singular matrix, numerical issues, etc.)
                print(f"Warning: Trendline fitting failed for group '{name}': {e}")
                continue

            if config.group_by:
                line_color = color_map.get(name, "black")
            else:
                line_color = color_map.get("_SINGLE_", "black")

            conf_alpha = 0.05
            if ci_config and ci_config.enabled:
                conf_alpha = 1.0 - ci_config.level

            if ci_config and ci_config.enabled:
                predictions = model.get_prediction(X_fit_des)
                pred_frame = predictions.summary_frame(alpha=conf_alpha)

                ax.fill_between(
                    x_fit_grid,
                    pred_frame['mean_ci_lower'],
                    pred_frame['mean_ci_upper'],
                    color=line_color,
                    alpha=ci_config.alpha,
                    zorder=1
                )

            ax.plot(
                x_fit_grid,
                y_fit_grid,
                color=line_color,
                linewidth=trend_config.linewidth,
                linestyle=trend_config.linestyle,
                alpha=trend_config.alpha,
                zorder=2
            )

            param_ci = model.conf_int(alpha=conf_alpha)
            bse = model.bse

            row_data = {
                "group": str(name),
                "order": trend_config.order,
                "n": len(x_subset),
                "r2": model.rsquared,
                "p_value": model.f_pvalue,
                "coefficients": model.params.tolist(),
            }

            if trend_config.order >= 1:
                row_data["intercept"] = model.params[0]
                row_data["intercept_std_err"] = bse[0]
                row_data["intercept_lower"] = param_ci[0][0]
                row_data["intercept_upper"] = param_ci[0][1]

                row_data["slope"] = model.params[1]
                row_data["slope_std_err"] = bse[1]
                row_data["slope_lower"] = param_ci[1][0]
                row_data["slope_upper"] = param_ci[1][1]

            results.append(row_data)

        return results


class LinePlotEngine(BasePlotEngine):
    """
    Engine for creating line plots.
    
    Supports:
    - Single or multiple lines (via group_by)
    - Optional markers on data points
    - Fill between line and x-axis
    - Confidence intervals (via overlays)
    """

    def draw_core(self, ax, df: pd.DataFrame, config: 'LinePlotConfig') -> None:
        """Draw the line plot"""
        
        # Validate required columns
        self._validate_columns(df, [config.x, config.y])
        
        # Generate color mapping
        color_map = self._generate_color_map(df, config)
        
        if config.group_by:
            # Multiple lines (one per group)
            for group_name, group_df in df.groupby(config.group_by):
                self._draw_single_line(ax, group_df, config, color_map, group_name)
        else:
            # Single line
            self._draw_single_line(ax, df, config, color_map)
        
        # Add error bars if configured
        self._add_error_bars(ax, df, config, color_map)
    
    def _draw_single_line(self, ax, df, config, color_map, label=None):
        """Helper to draw a single line"""
        
        # Get color
        color = color_map.get(label, color_map.get("_SINGLE_", "blue"))
        
        # Sort by X for proper line drawing
        df_sorted = df[[config.x, config.y]].dropna().sort_values(config.x)
        
        if df_sorted.empty:
            return
        
        # Draw line
        ax.plot(
            df_sorted[config.x],
            df_sorted[config.y],
            color=color,
            linewidth=config.linewidth,
            linestyle=config.linestyle,
            marker=config.marker_style if config.show_markers else None,
            markersize=config.marker_size if config.show_markers else 0,
            alpha=config.alpha,
            label=label
        )
        
        # Optional fill
        if config.fill_between:
            ax.fill_between(
                df_sorted[config.x],
                df_sorted[config.y],
                alpha=config.fill_alpha,
                color=color
            )
    
    def apply_overlays(self, ax, df, config):
        """Apply line-specific overlays"""
        artifacts = {}
        
        # Confidence intervals could be added here in the future
        # For now, line plots don't have specific overlays beyond fill_between
        
        return artifacts