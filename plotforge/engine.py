import abc
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.ticker as ticker
import statsmodels.api as sm
from scipy.signal import find_peaks
from typing import Tuple, List, Dict, Any, Optional

from plotforge.config import BasePlotConfig, ScatterPlotConfig, LinePlotConfig, HistogramConfig, BarPlotConfig, BoxPlotConfig, PlotResult


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

        # constrained_layout on the Figure handles final layout automatically at draw time.
        warnings = self.collect_warnings(df, config)
        return PlotResult(figure=fig, artifacts=artifacts, warnings=warnings)

    def prepare_axes(self, config: 'BasePlotConfig') -> Tuple[matplotlib.figure.Figure, plt.Axes]:
        # FIX: Use OO-Interface (Figure) instead of Pyplot (subplots)
        # This prevents the "More than 20 figures" memory warning because
        # these figures are not registered with the global pyplot state machine.
        #
        # constrained_layout=True replaces the old tight_layout() call.
        # It computes layout incrementally at draw time, so it handles
        # box plots with wide category labels without producing a
        # "margins cannot be made large enough" UserWarning.
        fig = matplotlib.figure.Figure(figsize=config.save.figure_size, constrained_layout=True)
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
        if not config.overlays.error_bars.enabled:
            return

        eb_config = config.overlays.error_bars

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


    def _add_annotations(
        self,
        ax: plt.Axes,
        df: pd.DataFrame,
        config: 'BasePlotConfig',
        color_map: Dict[Any, Any]
    ) -> None:
        """
        Add annotations (text labels) to specific points on the plot.
        
        Supports:
        - Manual annotations at specific (x, y) coordinates
        - Automatic annotations (peaks, troughs, first/last points)
        - Custom styling (font, color, arrows, boxes)
        - Grouped and ungrouped data
        
        Args:
            ax: Matplotlib axes
            df: DataFrame with data
            config: Plot configuration with overlays.annotations
            color_map: Color mapping for groups
        """
        if not config.overlays.annotations.enabled:
            return

        ann_config = config.overlays.annotations

        # Manual annotations
        for annotation in ann_config.annotations:
            self._draw_single_annotation(ax, annotation)
        
        # Automatic annotations
        if config.group_by:
            # Annotate each group separately
            for group_name in sorted(df[config.group_by].dropna().unique()):
                group_df = df[df[config.group_by] == group_name]
                self._add_auto_annotations(
                    ax, group_df, config, ann_config, 
                    group_name, color_map
                )
        else:
            # Annotate ungrouped data
            self._add_auto_annotations(
                ax, df, config, ann_config, 
                None, color_map
            )
    
    def _draw_single_annotation(
        self,
        ax: plt.Axes,
        annotation
    ) -> None:
        """Draw a single manual annotation"""
        
        if annotation.x is None or annotation.y is None:
            return  # Skip if coordinates not specified
        
        # Build annotation kwargs
        ann_kwargs = {
            'xy': (annotation.x, annotation.y),
            'xytext': annotation.xytext_offset,
            'textcoords': 'offset points',
            'fontsize': annotation.fontsize,
            'color': annotation.color,
            'ha': 'left',
            'va': 'bottom'
        }
        
        # Add arrow if enabled
        if annotation.arrow:
            arrow_color = annotation.arrow_color if annotation.arrow_color else annotation.color
            ann_kwargs['arrowprops'] = {
                'arrowstyle': annotation.arrow_style,
                'color': arrow_color,
                'lw': 1.5
            }
        
        # Add bbox if enabled
        if annotation.bbox:
            ann_kwargs['bbox'] = {
                'boxstyle': 'round,pad=0.5',
                'facecolor': annotation.bbox_facecolor,
                'edgecolor': annotation.bbox_edgecolor,
                'alpha': annotation.bbox_alpha
            }
        
        ax.annotate(annotation.text, **ann_kwargs)
    
    def _add_auto_annotations(
        self,
        ax: plt.Axes,
        df: pd.DataFrame,
        config: 'BasePlotConfig',
        ann_config,
        group_name: Optional[Any],
        color_map: Dict[Any, Any]
    ) -> None:
        """Add automatic annotations (peaks, troughs, first/last)"""
        
        # Sort by X
        df_sorted = df.sort_values(config.x)
        x_vals = df_sorted[config.x].values
        y_vals = df_sorted[config.y].values
        
        if len(x_vals) == 0:
            return
        
        # Get color for this group
        if group_name is not None:
            color = color_map.get(group_name, ann_config.auto_color)
        else:
            color = color_map.get("_SINGLE_", ann_config.auto_color)
        
        # First point
        if ann_config.annotate_first:
            label = f"Start: ({x_vals[0]:.2f}, {y_vals[0]:.2f})"
            if group_name:
                label = f"{group_name} " + label
            self._draw_auto_annotation(
                ax, x_vals[0], y_vals[0], label, ann_config, color
            )
        
        # Last point
        if ann_config.annotate_last:
            label = f"End: ({x_vals[-1]:.2f}, {y_vals[-1]:.2f})"
            if group_name:
                label = f"{group_name} " + label
            self._draw_auto_annotation(
                ax, x_vals[-1], y_vals[-1], label, ann_config, color
            )
        
        # Peaks (local maxima)
        if ann_config.annotate_peaks and len(y_vals) >= 3:
            peaks, _ = find_peaks(y_vals)
            for peak_idx in peaks:
                label = f"Peak: {y_vals[peak_idx]:.2f}"
                if group_name:
                    label = f"{group_name} " + label
                self._draw_auto_annotation(
                    ax, x_vals[peak_idx], y_vals[peak_idx], 
                    label, ann_config, color
                )
        
        # Troughs (local minima)
        if ann_config.annotate_troughs and len(y_vals) >= 3:
            # Find peaks in inverted signal = troughs
            troughs, _ = find_peaks(-y_vals)
            for trough_idx in troughs:
                label = f"Trough: {y_vals[trough_idx]:.2f}"
                if group_name:
                    label = f"{group_name} " + label
                self._draw_auto_annotation(
                    ax, x_vals[trough_idx], y_vals[trough_idx], 
                    label, ann_config, color, offset=(10, -20)
                )
    
    def _draw_auto_annotation(
        self,
        ax: plt.Axes,
        x: float,
        y: float,
        text: str,
        ann_config,
        color: str,
        offset: Tuple[float, float] = (10, 10)
    ) -> None:
        """Draw a single automatic annotation"""
        
        ann_kwargs = {
            'xy': (x, y),
            'xytext': offset,
            'textcoords': 'offset points',
            'fontsize': ann_config.auto_fontsize,
            'color': color,
            'ha': 'left',
            'va': 'bottom'
        }
        
        if ann_config.auto_arrow:
            ann_kwargs['arrowprops'] = {
                'arrowstyle': '->',
                'color': color,
                'lw': 1.5
            }
        
        if ann_config.auto_bbox:
            ann_kwargs['bbox'] = {
                'boxstyle': 'round,pad=0.3',
                'facecolor': 'white',
                'edgecolor': color,
                'alpha': 0.9
            }
        
        ax.annotate(text, **ann_kwargs)


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
        if config.x_minor_interval:
            ax.xaxis.set_minor_locator(ticker.MultipleLocator(config.x_minor_interval))

        if config.y_major_interval:
            ax.yaxis.set_major_locator(ticker.MultipleLocator(config.y_major_interval))
        if config.y_minor_interval:
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(config.y_minor_interval))

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
            if legend:
                legend.remove()
            return

        cols = config.ncol if (config.ncol and config.ncol > 0) else 1

        if config.bbox_to_anchor:
            # sns.move_legend() requires an existing legend — create one first if absent.
            if ax.get_legend() is None:
                handles, labels = ax.get_legend_handles_labels()
                if not handles:
                    return
                ax.legend(handles=handles, labels=labels, title=config.title, ncol=cols)
            try:
                sns.move_legend(
                    ax, "center",
                    bbox_to_anchor=config.bbox_to_anchor,
                    ncol=cols,
                    title=config.title,
                    frameon=True
                )
            except Exception:
                pass  # Move failed gracefully — existing legend stays in place
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
        # Compute once here; apply_overlays() will reuse via self._color_map
        color_map = self._generate_color_map(df, config)
        self._color_map = color_map

        # --- Binned scatter: delegate to sns.regplot(x_bins=N) ---
        # regplot handles binning, per-bin mean estimation, and CI bands natively.
        # We skip sns.scatterplot entirely in this mode (early return below).
        # Grouping: regplot has no hue parameter, so we loop over groups and
        # call it once per group with the correct color from color_map.
        # fit_reg=False: our existing trendline overlay handles regression separately
        # so we don't want regplot to draw a second regression line.
        if config.bins and config.bins > 1:
            scatter_kws = {
                "s": config.marker_size,
                "alpha": config.alpha,
                "edgecolors": config.edgecolor,
                "linewidths": config.linewidth,
            }
            regplot_base = {
                "x": config.x,
                "y": config.y,
                "x_bins": config.bins,
                "fit_reg": False,
                "scatter_kws": scatter_kws,
                "ax": ax,
            }
            if config.group_by:
                for group_name in sorted(df[config.group_by].dropna().unique()):
                    group_df = df[df[config.group_by] == group_name]
                    color = color_map.get(group_name, "steelblue")
                    sns.regplot(data=group_df, color=color, label=str(group_name), **regplot_base)
            else:
                color = color_map.get("_SINGLE_", "steelblue")
                sns.regplot(data=df, color=color, **regplot_base)
            return  # scatterplot call below is skipped in binned mode
        # ------------------------------------------------------------------

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
            # Truncate markers list to the number of unique style values.
            # Seaborn warns if the list is longer than the number of categories.
            if isinstance(config.markers, list):
                n_styles = df[style_col].dropna().nunique()
                plot_kwargs["markers"] = config.markers[:n_styles]
            else:
                plot_kwargs["markers"] = config.markers
        else:
            # If no style column is selected, force all points to use the FIRST marker in the list
            if isinstance(config.markers, list) and len(config.markers) > 0:
                plot_kwargs["marker"] = config.markers[0]

        sns.scatterplot(**plot_kwargs)

    def apply_overlays(self, ax, df: pd.DataFrame, config: 'ScatterPlotConfig') -> Dict[str, Any]:
        artifacts = {}

        # Reuse the color map already computed in draw_core() — no second DataFrame scan.
        color_map = getattr(self, '_color_map', None) or self._generate_color_map(df, config)

        # 1. Trendlines (Includes CI)
        if config.overlays.trendline.enabled:
            trendline_data = self._calculate_and_draw_trendlines(ax, df, config, color_map)
            artifacts["trendlines"] = pd.DataFrame(trendline_data)

        # 2. KDE
        if config.overlays.kde.enabled:
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
                label="_nolegend_",  # Exclude trendlines from the auto-legend
                alpha=trend_config.alpha,
                zorder=2
            )

            # Calculate confidence intervals and standard errors
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


