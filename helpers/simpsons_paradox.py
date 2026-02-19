"""
Simpson's Paradox Scanner (DQ-3.5).

Scans analytical results for Simpson's Paradox — where a trend that
appears in aggregated data reverses when the data is split into segments.
This is one of the most dangerous analytical errors because the aggregate
conclusion is literally the opposite of what each segment shows.

Usage:
    from helpers.simpsons_paradox import (
        check_simpsons_paradox, scan_dimensions,
    )

    # Check a single dimension for reversal
    result = check_simpsons_paradox(
        df, metric_col="conversion_rate",
        group_col="variant", segment_col="device_type",
    )
    if result["paradox_detected"]:
        print(result["explanation"])

    # Scan multiple candidate dimensions
    result = scan_dimensions(
        df, metric_col="conversion_rate",
        group_col="variant",
        candidate_segments=["device_type", "region", "plan"],
    )
    print(f"Paradoxes found: {result['paradoxes_found']}")
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Core paradox check
# ---------------------------------------------------------------------------

def check_simpsons_paradox(df, metric_col, group_col, segment_col):
    """Check for Simpson's Paradox across a single segmentation dimension.

    Compares the metric direction (group A > group B) at the aggregate
    level versus within each segment. A paradox is detected when the
    aggregate direction is opposite to the direction in the majority of
    segments.

    The function identifies exactly two groups from group_col (the two
    most common values). If more than two groups exist, only the top two
    by row count are compared.

    Args:
        df: pandas.DataFrame containing the data.
        metric_col: Column name of the metric to compare (numeric).
        group_col: Column name defining the two groups (e.g., 'variant',
            'channel', 'platform').
        segment_col: Column name defining the segments to check within
            (e.g., 'device_type', 'region', 'plan_tier').

    Returns:
        dict with keys:
            paradox_detected (bool),
            aggregate_direction (str — 'A>B', 'B>A', or 'equal'),
            segment_directions (list of dicts with segment/direction/
                group_a_val/group_b_val),
            reversal_segments (list of segment names where direction
                reversed),
            explanation (str — human-readable interpretation),
            severity ('PASS'|'INFO'|'BLOCKER')
    """
    # Edge case: empty DataFrame
    if len(df) == 0:
        return _empty_result("DataFrame is empty — cannot check for paradox.")

    # Edge case: all-null metric or group column
    working = df.dropna(subset=[metric_col, group_col, segment_col])
    if len(working) < 2:
        return _empty_result(
            "Insufficient non-null data to check for paradox."
        )

    # Identify the two groups (top 2 by frequency)
    group_counts = working[group_col].value_counts()
    if len(group_counts) < 2:
        return _empty_result(
            f"Only one group found in '{group_col}' — need at least two."
        )

    group_a_label = group_counts.index[0]
    group_b_label = group_counts.index[1]

    subset = working[working[group_col].isin([group_a_label, group_b_label])]

    # --- Aggregate comparison ---
    agg = subset.groupby(group_col)[metric_col].mean()
    agg_a = float(agg.get(group_a_label, 0))
    agg_b = float(agg.get(group_b_label, 0))

    if agg_a > agg_b:
        aggregate_direction = "A>B"
    elif agg_b > agg_a:
        aggregate_direction = "B>A"
    else:
        aggregate_direction = "equal"

    # --- Segment-level comparison ---
    segment_directions = []
    for segment_value, seg_df in subset.groupby(segment_col):
        seg_agg = seg_df.groupby(group_col)[metric_col].mean()
        seg_a = float(seg_agg.get(group_a_label, 0))
        seg_b = float(seg_agg.get(group_b_label, 0))

        if seg_a > seg_b:
            seg_direction = "A>B"
        elif seg_b > seg_a:
            seg_direction = "B>A"
        else:
            seg_direction = "equal"

        segment_directions.append({
            "segment": segment_value,
            "direction": seg_direction,
            "group_a_val": round(seg_a, 6),
            "group_b_val": round(seg_b, 6),
        })

    # --- Detect paradox ---
    # A paradox exists when the aggregate direction is opposite to the
    # majority of non-equal segment directions.
    non_equal_segments = [
        s for s in segment_directions if s["direction"] != "equal"
    ]

    if len(non_equal_segments) == 0 or aggregate_direction == "equal":
        return {
            "paradox_detected": False,
            "aggregate_direction": aggregate_direction,
            "segment_directions": segment_directions,
            "reversal_segments": [],
            "explanation": (
                f"No directional comparison possible — "
                f"aggregate is '{aggregate_direction}', "
                f"{len(non_equal_segments)} segments have a clear direction."
            ),
            "severity": "PASS",
        }

    # Count how many segments agree vs disagree with aggregate
    opposite = "B>A" if aggregate_direction == "A>B" else "A>B"
    reversal_segments = [
        s["segment"] for s in non_equal_segments if s["direction"] == opposite
    ]
    agree_count = len(non_equal_segments) - len(reversal_segments)

    paradox_detected = len(reversal_segments) > agree_count

    # --- Build explanation ---
    if paradox_detected:
        explanation = (
            f"Simpson's Paradox detected on '{segment_col}'. "
            f"Aggregate: {group_a_label} {'>' if aggregate_direction == 'A>B' else '<'} "
            f"{group_b_label} (mean {metric_col}: {agg_a:.4f} vs {agg_b:.4f}). "
            f"But in {len(reversal_segments)} of {len(non_equal_segments)} segments, "
            f"the direction reverses. "
            f"Reversing segments: {reversal_segments}. "
            f"The aggregate result is misleading — segment-level analysis is required."
        )
        severity = "BLOCKER"
    else:
        explanation = (
            f"No paradox on '{segment_col}'. "
            f"Aggregate: {group_a_label} {'>' if aggregate_direction == 'A>B' else '<'} "
            f"{group_b_label}. "
            f"{agree_count} of {len(non_equal_segments)} segments agree with aggregate direction."
        )
        if len(reversal_segments) > 0:
            explanation += (
                f" Note: {len(reversal_segments)} segment(s) show reversal: "
                f"{reversal_segments} — worth investigating."
            )
            severity = "INFO"
        else:
            severity = "PASS"

    return {
        "paradox_detected": paradox_detected,
        "aggregate_direction": aggregate_direction,
        "segment_directions": segment_directions,
        "reversal_segments": reversal_segments,
        "explanation": explanation,
        "severity": severity,
    }


def _empty_result(message):
    """Return a default result dict for edge cases.

    Args:
        message: Explanation string for why the check could not run.

    Returns:
        dict with paradox_detected=False and the message as explanation.
    """
    return {
        "paradox_detected": False,
        "aggregate_direction": "equal",
        "segment_directions": [],
        "reversal_segments": [],
        "explanation": message,
        "severity": "PASS",
    }


# ---------------------------------------------------------------------------
# Multi-dimension scanner
# ---------------------------------------------------------------------------

def scan_dimensions(df, metric_col, group_col, candidate_segments):
    """Scan multiple candidate segment columns for Simpson's Paradox.

    Runs check_simpsons_paradox for each candidate segment and aggregates
    results into a summary.

    Args:
        df: pandas.DataFrame containing the data.
        metric_col: Column name of the metric to compare (numeric).
        group_col: Column name defining the two groups.
        candidate_segments: List of column names to scan as potential
            confounding segments.

    Returns:
        dict with keys:
            scanned (int — number of dimensions checked),
            paradoxes_found (int),
            results (list of check_simpsons_paradox results, one per
                candidate segment),
            interpretation (str — human-readable summary)
    """
    # Edge case: no candidates
    if not candidate_segments:
        return {
            "scanned": 0,
            "paradoxes_found": 0,
            "results": [],
            "interpretation": "No candidate segments provided — nothing to scan.",
        }

    results = []
    paradox_count = 0

    for seg_col in candidate_segments:
        # Skip if column does not exist in the DataFrame
        if seg_col not in df.columns:
            results.append({
                "paradox_detected": False,
                "aggregate_direction": "equal",
                "segment_directions": [],
                "reversal_segments": [],
                "explanation": f"Column '{seg_col}' not found in DataFrame.",
                "severity": "WARNING",
            })
            continue

        result = check_simpsons_paradox(df, metric_col, group_col, seg_col)
        results.append(result)
        if result["paradox_detected"]:
            paradox_count += 1

    # --- Interpretation ---
    if paradox_count == 0:
        interpretation = (
            f"Scanned {len(candidate_segments)} dimension(s) for Simpson's "
            f"Paradox — none detected. Aggregate results are consistent "
            f"with segment-level patterns."
        )
    else:
        paradox_dims = [
            candidate_segments[i]
            for i, r in enumerate(results)
            if r["paradox_detected"]
        ]
        interpretation = (
            f"Simpson's Paradox detected in {paradox_count} of "
            f"{len(candidate_segments)} dimension(s): {paradox_dims}. "
            f"Aggregate conclusions may be misleading — segment-level "
            f"analysis is required before drawing conclusions."
        )

    return {
        "scanned": len(candidate_segments),
        "paradoxes_found": paradox_count,
        "results": results,
        "interpretation": interpretation,
    }
