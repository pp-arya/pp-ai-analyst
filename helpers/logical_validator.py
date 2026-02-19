"""
Logical Validation Helpers (DQ-3.2 — Layer 3).

Validates LOGICAL consistency of analytical results: aggregation integrity,
trend continuity, segment exhaustiveness, and temporal consistency.

Usage:
    from helpers.logical_validator import (
        validate_aggregation_consistency, validate_trend_continuity,
        validate_segment_exhaustiveness, validate_temporal_consistency,
    )

    # Verify detail rows sum to summary
    result = validate_aggregation_consistency(
        detail_df, summary_df, group_col="region",
        metric_col="revenue", agg="sum",
    )
    print(result["mismatches"])

    # Check for sudden jumps in a time series
    result = validate_trend_continuity(monthly_revenue, max_gap_pct=0.5)
    print(result["breaks"])
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Aggregation consistency
# ---------------------------------------------------------------------------

def validate_aggregation_consistency(detail_df, summary_df, group_col,
                                     metric_col, agg="sum", tolerance=0.01):
    """Re-aggregate detail_df and compare to summary_df.

    Flags groups where the re-aggregated value differs from the summary
    value beyond the specified tolerance.

    Args:
        detail_df: pandas.DataFrame with row-level detail data.
        summary_df: pandas.DataFrame with pre-aggregated summary data.
        group_col: Column name to group by (must exist in both DataFrames).
        metric_col: Column name of the metric to aggregate.
        agg: Aggregation function — 'sum', 'mean', 'count', 'min', 'max'.
            Default is 'sum'.
        tolerance: Relative tolerance for mismatch detection (default 0.01
            = 1%).

    Returns:
        dict with keys:
            valid (bool), mismatches (list of dicts with group/expected/
            actual/diff_pct), severity ('PASS'|'WARNING'|'BLOCKER')
    """
    # Edge case: empty DataFrames
    if len(detail_df) == 0 and len(summary_df) == 0:
        return {
            "valid": True,
            "mismatches": [],
            "severity": "PASS",
        }

    if len(detail_df) == 0 or len(summary_df) == 0:
        return {
            "valid": False,
            "mismatches": [],
            "severity": "BLOCKER",
        }

    # Re-aggregate detail data
    re_agg = detail_df.groupby(group_col)[metric_col].agg(agg).reset_index()
    re_agg.columns = [group_col, "expected"]

    # Merge with summary
    summary_subset = summary_df[[group_col, metric_col]].copy()
    summary_subset.columns = [group_col, "actual"]

    merged = pd.merge(re_agg, summary_subset, on=group_col, how="outer")

    mismatches = []
    for _, row in merged.iterrows():
        expected = row.get("expected")
        actual = row.get("actual")

        # Handle NaN / missing on either side
        if pd.isna(expected) or pd.isna(actual):
            mismatches.append({
                "group": row[group_col],
                "expected": None if pd.isna(expected) else float(expected),
                "actual": None if pd.isna(actual) else float(actual),
                "diff_pct": None,
            })
            continue

        expected = float(expected)
        actual = float(actual)

        # Compute relative difference
        denominator = abs(expected) if expected != 0 else abs(actual)
        if denominator == 0:
            diff_pct = 0.0
        else:
            diff_pct = abs(actual - expected) / denominator

        if diff_pct > tolerance:
            mismatches.append({
                "group": row[group_col],
                "expected": expected,
                "actual": actual,
                "diff_pct": round(diff_pct, 6),
            })

    # --- Severity ---
    if len(mismatches) == 0:
        severity = "PASS"
    elif any(m["diff_pct"] is None or m["diff_pct"] > 0.05 for m in mismatches):
        severity = "BLOCKER"
    else:
        severity = "WARNING"

    valid = severity == "PASS"

    return {
        "valid": valid,
        "mismatches": mismatches,
        "severity": severity,
    }


# ---------------------------------------------------------------------------
# Trend continuity
# ---------------------------------------------------------------------------

def validate_trend_continuity(series, max_gap_pct=0.5):
    """Check for sudden jumps (structural breaks) in a numeric series.

    Flags any period-over-period change that exceeds max_gap_pct as a
    fraction of the previous value.

    Args:
        series: Array-like or pandas.Series of numeric values (ordered
            chronologically). Index is preserved for break location reporting.
        max_gap_pct: Maximum allowed period-over-period change as a fraction
            (default 0.5 = 50%).

    Returns:
        dict with keys:
            valid (bool), breaks (list of dicts with index/prev_value/
            curr_value/change_pct), severity ('PASS'|'WARNING'|'BLOCKER')
    """
    s = pd.Series(series).dropna()

    # Edge case: too few data points to detect breaks
    if len(s) < 2:
        return {
            "valid": True,
            "breaks": [],
            "severity": "PASS",
        }

    breaks = []
    values = s.values
    indices = s.index.tolist()

    for i in range(1, len(values)):
        prev_val = float(values[i - 1])
        curr_val = float(values[i])

        # Skip zero-denominator (cannot compute relative change)
        if prev_val == 0:
            if curr_val != 0:
                breaks.append({
                    "index": indices[i],
                    "prev_value": prev_val,
                    "curr_value": curr_val,
                    "change_pct": float("inf"),
                })
            continue

        change_pct = abs(curr_val - prev_val) / abs(prev_val)
        if change_pct > max_gap_pct:
            breaks.append({
                "index": indices[i],
                "prev_value": prev_val,
                "curr_value": curr_val,
                "change_pct": round(change_pct, 6),
            })

    # --- Severity ---
    if len(breaks) == 0:
        severity = "PASS"
    elif len(breaks) <= 2:
        severity = "WARNING"
    else:
        severity = "BLOCKER"

    valid = severity == "PASS"

    return {
        "valid": valid,
        "breaks": breaks,
        "severity": severity,
    }


# ---------------------------------------------------------------------------
# Segment exhaustiveness
# ---------------------------------------------------------------------------

def validate_segment_exhaustiveness(df, segment_col, metric_col):
    """Verify segments are mutually exclusive and collectively exhaustive.

    Checks that the sum of segment-level metric values equals the overall
    total (within tolerance) and that no row belongs to multiple segments.

    Args:
        df: pandas.DataFrame containing the data.
        segment_col: Column name defining the segment (e.g., 'region',
            'plan_type').
        metric_col: Column name of the metric to verify (e.g., 'revenue').

    Returns:
        dict with keys:
            valid (bool), segment_sum (float), total (float), diff_pct (float),
            missing_rows (int), severity ('PASS'|'WARNING'|'BLOCKER')
    """
    # Edge case: empty DataFrame
    if len(df) == 0:
        return {
            "valid": True,
            "segment_sum": 0.0,
            "total": 0.0,
            "diff_pct": 0.0,
            "missing_rows": 0,
            "severity": "PASS",
        }

    total = float(df[metric_col].sum())
    segment_sum = float(df.groupby(segment_col)[metric_col].sum().sum())

    # Relative difference
    denominator = abs(total) if total != 0 else abs(segment_sum)
    if denominator == 0:
        diff_pct = 0.0
    else:
        diff_pct = abs(segment_sum - total) / denominator

    # Check for rows with null segment (missing from segmentation)
    null_segment_mask = df[segment_col].isna()
    missing_rows = int(null_segment_mask.sum())

    # --- Severity ---
    tolerance = 0.001
    if diff_pct > 0.01 or missing_rows > 0:
        severity = "BLOCKER"
    elif diff_pct > tolerance:
        severity = "WARNING"
    else:
        severity = "PASS"

    valid = severity == "PASS"

    return {
        "valid": valid,
        "segment_sum": round(segment_sum, 6),
        "total": round(total, 6),
        "diff_pct": round(diff_pct, 6),
        "missing_rows": missing_rows,
        "severity": severity,
    }


# ---------------------------------------------------------------------------
# Temporal consistency
# ---------------------------------------------------------------------------

def validate_temporal_consistency(df, date_col, metric_col, expected_freq="D"):
    """Check for missing dates, duplicate dates, and zero-value gaps.

    Identifies gaps in the expected date sequence, duplicate entries for
    the same date, and dates where the metric is 0 or null in the middle
    of an otherwise active range.

    Args:
        df: pandas.DataFrame containing the time series data.
        date_col: Column name containing date/datetime values.
        metric_col: Column name of the metric to check for zero/null gaps.
        expected_freq: Expected frequency — 'D' (daily), 'W' (weekly),
            'M' (monthly), etc. Default is 'D'.

    Returns:
        dict with keys:
            valid (bool), missing_dates (list of date strings),
            duplicate_dates (list of date strings),
            zero_dates (list of date strings),
            severity ('PASS'|'WARNING'|'BLOCKER')
    """
    # Edge case: empty DataFrame
    if len(df) == 0:
        return {
            "valid": True,
            "missing_dates": [],
            "duplicate_dates": [],
            "zero_dates": [],
            "severity": "PASS",
        }

    # Parse dates
    dates = pd.to_datetime(df[date_col])

    # --- Duplicate dates ---
    date_counts = dates.value_counts()
    duplicate_dates = sorted(
        str(d.date()) if hasattr(d, "date") else str(d)
        for d in date_counts[date_counts > 1].index
    )

    # --- Missing dates ---
    min_date = dates.min()
    max_date = dates.max()

    # Edge case: single date — no gaps possible
    if min_date == max_date:
        return {
            "valid": len(duplicate_dates) == 0,
            "missing_dates": [],
            "duplicate_dates": duplicate_dates,
            "zero_dates": [],
            "severity": "WARNING" if duplicate_dates else "PASS",
        }

    expected_range = pd.date_range(start=min_date, end=max_date, freq=expected_freq)
    actual_dates = set(dates.dt.normalize())
    expected_dates = set(expected_range.normalize())
    missing = sorted(expected_dates - actual_dates)
    missing_dates = [str(d.date()) for d in missing]

    # --- Zero / null dates in the middle of the active range ---
    # Only flag zeros/nulls that are not at the very start or end
    working = df.copy()
    working["_parsed_date"] = dates
    working = working.sort_values("_parsed_date")

    # Find dates where metric is 0 or null (excluding first and last dates)
    inner = working.iloc[1:-1] if len(working) > 2 else pd.DataFrame()
    zero_dates = []
    if len(inner) > 0:
        zero_mask = inner[metric_col].isna() | (inner[metric_col] == 0)
        zero_dates = sorted(
            str(d.date()) if hasattr(d, "date") else str(d)
            for d in inner.loc[zero_mask, "_parsed_date"]
        )

    # --- Severity ---
    n_issues = len(missing_dates) + len(duplicate_dates) + len(zero_dates)
    total_expected = len(expected_range)
    issue_rate = n_issues / total_expected if total_expected > 0 else 0.0

    if len(duplicate_dates) > 0 or issue_rate > 0.1:
        severity = "BLOCKER"
    elif n_issues > 0:
        severity = "WARNING"
    else:
        severity = "PASS"

    valid = severity == "PASS"

    return {
        "valid": valid,
        "missing_dates": missing_dates,
        "duplicate_dates": duplicate_dates,
        "zero_dates": zero_dates,
        "severity": severity,
    }