class HistogramPlotEngine(BasePlotEngine):
    """Ref: SPEC-1A Section 6 (New)"""
    
    def draw_core(self, ax, df: pd.DataFrame, config: 'HistogramConfig') -> None:
        # Generate color map (uses 'hue' logic)
        color_map = self._generate_color_map(df, config)
        self._color_map = color_map
        
        plot_kwargs = {
            "data": df,
            "x": config.x,
            "stat": config.stat,
            "kde": config.kde,
            "cumulative": config.cumulative,
            "element": config.element,
            "fill": config.fill,
            "log_scale": config.log_scale,
            "alpha": config.alpha,
            "linewidth": config.linewidth,
            "ax": ax
        }
        
        if config.edgecolor and config.edgecolor.lower() != "none":
            plot_kwargs["edgecolor"] = config.edgecolor
        
        # Handle bins
        if config.bins != "auto":
             try:
                 plot_kwargs["bins"] = int(config.bins)
             except ValueError:
                 plot_kwargs["bins"] = config.bins
        else:
            plot_kwargs["bins"] = "auto"

        # Handle grouping/coloring
        if config.group_by:
            plot_kwargs["hue"] = config.group_by
            plot_kwargs["palette"] = color_map
            # If element is 'poly' or 'step', we might want common_norm=False?
            # Usually strict users want density normalized per group.
            # Default behavior of sns.histplot is pretty good.
        else:
            if isinstance(color_map, dict) and "_SINGLE_" in color_map:
                 plot_kwargs["color"] = color_map["_SINGLE_"]
            else:
                 plot_kwargs["color"] = "blue"

        sns.histplot(**plot_kwargs)
        
    def apply_overlays(self, ax, df: pd.DataFrame, config: 'HistogramConfig') -> Dict[str, Any]:
        color_map = getattr(self, '_color_map', None) or self._generate_color_map(df, config)

        if config.overlays.annotations.enabled:
            self._add_annotations(ax, df, config, color_map)

        return {}




