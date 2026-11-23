# =============================================================================
# OsdagBridge — Report charts (matplotlib)
# =============================================================================
# Programmatic charts embedded in the design report:
#   • Governing utilization-ratio summary             (Section 5.5)
#   • Structural-steel tonnage, concrete vs. rebar    (Chapter 7)
#
# Every colour / size / limit-line setting comes from ``styles.CHART``.
# Charts are written as PNG files into a caller-supplied directory (the report
# builder passes its temporary asset folder, which is deleted after the PDF is
# compiled).  The object-oriented matplotlib API is used on purpose — the report
# runs on a worker thread, where pyplot's global GUI state is not safe.
# =============================================================================

from __future__ import annotations

import logging
import os
import re
from typing import Dict, Iterable, List, Optional, Sequence

from osdagbridge.core.reports import styles as S

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def to_float(value) -> Optional[float]:
    """'12.34', 12.34, '\\textcolor{red}{1.05}' → float; 'N.A.', '---', None → None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    m = re.search(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", str(value))
    return float(m.group(0)) if m else None


def _rc():
    c = S.CHART
    return {
        "font.size": c["font_size"],
        "axes.titlesize": c["title_size"],
        "axes.edgecolor": c["axis_color"],
        "axes.labelcolor": c["axis_color"],
        "xtick.color": c["axis_color"],
        "ytick.color": c["axis_color"],
        "axes.spines.top": False,
        "axes.spines.right": False,
    }


def _new_figure(width=None, height=None, ncols=1):
    import matplotlib
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    w, h = S.CHART["figsize"]
    fig = Figure(figsize=(width or w, height or h), dpi=S.CHART["dpi"])
    FigureCanvasAgg(fig)
    return fig


def _save(fig, out_dir: str, stem: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, stem + ".png")
    fig.savefig(path, dpi=S.CHART["dpi"], bbox_inches="tight", facecolor="white")
    return path.replace("\\", "/")


def _style_axes(ax):
    ax.grid(axis="y", alpha=S.CHART["grid_alpha"], linewidth=0.6)
    ax.set_axisbelow(True)


# ─────────────────────────────────────────────────────────────────────────────
# Utilization-ratio charts
#   records: [{"element": "Steel Plate Girders", "label": "Moment", "ur": 0.83}, …]
# ─────────────────────────────────────────────────────────────────────────────

def _limit_line(ax):
    c = S.CHART
    return ax.axhline(c["limit_value"], color=c["limit_color"], linestyle=c["limit_style"],
                      linewidth=c["limit_width"], label=c["limit_label"], zorder=3)


def _bar_kwargs(ur: float, color: str):
    c = S.CHART
    if ur > c["limit_value"]:                    # failing check
        return dict(color=color, edgecolor=c["fail_edge_color"], hatch=c["fail_hatch"], linewidth=1.2)
    return dict(color=color, edgecolor="white", linewidth=0.6)


def _clean(records: Iterable[dict]) -> List[dict]:
    out = []
    for r in records or []:
        ur = to_float(r.get("ur"))
        if ur is None:
            continue
        out.append({"element": r.get("element", ""), "label": r.get("label", ""), "ur": ur})
    return out


def ur_summary_chart(records, out_dir: str, stem: str = "ur_summary") -> Optional[str]:
    """One bar per primary element showing its governing (maximum) UR."""
    import matplotlib
    from matplotlib.patches import Patch
    recs = _clean(records)
    c = S.CHART
    elements = list(c["element_colors"].keys())
    gov = {e: max((r["ur"] for r in recs if r["element"] == e), default=None) for e in elements}
    top = max([v for v in gov.values() if v is not None] + [c["limit_value"]])
    with matplotlib.rc_context(_rc()):
        fig = _new_figure(height=4.1)
        ax = fig.subplots()
        for i, e in enumerate(elements):
            v = gov[e]
            if v is None:
                ax.text(i, 0.02 * top, "n/a", ha="center", va="bottom", color="#777777", style="italic")
                continue
            ax.bar(i, v, width=c["bar_width"], zorder=2, **_bar_kwargs(v, c["element_colors"][e]))
            ax.text(i, v + 0.015 * top, c["value_fmt"].format(v), ha="center", va="bottom", fontweight="bold")
        _limit_line(ax)
        ax.set_xlim(-0.6, len(elements) - 0.4)
        ax.set_xticks(range(len(elements)))
        axis_labels = {
            "Steel Plate Girders": "Steel plate\ngirders",
            "Concrete Deck Slab": "Concrete deck\nslab",
            "Cross Bracing": "Cross\nbracing",
            "End Diaphragms": "End\ndiaphragms",
        }
        ax.set_xticklabels([axis_labels.get(e, e) for e in elements])
        ax.tick_params(axis="x", labelsize=c["font_size"] - 0.5)
        ax.set_ylabel("Utilization Ratio  (Demand / Capacity)")
        ax.set_ylim(0, max(1.2, top * 1.22))
        ax.set_title("Governing Utilization Ratio by Structural Element")
        _style_axes(ax)
        handles, labels = ax.get_legend_handles_labels()
        handles.append(Patch(facecolor="white", edgecolor=c["fail_edge_color"], hatch=c["fail_hatch"]))
        labels.append("UR > 1.0 (fails)")
        fig.subplots_adjust(bottom=0.27, top=0.84)
        ax.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.25),
                  ncol=2, frameon=False)
        path = _save(fig, out_dir, stem)
    return path


def ur_detail_chart(records, out_dir: str, stem: str = "ur_detail") -> Optional[str]:
    """One bar per design check, coloured by structural element."""
    import matplotlib
    from matplotlib.patches import Patch
    recs = _clean(records)
    if not recs:
        return None
    c = S.CHART
    order = {e: i for i, e in enumerate(c["element_colors"])}
    recs.sort(key=lambda r: order.get(r["element"], 99))
    n = len(recs)
    top = max([r["ur"] for r in recs] + [c["limit_value"]])
    with matplotlib.rc_context(_rc()):
        fig = _new_figure(width=max(c["figsize"][0], 0.62 * n + 2.0), height=4.4)
        ax = fig.subplots()
        for i, r in enumerate(recs):
            col = c["element_colors"].get(r["element"], "#999999")
            ax.bar(i, r["ur"], width=c["bar_width"], zorder=2, **_bar_kwargs(r["ur"], col))
            ax.text(i, r["ur"] + 0.012 * top, c["value_fmt"].format(r["ur"]),
                    ha="center", va="bottom", fontsize=c["font_size"] - 1)
        _limit_line(ax)
        ax.set_xlim(-0.6, n - 0.4)
        ax.set_xticks(range(n))
        ax.set_xticklabels([r["label"] for r in recs], rotation=35, ha="right")
        ax.set_ylabel("Utilization Ratio  (Demand / Capacity)")
        ax.set_ylim(0, max(1.2, top * 1.15))
        ax.set_title("Utilization Ratio by Design Check")
        _style_axes(ax)
        present = [e for e in c["element_colors"] if any(r["element"] == e for r in recs)]
        handles = [Patch(facecolor=c["element_colors"][e], label=e) for e in present]
        handles.append(ax.get_legend_handles_labels()[0][0])
        ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.30),
                  ncol=min(len(handles), 5), frameon=False)
        path = _save(fig, out_dir, stem)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# Material-quantity charts (Chapter 7)
# ─────────────────────────────────────────────────────────────────────────────

def steel_tonnage_chart(items: Sequence[dict], out_dir: str, stem: str = "qty_steel") -> Optional[str]:
    """items: [{"label": "Girders", "value": 12.3 | None, "color": "girders"}, …]  (MT)."""
    import matplotlib
    if not items or all(to_float(i.get("value")) is None for i in items):
        return None
    c = S.CHART
    vals = [to_float(i.get("value")) for i in items]
    top = max([v for v in vals if v is not None] + [0.0]) or 1.0
    with matplotlib.rc_context(_rc()):
        fig = _new_figure(height=3.5)
        ax = fig.subplots()
        for i, (it, v) in enumerate(zip(items, vals)):
            if v is None:
                ax.text(i, 0.02 * top, "n/a", ha="center", va="bottom", color="#777777", style="italic")
                continue
            ax.bar(i, v, width=c["bar_width"], zorder=2, edgecolor="white", linewidth=0.6,
                   color=c["quantity_colors"].get(it.get("color"), "#999999"))
            ax.text(i, v + 0.015 * top, "{:.2f} MT".format(v), ha="center", va="bottom", fontweight="bold")
        ax.set_xlim(-0.6, len(items) - 0.4)
        ax.set_xticks(range(len(items)))
        ax.set_xticklabels([i["label"] for i in items])
        ax.set_ylabel("Weight (MT)")
        ax.set_ylim(0, top * 1.18)
        ax.set_title("Structural Steel Quantity (Tonnage)")
        _style_axes(ax)
        path = _save(fig, out_dir, stem)
    return path


def concrete_rebar_chart(concrete_m3, rebar_mt, out_dir: str, stem: str = "qty_concrete_rebar") -> Optional[str]:
    """Concrete volume (m³) beside reinforcement-steel weight (MT).  The two
    quantities have different units, so each gets its own axis panel."""
    import matplotlib
    cv, rw = to_float(concrete_m3), to_float(rebar_mt)
    if cv is None and rw is None:
        return None
    c = S.CHART
    with matplotlib.rc_context(_rc()):
        fig = _new_figure(width=6.6, height=3.5)
        axes = fig.subplots(1, 2)
        panels = [(axes[0], cv, "Concrete (M40) — Deck Slab", "Volume (m³)", "{:.2f} m³", "concrete"),
                  (axes[1], rw, "Reinforcement Steel (Fe 500)", "Weight (MT)", "{:.2f} MT", "rebar")]
        for ax, v, title, ylab, fmt, key in panels:
            if v is None:
                ax.text(0.5, 0.5, "n/a", transform=ax.transAxes, ha="center", va="center",
                        color="#777777", style="italic")
                ax.set_xticks([])
            else:
                ax.bar(0, v, width=0.5, zorder=2, color=c["quantity_colors"][key], edgecolor="white")
                ax.text(0, v * 1.02, fmt.format(v), ha="center", va="bottom", fontweight="bold")
                ax.set_ylim(0, v * 1.2)
                ax.set_xticks([0])
                ax.set_xticklabels(["Deck slab"])
            ax.set_xlim(-0.6, 0.6)
            ax.set_ylabel(ylab)
            ax.set_title(title, fontsize=c["font_size"] + 0.5)
            _style_axes(ax)
        fig.suptitle("Concrete Volume vs. Reinforcement Steel Weight", fontsize=c["title_size"], y=1.02)
        fig.subplots_adjust(wspace=0.45)
        path = _save(fig, out_dir, stem)
    return path
