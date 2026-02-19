"""
Structural Validation Helpers (DQ-3.1 — Layer 1).

Validates the STRUCTURE of data before analysis begins: schema conformance,
primary key integrity, referential integrity, and column completeness.

Usage:
    from helpers.structural_validator import (
        validate_schema, validate_primary_key,
        validate_referential_integrity, validate_completeness,
    )

    # Check schema matches expectations
    result = validate_schema(df, expected_columns=["user_id", "revenue"])
    print(result["severity"])  # 'PASS', 'WARNING', or 'BLOCKER'

    # Check primary key has no nulls or duplicates
    result = validate_primary_key(df, key_columns=["order_id"])
    print(result["duplicate_count"])

    # Verify foreign key relationships
    result = validate_referential_integrity(
        parent_df=users, child_df=orders,
        parent_key="user_id", child_key="user_id",
    )
    print(result["orphan_rate"])
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Compatible dtype groups
# ---------------------------------------------------------------------------

_NUMERIC_DTYPES = {"int8", "int16", "int32", "int64",
                   "uint8", "uint16", "uint32", "uint64",
                   "float16", "float32", "float64"}
_DATETIME_DTYPES = {"datetime64[ns]", "datetime64[us]", "datetime64[ms]",
                    "datetime64[s]"}
_STRING_DTYPES = {"object", "string", "str"}


def _dtypes_compatible(actual, expected):
    """Check whether two dtype names are compatible.

    Allows int64/float64 to match (both numeric), various datetime
    precisions to match, and object/string to match.

    Args:
        actual: The dtype name from the DataFrame (str).
        expected: The expected dtype name (str).

    Returns:
        bool: True if the dtypes are compatible.
    """
    actual_str = str(actual).lower()
    expected_str = str(expected).lower()

    if actual_str == expected_str:
        return True

    # Numeric family
    if actual_str in _NUMERIC_DTYPES and expected_str in _NUMERIC_DTYPES:
        return True

    # Datetime family
    if actual_str in _DATETIME_DTYPES and expected_str in _DATETIME_DTYPES:
        return True

    # String family
    if actual_str in _STRING_DTYPES and expected_str in _STRING_DTYPES:
        return True

    return False


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def validate_schema(df, expected_columns=None, expected_dtypes=None):
    """Validate that a DataFrame conforms to the expected schema.

    Checks that all expected columns exist, that dtypes match (allowing
    compatible types like int64/float64), and flags any unexpected columns
    as INFO-level findings.

    Args:
        df: pandas.DataFrame to validate.
        expected_columns: Optional list of column names that must be present.
            If None, the check is skipped.
        expected_dtypes: Optional dict of {column_name: expected_dtype_str}.
            Compatible types (e.g., int64 and float64) are accepted as matches.
            If None, dtype checking is skipped.

    Returns:
        dict with keys:
            valid (bool), missing_columns (list), dtype_mismatches (list of
            dicts with column/expected/actual), extra_columns (list),
            severity ('PASS'|'WARNING'|'BLOCKER')
    """
    # Edge case: empty DataFrame with no columns
    if df is None or (isinstance(df, pd.DataFrame) and df.columns.empty):
        return {
            "valid": expected_columns is None or len(expected_columns) == 0,
            "missing_columns": list(expected_columns) if expected_columns else [],
            "dtype_mismatches": [],
            "extra_columns": [],
            "severity": "BLOCKER" if expected_columns else "PASS",
        }

    actual_columns = set(df.columns.tolist())

    # --- Missing columns ---
    missing_columns = []
    if expected_columns is not None:
        missing_columns = [c for c in expected_columns if c not in actual_columns]

    # --- Extra columns (INFO-level, not a problem) ---
    expected_set = set(expected_columns) if expected_columns else set()
    extra_columns = sorted(actual_columns - expected_set) if expected_columns else []

    # --- Dtype mismatches ---
    dtype_mismatches = []
    if expected_dtypes is not None:
        for col, expected_dtype in expected_dtypes.items():
            if col not in actual_columns:
                continue  # already captured in missing_columns
            actual_dtype = str(df[col].dtype)
            if not _dtypes_compatible(actual_dtype, expected_dtype):
                dtype_mismatches.append({
                    "column": col,
                    "expected": str(expected_dtype),
                    "actual": actual_dtype,
                })

    # --- Severity ---
    if missing_columns:
        severity = "BLOCKER"
    elif dtype_mismatches:
        severity = "WARNING"
    else:
        severity = "PASS"

    valid = severity == "PASS"

    return {
        "valid": valid,
        "missing_columns": missing_columns,
        "dtype_mismatches": dtype_mismatches,
        "extra_columns": extra_columns,
        "severity": severity,
    }


# ---------------------------------------------------------------------------
# Primary key validation
# ---------------------------------------------------------------------------

def validate_primary_key(df, key_columns):
    """Validate that a composite primary key has no nulls or duplicates.

    Args:
        df: pandas.DataFrame to validate.
        key_columns: List of column names forming the primary key.

    Returns:
        dict with keys:
            valid (bool), null_count (int), duplicate_count (int),
            duplicate_examples (DataFrame — first 5 duplicate rows),
            severity ('PASS'|'WARNING'|'BLOCKER')
    """
    # Edge case: empty DataFrame
    if len(df) == 0:
        return {
            "valid": True,
            "null_count": 0,
            "duplicate_count": 0,
            "duplicate_examples": pd.DataFrame(),
            "severity": "PASS",
        }

    # Edge case: single row — by definition unique
    if len(df) == 1:
        null_count = int(df[key_columns].isna().any(axis=1).sum())
        return {
            "valid": null_count == 0,
            "null_count": null_count,
            "duplicate_count": 0,
            "duplicate_examples": pd.DataFrame(),
            "severity": "BLOCKER" if null_count > 0 else "PASS",
        }

    # --- Null check ---
    null_mask = df[key_columns].isna().any(axis=1)
    null_count = int(null_mask.sum())

    # --- Duplicate check ---
    dup_mask = df.duplicated(subset=key_columns, keep=False)
    duplicate_rows = df[dup_mask]
    duplicate_count = int(duplicate_rows.drop_duplicates(subset=key_columns).shape[0])
    duplicate_examples = duplicate_rows.head(5).copy()

    # --- Severity ---
    if null_count > 0 or duplicate_count > 0:
        severity = "BLOCKER"
    else:
        severity = "PASS"

    valid = severity == "PASS"

    return {
        "valid": valid,
        "null_count": null_count,
        "duplicate_count": duplicate_count,
        "duplicate_examples": duplicate_examples,
        "severity": severity,
    }


# ---------------------------------------------------------------------------
# Referential integrity validation
# ---------------------------------------------------------------------------

def validate_referential_integrity(parent_df, child_df, parent_key, child_key):
    """Verify that all child_key values exist in the parent_key.

    Computes the orphan rate (percentage of child rows whose key value does
    not appear in the parent table).

    Args:
        parent_df: pandas.DataFrame containing the parent (lookup) table.
        child_df: pandas.DataFrame containing the child (fact) table.
        parent_key: Column name in parent_df.
        child_key: Column name in child_df.

    Returns:
        dict with keys:
            valid (bool), orphan_count (int), orphan_rate (float),
            orphan_examples (list — first 10 orphan values),
            severity ('PASS'|'WARNING'|'BLOCKER')
    """
    # Edge case: empty child DataFrame — nothing to check
    if len(child_df) == 0:
        return {
            "valid": True,
            "orphan_count": 0,
            "orphan_rate": 0.0,
            "orphan_examples": [],
            "severity": "PASS",
        }

    parent_values = set(parent_df[parent_key].dropna().unique())
    child_values = child_df[child_key].dropna()

    orphan_mask = ~child_values.isin(parent_values)
    orphan_count = int(orphan_mask.sum())
    orphan_rate = float(orphan_count / len(child_df)) if len(child_df) > 0 else 0.0

    orphan_examples = child_values[orphan_mask].unique().tolist()[:10]

    # --- Severity ---
    if orphan_rate > 0.05:
        severity = "BLOCKER"
    elif orphan_rate > 0:
        severity = "WARNING"
    else:
        severity = "PASS"

    valid = severity == "PASS"

    return {
        "valid": valid,
        "orphan_count": orphan_count,
        "orphan_rate": round(orphan_rate, 6),
        "orphan_examples": orphan_examples,
        "severity": severity,
    }


# ---------------------------------------------------------------------------
# Completeness validation
# ---------------------------------------------------------------------------

def validate_completeness(df, required_columns=None, threshold=0.05):
    """Check null rates across columns and classify severity.

    For each column (or a specified subset), computes the null rate and
    classifies: PASS (<threshold), WARNING (threshold to 0.2),
    BLOCKER (>0.2).

    Args:
        df: pandas.DataFrame to validate.
        required_columns: Optional list of column names to check. If None,
            checks all columns.
        threshold: Null rate below which a column is considered PASS
            (default 0.05 = 5%).

    Returns:
        dict with keys:
            columns (list of dicts with name/null_count/null_rate/severity),
            overall_severity ('PASS'|'WARNING'|'BLOCKER'),
            summary_text (str)
    """
    columns_to_check = required_columns if required_columns else df.columns.tolist()
    n = len(df)

    # Edge case: empty DataFrame
    if n == 0:
        column_results = [
            {
                "name": col,
                "null_count": 0,
                "null_rate": 0.0,
                "severity": "PASS",
            }
            for col in columns_to_check
        ]
        return {
            "columns": column_results,
            "overall_severity": "WARNING",
            "summary_text": "DataFrame is empty — no data to assess completeness.",
        }

    column_results = []
    for col in columns_to_check:
        if col not in df.columns:
            column_results.append({
                "name": col,
                "null_count": n,
                "null_rate": 1.0,
                "severity": "BLOCKER",
            })
            continue

        null_count = int(df[col].isna().sum())
        null_rate = float(null_count / n)

        if null_rate > 0.2:
            severity = "BLOCKER"
        elif null_rate >= threshold:
            severity = "WARNING"
        else:
            severity = "PASS"

        column_results.append({
            "name": col,
            "null_count": null_count,
            "null_rate": round(null_rate, 6),
            "severity": severity,
        })

    # --- Roll up severity ---
    severities = {c["severity"] for c in column_results}
    if "BLOCKER" in severities:
        overall_severity = "BLOCKER"
    elif "WARNING" in severities:
        overall_severity = "WARNING"
    else:
        overall_severity = "PASS"

    # --- Summary text ---
    blocker_cols = [c["name"] for c in column_results if c["severity"] == "BLOCKER"]
    warning_cols = [c["name"] for c in column_results if c["severity"] == "WARNING"]

    parts = []
    if blocker_cols:
        parts.append(f"{len(blocker_cols)} column(s) with >20% nulls: {blocker_cols}")
    if warning_cols:
        parts.append(f"{len(warning_cols)} column(s) with elevated nulls: {warning_cols}")
    if not parts:
        parts.append(f"All {len(column_results)} column(s) within acceptable null thresholds.")

    summary_text = " ".join(parts)

    return {
        "columns": column_results,
        "overall_severity": overall_severity,
        "summary_text": summary_text,
    }