class LinePlotEngine(BasePlotEngine):
    """
    Engine for creating line plots.

    Delegates all line drawing, grouping, sorting, and CI bands to
    sns.lineplot() — which handles these natively via hue/palette and
    the errorbar parameter. The only custom overlay is fill_between
    (area under the line to y=0), which seaborn has no native parameter
    for and is applied in apply_overlays().
    """

    def draw_core(self, ax, df: pd.DataFrame, config: 'LinePlotConfig') -> None:
        self._validate_columns(df, [config.x, config.y])

        color_map = self._generate_color_map(df, config)
        self._color_map = color_map

        # Build the errorbar spec from LineCIConfig.
        # sns.lineplot errorbar accepts:
        #   ("ci", level)  — bootstrap CI  (level is a percentage, e.g. 95)
        #   ("se", N)      — N standard errors
        #   ("sd", N)      — N standard deviations
        #   None           — no CI band
        ci_cfg = config.overlays.line_ci
        if ci_cfg.enabled:
            level_pct = ci_cfg.level * 100  # e.g. 0.95 → 95
            errorbar: Any = (ci_cfg.method, level_pct) if ci_cfg.method == "ci" else (ci_cfg.method, 1)
        else:
            errorbar = None

        plot_kwargs: Dict[str, Any] = {
            "data": df,
            "x": config.x,
            "y": config.y,
            "linewidth": config.linewidth,
            "linestyle": config.linestyle,
            "alpha": config.alpha,
            "errorbar": errorbar,
            "err_kws": {"alpha": ci_cfg.alpha} if ci_cfg.enabled else {},
            "ax": ax,
        }

        if config.show_markers:
            plot_kwargs["marker"] = config.marker_style
            plot_kwargs["markersize"] = config.marker_size

        if config.group_by:
            plot_kwargs["hue"] = config.group_by
            plot_kwargs["palette"] = color_map
        else:
            plot_kwargs["color"] = color_map["_SINGLE_"]

        sns.lineplot(**plot_kwargs)

    def apply_overlays(self, ax, df: pd.DataFrame, config: 'LinePlotConfig') -> Dict[str, Any]:
        color_map = getattr(self, '_color_map', None) or self._generate_color_map(df, config)

        # Area fill: shade the region between the line and y=0.
        # This is a style overlay unrelated to CI — seaborn has no native param for it.
        if config.fill_between:
            if config.group_by:
                for group_name, group_df in df.groupby(config.group_by):
                    gdf = group_df.sort_values(config.x)
                    color = color_map.get(group_name, "steelblue")
                    ax.fill_between(
                        gdf[config.x], 0, gdf[config.y],
                        color=color, alpha=config.fill_alpha
                    )
            else:
                df_sorted = df.sort_values(config.x)
                color = color_map.get("_SINGLE_", "steelblue")
                ax.fill_between(
                    df_sorted[config.x], 0, df_sorted[config.y],
                    color=color, alpha=config.fill_alpha
                )

        self._add_error_bars(ax, df, config, color_map)
        self._add_annotations(ax, df, config, color_map)
        return {}


