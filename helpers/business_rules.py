"""
Business Rules Validation Helpers (DQ-3.3 — Plausibility).

Validates analytical results against business plausibility: value ranges,
computed rates, and year-over-year change thresholds.

Usage:
    from helpers.business_rules import (
        validate_ranges, validate_rates, validate_yoy_change,
    )

    # Check values fall within expected ranges
    rules = [
        {"column": "price", "min": 0, "max": 10000, "name": "product_price"},
        {"column": "quantity", "min": 1, "max": 500, "name": "order_qty"},
    ]
    result = validate_ranges(df, rules)
    print(result["violations"])

    # Check computed rate is within expected bounds
    result = validate_rates(df, "conversions", "sessions", expected_range=(0, 1))
    print(result["rate_stats"])

    # Flag implausible year-over-year changes
    result = validate_yoy_change(1_200_000, 500_000, max_change_pct=2.0)
    print(result["interpretation"])
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Range validation
# ---------------------------------------------------------------------------

def validate_ranges(df, rules):
    """Validate that column values fall within expected ranges.

    For each rule, computes the percentage of values outside the specified
    [min, max] range and classifies severity.

    Args:
        df: pandas.DataFrame to validate.
        rules: List of dicts, each with keys:
            column (str) — column name to check,
            min (numeric) — minimum allowed value (inclusive),
            max (numeric) — maximum allowed value (inclusive),
            name (str) — human-readable rule name.

    Returns:
        dict with keys:
            valid (bool), violations (list of dicts with rule_name/column/
            out_of_range_count/out_of_range_pct/min_seen/max_seen/severity)
    """
    # Edge case: empty DataFrame
    if len(df) == 0:
        violations = []
        for rule in rules:
            violations.append({
                "rule_name": rule.get("name", rule["column"]),
                "column": rule["column"],
                "out_of_range_count": 0,
                "out_of_range_pct": 0.0,
                "min_seen": None,
                "max_seen": None,
                "severity": "PASS",
            })
        return {"valid": True, "violations": violations}

    # Edge case: no rules
    if not rules:
        return {"valid": True, "violations": []}

    violations = []
    for rule in rules:
        col = rule["column"]
        rule_name = rule.get("name", col)
        rule_min = rule.get("min")
        rule_max = rule.get("max")

        # Column does not exist
        if col not in df.columns:
            violations.append({
                "rule_name": rule_name,
                "column": col,
                "out_of_range_count": 0,
                "out_of_range_pct": 0.0,
                "min_seen": None,
                "max_seen": None,
                "severity": "WARNING",
            })
            continue

        series = df[col].dropna()
        n = len(series)

        if n == 0:
            violations.append({
                "rule_name": rule_name,
                "column": col,
                "out_of_range_count": 0,
                "out_of_range_pct": 0.0,
                "min_seen": None,
                "max_seen": None,
                "severity": "WARNING",
            })
            continue

        # Build out-of-range mask
        mask = pd.Series(False, index=series.index)
        if rule_min is not None:
            mask = mask | (series < rule_min)
        if rule_max is not None:
            mask = mask | (series > rule_max)

        out_of_range_count = int(mask.sum())
        out_of_range_pct = float(out_of_range_count / n)
        min_seen = float(series.min())
        max_seen = float(series.max())

        # --- Severity ---
        if out_of_range_pct > 0.05:
            severity = "BLOCKER"
        elif out_of_range_pct > 0:
            severity = "WARNING"
        else:
            severity = "PASS"

        violations.append({
            "rule_name": rule_name,
            "column": col,
            "out_of_range_count": out_of_range_count,
            "out_of_range_pct": round(out_of_range_pct, 6),
            "min_seen": min_seen,
            "max_seen": max_seen,
            "severity": severity,
        })

    # Overall validity
    any_blocker = any(v["severity"] == "BLOCKER" for v in violations)
    any_warning = any(v["severity"] == "WARNING" for v in violations)
    valid = not any_blocker and not any_warning

    return {
        "valid": valid,
        "violations": violations,
    }


# ---------------------------------------------------------------------------
# Rate validation
# ---------------------------------------------------------------------------

def validate_rates(df, numerator_col, denominator_col, expected_range=(0, 1),
                   name="rate"):
    """Validate a computed rate (numerator / denominator).

    Checks that the rate falls within the expected range, and flags
    zero-denominator cases.

    Args:
        df: pandas.DataFrame containing numerator and denominator columns.
        numerator_col: Column name for the numerator.
        denominator_col: Column name for the denominator.
        expected_range: Tuple (min, max) for the expected rate range.
            Default is (0, 1) for typical conversion rates.
        name: Human-readable name for the rate (default 'rate').

    Returns:
        dict with keys:
            valid (bool), out_of_range_count (int),
            zero_denominator_count (int),
            rate_stats (dict with mean/median/min/max),
            severity ('PASS'|'WARNING'|'BLOCKER')
    """
    # Edge case: empty DataFrame
    if len(df) == 0:
        return {
            "valid": True,
            "out_of_range_count": 0,
            "zero_denominator_count": 0,
            "rate_stats": {"mean": None, "median": None, "min": None, "max": None},
            "severity": "PASS",
        }

    # Flag zero denominators
    denom = df[denominator_col]
    zero_denom_mask = (denom == 0) | denom.isna()
    zero_denominator_count = int(zero_denom_mask.sum())

    # Compute rate where denominator is valid
    valid_mask = ~zero_denom_mask
    if valid_mask.sum() == 0:
        return {
            "valid": False,
            "out_of_range_count": 0,
            "zero_denominator_count": zero_denominator_count,
            "rate_stats": {"mean": None, "median": None, "min": None, "max": None},
            "severity": "BLOCKER",
        }

    rates = df.loc[valid_mask, numerator_col] / df.loc[valid_mask, denominator_col]
    rates = rates.dropna()

    range_min, range_max = expected_range
    out_of_range_mask = (rates < range_min) | (rates > range_max)
    out_of_range_count = int(out_of_range_mask.sum())

    rate_stats = {
        "mean": round(float(rates.mean()), 6),
        "median": round(float(rates.median()), 6),
        "min": round(float(rates.min()), 6),
        "max": round(float(rates.max()), 6),
    }

    # --- Severity ---
    out_of_range_pct = out_of_range_count / len(rates) if len(rates) > 0 else 0.0
    if zero_denominator_count > 0 and out_of_range_pct > 0.05:
        severity = "BLOCKER"
    elif out_of_range_count > 0 or zero_denominator_count > 0:
        severity = "WARNING"
    else:
        severity = "PASS"

    valid = severity == "PASS"

    return {
        "valid": valid,
        "out_of_range_count": out_of_range_count,
        "zero_denominator_count": zero_denominator_count,
        "rate_stats": rate_stats,
        "severity": severity,
    }


# ---------------------------------------------------------------------------
# Year-over-year change validation
# ---------------------------------------------------------------------------

def validate_yoy_change(current_value, prior_value, max_change_pct=2.0,
                        metric_name="metric"):
    """Flag implausible year-over-year changes.

    Computes the relative change and flags it if the absolute change
    exceeds max_change_pct (as a fraction, e.g. 2.0 = 200%).

    Args:
        current_value: Current period value (numeric).
        prior_value: Prior period value (numeric).
        max_change_pct: Maximum allowed relative change as a fraction
            (default 2.0 = 200%). E.g., if prior=100 and current=350,
            the change is 250% which exceeds the 200% threshold.
        metric_name: Human-readable name for the metric (default 'metric').

    Returns:
        dict with keys:
            valid (bool), change_pct (float), direction ('up'|'down'|'flat'),
            severity ('PASS'|'WARNING'|'BLOCKER'), interpretation (str)
    """
    # Edge cases: None or NaN
    if current_value is None or prior_value is None:
        return {
            "valid": False,
            "change_pct": None,
            "direction": "flat",
            "severity": "WARNING",
            "interpretation": f"Cannot compute YoY change for {metric_name} — missing value(s).",
        }

    current_value = float(current_value)
    prior_value = float(prior_value)

    if np.isnan(current_value) or np.isnan(prior_value):
        return {
            "valid": False,
            "change_pct": None,
            "direction": "flat",
            "severity": "WARNING",
            "interpretation": f"Cannot compute YoY change for {metric_name} — NaN value(s).",
        }

    # Edge case: prior value is zero
    if prior_value == 0:
        if current_value == 0:
            return {
                "valid": True,
                "change_pct": 0.0,
                "direction": "flat",
                "severity": "PASS",
                "interpretation": f"{metric_name}: no change (both periods are zero).",
            }
        return {
            "valid": False,
            "change_pct": float("inf"),
            "direction": "up" if current_value > 0 else "down",
            "severity": "BLOCKER",
            "interpretation": (
                f"{metric_name}: prior value is zero, current is "
                f"{current_value:,.2f} — infinite change. Verify data."
            ),
        }

    # Compute change
    change = (current_value - prior_value) / abs(prior_value)
    change_pct = round(abs(change), 6)

    if change > 0:
        direction = "up"
    elif change < 0:
        direction = "down"
    else:
        direction = "flat"

    # --- Severity ---
    if change_pct > max_change_pct:
        severity = "BLOCKER"
        interpretation = (
            f"{metric_name}: {direction} {change_pct:.1%} YoY "
            f"({prior_value:,.2f} -> {current_value:,.2f}). "
            f"Exceeds {max_change_pct:.0%} threshold — verify this is real."
        )
    elif change_pct > max_change_pct * 0.5:
        severity = "WARNING"
        interpretation = (
            f"{metric_name}: {direction} {change_pct:.1%} YoY "
            f"({prior_value:,.2f} -> {current_value:,.2f}). "
            f"Large change — worth investigating."
        )
    else:
        severity = "PASS"
        interpretation = (
            f"{metric_name}: {direction} {change_pct:.1%} YoY "
            f"({prior_value:,.2f} -> {current_value:,.2f}). "
            f"Within expected range."
        )

    valid = severity == "PASS"

    return {
        "valid": valid,
        "change_pct": change_pct,
        "direction": direction,
        "severity": severity,
        "interpretation": interpretation,
    }
