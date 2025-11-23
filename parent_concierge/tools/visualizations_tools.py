import io
from pathlib import Path
from typing import List, Dict, Any

import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import google.genai.types as types
from google.adk.tools import ToolContext


# Pre-load icons (64x64 PNGs) from the assets folder so repeated tool calls
# reuse cached images instead of re-reading from disk inside the async flow.
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
FEED_ICON_PATH = ASSETS_DIR / "feed_icon.png"
NAP_ICON_PATH = ASSETS_DIR / "nap_icon.png"
DIAPER_ICON_PATH = ASSETS_DIR / "diaper_icon.png"


def _load_icon(path: Path, zoom: float = 0.6) -> OffsetImage:
    """Load an icon image and wrap it as an OffsetImage for use with AnnotationBbox."""
    img = plt.imread(path)
    return OffsetImage(img, zoom=zoom)


FEED_ICON_IMG = _load_icon(FEED_ICON_PATH, zoom=0.4)
NAP_ICON_IMG = _load_icon(NAP_ICON_PATH, zoom=0.4)
DIAPER_ICON_IMG = _load_icon(DIAPER_ICON_PATH, zoom=0.4)


async def create_bar_chart_artifact(
    logs_for_day: List[Dict[str, Any]],
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Generate a PNG bar chart representing feeds, naps, and diapers for a given day.

    Args:
        logs_for_day: List of care events for the day.

    Returns:
        {
          "filename": "daily_summary_chart.png",
          "version": <int version>,
        }
    """
    total_feed_ml = 0
    total_nap_minutes = 0
    diaper_count = 0

    for event in logs_for_day or []:
        etype = event.get("event_type")
        if etype == "feed":
            vol = event.get("volume_ml")
            if isinstance(vol, (int, float)):
                total_feed_ml += int(vol)
        elif etype == "nap":
            mins = event.get("duration_minutes")
            if isinstance(mins, (int, float)):
                total_nap_minutes += int(mins)
        elif etype == "diaper":
            diaper_count += 1

    metrics = ["Feeds (ml)", "Naps (mins)", "Diapers"]
    values = [total_feed_ml, total_nap_minutes, diaper_count]

    fig, ax = plt.subplots(figsize=(7, 4.5))

    bars = ax.bar(metrics, values, zorder=2)

    ax.set_title("Daily Care Summary", fontsize=14, pad=12)
    ax.set_ylabel("Value", fontsize=12)
    ax.tick_params(axis="x", labelrotation=10, labelsize=11)
    ax.tick_params(axis="y", labelsize=10)

    ax.grid(axis="y", linestyle="--", alpha=0.35, zorder=0)

    max_val = max(values) if values else 0

    ax.set_ylim(0, max_val * 1.35 + 10)

    LABEL_OFFSET = 8
    ICON_OFFSET = 30  # Spacing keeps labels/icons from overlapping small bars.

    icon_map = {
        "Feeds (ml)": FEED_ICON_IMG,
        "Naps (mins)": NAP_ICON_IMG,
        "Diapers": DIAPER_ICON_IMG,
    }

    for bar, metric_label, value in zip(bars, metrics, values):
        height = bar.get_height()
        x_center = bar.get_x() + bar.get_width() / 2

        ax.annotate(
            f"{value}",
            xy=(x_center, height),
            xytext=(0, LABEL_OFFSET),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
        )

        icon_img = icon_map[metric_label]
        ab = AnnotationBbox(
            icon_img,
            (x_center, height),
            xybox=(0, LABEL_OFFSET + ICON_OFFSET),
            frameon=False,
            boxcoords="offset points",
            box_alignment=(0.5, 0.5),
            pad=0.0,
        )
        ax.add_artist(ab)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)

    image_part = types.Part.from_bytes(
        data=buf.getvalue(),
        mime_type="image/png",
    )

    version = await tool_context.save_artifact(
        filename="daily_summary_chart.png",
        artifact=image_part,
    )

    return {
        "filename": "daily_summary_chart.png",
        "version": version,
    }