class BarPlotEngine(BasePlotEngine):
    """
    Engine for creating bar plots.
    Supports aggregation (mean, sum, etc.) and error bars.
    """
    
    def draw_core(self, ax, df: pd.DataFrame, config: 'BarPlotConfig') -> None:
        # Validate whichever columns are specified (y is optional for count estimator)
        required = [col for col in [config.x, config.y] if col]
        self._validate_columns(df, required)
        
        color_map = self._generate_color_map(df, config)
        self._color_map = color_map
        
        # Map simple estimator strings to actual functions if needed,
        # but seaborn handles "mean", "median", "sum", "min", "max" directly.
        estimator = config.estimator
        if estimator == "count":
            estimator = len

        
        # Prepare arguments
        plot_kwargs = {
            "data": df,
            "x": config.x,
            "y": config.y,
            "estimator": estimator,
            "errorbar": config.errorbar if config.errorbar != "none" else None,
            "capsize": config.capsize,
            "width": config.width,
            "alpha": config.alpha,
            "linewidth": config.linewidth,
            "ax": ax
        }
        
        if config.orientation == 'h':
            # Swap x and y in kwargs is NOT enough for seaborn if we want horizontal bars.
            # Seaborn infers orientation from x/y types usually, or we can explicit swap.
            # If config.orientation is 'h', user likely mapped Categorical to Y and Value to X.
            # But if they mapped standard (Cat->X, Val->Y) and requested horizontal,
            # we should swap them here.
            # However, typically config.x/y match the user's intent.
            # If user wants horizontal, they put the category on Y.
            # So standard kwargs are likely correct as long as config.x/y are correct.
            # Using 'orient' parameter can enforce it.
            plot_kwargs["orient"] = "h"
        else:
            plot_kwargs["orient"] = "v"
            
        if config.edgecolor:
            plot_kwargs["edgecolor"] = config.edgecolor
            
        # Coloring
        if config.group_by:
            plot_kwargs["hue"] = config.group_by
            plot_kwargs["palette"] = color_map
        else:
            # Single color
            if isinstance(color_map, dict) and "_SINGLE_" in color_map:
                 plot_kwargs["color"] = color_map["_SINGLE_"]
            else:
                 plot_kwargs["color"] = "blue"
        
        sns.barplot(**plot_kwargs)
        
    def apply_overlays(self, ax, df: pd.DataFrame, config: 'BarPlotConfig') -> Dict[str, Any]:
        color_map = getattr(self, '_color_map', None) or self._generate_color_map(df, config)

        if config.overlays.annotations.enabled:
            self._add_annotations(ax, df, config, color_map)

        return {}


