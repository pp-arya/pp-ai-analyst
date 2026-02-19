# Skill: Brand Theme Visualization

## Purpose
Apply a consistent, warm brand color theme to every chart Claude Code produces,
replacing the default minimal palette with colors that look polished and
professional in stakeholder presentations.

## When to Use
Apply this skill whenever generating a chart, graph, or data visualization. Use
these colors and styling rules instead of the default palette. Can be combined
with the Visualization Patterns skill for chart type selection and annotation
standards.

## Instructions

### Color Palette

```python
BRAND_THEME = {
    "colors": {
        "primary": "#2D5F2D",      # Forest green -- main bars, primary lines
        "secondary": "#8B4513",     # Saddle brown -- secondary elements
        "accent": "#DAA520",        # Goldenrod -- highlights, callouts, key data
        "palette": [
            "#2D5F2D",  # Forest green
            "#DAA520",  # Goldenrod
            "#8B4513",  # Saddle brown
            "#5B8C5B",  # Sage green (lighter)
            "#D4A76A",  # Warm tan
            "#3E7B3E",  # Medium green
        ],
        "background": "#FAFAF5",    # Warm off-white
        "grid": "#E8E4DC",          # Warm gray
        "text": "#2C2C2C",          # Near-black
        "muted": "#A0998C",         # For secondary labels
    },
    "fonts": {
        "title": {"family": "Georgia", "size": 16, "weight": "bold"},
        "subtitle": {"family": "Helvetica", "size": 11, "weight": "normal", "color": "#6B6560"},
        "axis_label": {"family": "Helvetica", "size": 10},
        "annotation": {"family": "Helvetica", "size": 9, "style": "italic"},
    },
    "grid": {
        "show": True,
        "axis": "y",
        "style": "-",
        "alpha": 0.2,
        "color": "#E8E4DC",
    },
    "annotations": {
        "style": "minimal",
        "direct_labels": True,
        "callout_color": "#DAA520",
    },
    "title": {
        "position": "left-aligned",
        "include_subtitle": True,
    },
}
```

### Styling Rules

1. **Background**: Always use the warm off-white (`#FAFAF5`), not pure white. It
   reduces eye strain and looks more professional on slides.

2. **Highlighting**: Use goldenrod (`#DAA520`) to highlight the key finding in any
   chart. All other bars/lines use forest green or saddle brown. Gray out
   non-essential elements using `#A0998C`.

3. **Text hierarchy**: Titles in Georgia Bold (serif creates authority), everything
   else in Helvetica. Never use more than 3 font sizes in one chart.

4. **Bar charts**: Default bar width is 0.6. Add direct labels above each bar in
   the primary text color. Round to 1 decimal for percentages, 0 decimals for
   counts.

5. **Line charts**: Line width of 2.5 for primary series, 1.5 for secondary.
   Add endpoint labels. Use dashed lines for benchmarks or averages.

6. **Spines**: Remove top and right spines. Left and bottom spines at 0.3 alpha.

7. **Legend**: Only use a legend when direct labeling is not possible (e.g., 4+
   overlapping lines). Place legends outside the plot area, top-right.

### Applying the Theme

```python
import matplotlib.pyplot as plt

def apply_brand_theme(fig, ax):
    """Apply the brand theme to a matplotlib figure."""
    fig.patch.set_facecolor("#FAFAF5")
    ax.set_facecolor("#FAFAF5")

    # Typography
    ax.set_title(
        ax.get_title(),
        fontfamily="Georgia", fontsize=16, fontweight="bold",
        loc="left", pad=15, color="#2C2C2C"
    )

    # Grid
    ax.grid(axis="y", linestyle="-", alpha=0.2, color="#E8E4DC")
    ax.set_axisbelow(True)

    # Spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_alpha(0.3)
    ax.spines["bottom"].set_alpha(0.3)

    # Axis labels
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily("Helvetica")
        label.set_fontsize(10)

    plt.tight_layout()
```

## Examples

### Example 1: Segment comparison bar chart
```python
fig, ax = plt.subplots(figsize=(10, 6))
segments = ["Enterprise", "Pro", "Free", "Trial"]
engagement = [78, 62, 34, 21]
colors = ["#DAA520", "#2D5F2D", "#2D5F2D", "#2D5F2D"]  # Highlight top segment

bars = ax.bar(segments, engagement, color=colors, width=0.6)
for bar, val in zip(bars, engagement):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
            f"{val}%", ha="center", fontsize=12, fontweight="bold", color="#2C2C2C")

ax.set_title("Enterprise users lead engagement at 78%", loc="left",
             fontfamily="Georgia", fontsize=16, fontweight="bold")
ax.set_ylabel("Engagement Rate (%)")
ax.set_ylim(0, 95)
apply_brand_theme(fig, ax)
```

### Example 2: Trend line with annotation
```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(months, values, color="#2D5F2D", linewidth=2.5)
ax.axhline(y=avg_value, color="#8B4513", linestyle="--", linewidth=1.5, alpha=0.6)
ax.annotate("Campaign launch\n+31% MoM", xy=(launch_month, launch_val),
            fontsize=9, fontstyle="italic", color="#DAA520",
            arrowprops=dict(arrowstyle="->", color="#DAA520"))
ax.set_title("Signups surged 31% after the September campaign", loc="left")
apply_brand_theme(fig, ax)
```

## Anti-Patterns

1. **Never use pure white background** -- always use the warm off-white. Pure white
   looks harsh on projectors and in dark-mode environments.

2. **Never highlight more than 2 elements** -- if everything is highlighted, nothing
   is. Use goldenrod for the one key finding, forest green for everything else.

3. **Never use the full 6-color palette in one chart** -- stick to 2-3 colors max.
   The palette exists for when you have multiple charts that need distinct colors
   across a report.
