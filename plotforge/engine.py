import abc
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.ticker as ticker
import statsmodels.api as sm
from typing import Tuple, List, Dict, Any

from plotforge.config import BasePlotConfig, ScatterPlotConfig, PlotResult


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
        fig, ax = plt.subplots(figsize=config.save.figure_size)
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

    def _generate_color_map(self, df: pd.DataFrame, config: 'ScatterPlotConfig') -> Dict[Any, Any]:
        """Creates a SINGLE source of truth for color mapping."""
        if not config.group_by:
            if isinstance(config.palette, list) and len(config.palette) > 0:
                color = config.palette[0]
            else:
                color = sns.color_palette(config.palette, n_colors=1)[0]
            return {"_SINGLE_": color}

        unique_groups = sorted(df[config.group_by].dropna().unique())
        palette_colors = sns.color_palette(config.palette, n_colors=len(unique_groups))
        return dict(zip(unique_groups, palette_colors))

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

        # 1. Trendlines (Includes CI)
        if config.overlays.trendline and config.overlays.trendline.enabled:
            trendline_data = self._calculate_and_draw_trendlines(ax, df, config)
            artifacts["trendlines"] = pd.DataFrame(trendline_data)

        # 2. KDE
        if config.overlays.kde and config.overlays.kde.enabled:
            self._draw_kde(ax, df, config)

        return artifacts

    def _draw_kde(self, ax, df: pd.DataFrame, config: 'ScatterPlotConfig') -> None:
        kde_conf = config.overlays.kde
        color_map = self._generate_color_map(df, config)  # Get the Truth Map

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

    def _calculate_and_draw_trendlines(self, ax, df: pd.DataFrame, config: 'ScatterPlotConfig') -> List[Dict[str, Any]]:
        results = []
        trend_config = config.overlays.trendline
        ci_config = config.overlays.ci
        color_map = self._generate_color_map(df, config)

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

            X_des = np.vander(x_subset, trend_config.order + 1, increasing=True)
            model = sm.OLS(y_subset, X_des).fit()

            x_fit_grid = np.linspace(x_subset.min(), x_subset.max(), 100)
            X_fit_des = np.vander(x_fit_grid, trend_config.order + 1, increasing=True)

            y_fit_grid = model.predict(X_fit_des)

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