class BoxPlotEngine(BasePlotEngine):
    """
    Engine for creating box plots (box-and-whisker).
    Supports grouping, orientation, and outliers.
    """
    
    def draw_core(self, ax, df: pd.DataFrame, config: 'BoxPlotConfig') -> None:
        # Validate whichever columns are actually specified
        required = [col for col in [config.x, config.y] if col]
        self._validate_columns(df, required)

        color_map = self._generate_color_map(df, config)
        self._color_map = color_map

        plot_kwargs = {
            "data": df,
            "notch": config.notch,
            "showmeans": config.showmeans,
            "width": config.width,
            "linewidth": config.linewidth,
            "fliersize": config.fliersize,
            "ax": ax
        }

        # Map orientation to seaborn's axis convention:
        #   Vertical   → x = Category (X),  y = Values (Y)
        #   Horizontal → x = Values (Y),    y = Category (X)   ← axes are flipped
        # config.x always holds the "Category" column and config.y always holds
        # the "Values" column, regardless of orientation — the engine does the swap.
        if config.orientation == "h":
            if config.x:
                plot_kwargs["y"] = config.x  # Category column goes on the Y axis
            if config.y:
                plot_kwargs["x"] = config.y  # Values column goes on the X axis
        else:
            if config.x:
                plot_kwargs["x"] = config.x  # Category column on X axis
            if config.y:
                plot_kwargs["y"] = config.y  # Values column on Y axis

        plot_kwargs["orient"] = "h" if config.orientation == "h" else "v"

        # Coloring
        if config.group_by:
            plot_kwargs["hue"] = config.group_by
            plot_kwargs["palette"] = color_map
        else:
            plot_kwargs["color"] = color_map.get("_SINGLE_", "steelblue")

        try:
            sns.boxplot(**plot_kwargs)
            
            # Overlay individual data points if requested
            if getattr(config, 'show_data_points', False):
                # We reuse the plot_kwargs but adjust it for stripplot
                strip_kwargs = {
                    "data": df,
                    "x": plot_kwargs.get("x"),
                    "y": plot_kwargs.get("y"),
                    "hue": plot_kwargs.get("hue"),
                    "orient": plot_kwargs.get("orient"),
                    "palette": plot_kwargs.get("palette"),
                    "color": plot_kwargs.get("color"),
                    "ax": ax,
                    "dodge": True if plot_kwargs.get("hue") else False,
                    "alpha": 0.5,
                    "zorder": 1,
                    # Edge color makes points visible against similarly colored boxes
                    "linewidth": 0.5,
                    "edgecolor": "0.5",
                }
                
                # If both are used simultaneously, we drop 'color' or 'palette' if invalid
                if strip_kwargs["hue"] is None:
                    strip_kwargs.pop("palette", None)
                else:
                    strip_kwargs.pop("color", None)
                    
                sns.stripplot(**strip_kwargs)
                
        except Exception as e:
            raise ValueError(
                f"Box plot failed: {e}\n\n"
                "Tip: 'Category (X)' should be a text/categorical column and "
                "'Values (Y)' should be numeric."
            ) from e
        
    def apply_overlays(self, ax, df: pd.DataFrame, config: 'BoxPlotConfig') -> Dict[str, Any]:
        color_map = getattr(self, '_color_map', None) or self._generate_color_map(df, config)

        if config.overlays.annotations.enabled:
            self._add_annotations(ax, df, config, color_map)

        artifacts = {}

        # config.x is ALWAYS the Category column and config.y is ALWAYS the Values column,
        # regardless of orientation.  The axis swap for seaborn is performed inside draw_core
        # and is transparent to apply_overlays — so we always read group/value the same way.
        primary_group = config.x
        value_col = config.y

        # Only compute statistics when a numeric value column was actually selected.
        if value_col and value_col in df.columns:
            group_cols = []
            if primary_group and primary_group in df.columns:
                group_cols.append(primary_group)
            if config.group_by and config.group_by in df.columns:
                group_cols.append(config.group_by)

            if group_cols:
                box_stats = df.groupby(group_cols)[value_col].describe()
                artifacts["box_stats"] = box_stats
            else:
                desc = df[value_col].describe().to_frame().T
                desc["group"] = "All"
                artifacts["box_stats"] = desc

        return artifacts
    
