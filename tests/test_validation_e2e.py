"""
End-to-end integration test: Full validation pipeline on NovaMart data.

Tests the complete chain:
1. Load actual NovaMart CSV data (users, orders, products, events, sessions)
2. Layer 1: Structural validation (schema, PK, RI, completeness)
3. Layer 2: Logical validation (aggregation, segment, temporal, trend)
4. Layer 3: Business rules (ranges, rates)
5. Layer 4: Simpson's Paradox scan
6. Confidence scoring synthesis (7-factor → score/grade/badge)
7. Lineage tracking (record → chain → save/load)

This is the capstone integration test for the DQ workstream (DQ-4.4).
"""

import os
import tempfile

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(REPO_ROOT, "data", "novamart")

# Skip entire module if NovaMart CSVs are missing
pytestmark = pytest.mark.skipif(
    not os.path.isdir(DATA_DIR),
    reason="NovaMart data directory not found",
)


# ============================================================
# Fixtures: load NovaMart tables once per session
# ============================================================

@pytest.fixture(scope="module")
def users():
    return pd.read_csv(os.path.join(DATA_DIR, "users.csv"))


@pytest.fixture(scope="module")
def orders():
    return pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))


@pytest.fixture(scope="module")
def products():
    return pd.read_csv(os.path.join(DATA_DIR, "products.csv"))


@pytest.fixture(scope="module")
def events():
    # Only load first 50k rows to keep tests fast
    return pd.read_csv(os.path.join(DATA_DIR, "events.csv"), nrows=50000)


@pytest.fixture(scope="module")
def sessions():
    return pd.read_csv(os.path.join(DATA_DIR, "sessions.csv"), nrows=50000)


@pytest.fixture(scope="module")
def order_items():
    return pd.read_csv(os.path.join(DATA_DIR, "order_items.csv"))


# ============================================================
# Layer 1: Structural Validation
# ============================================================

class TestStructuralValidation:
    """Layer 1: Schema, PK, RI, completeness on NovaMart tables."""

    def test_users_schema_passes(self, users):
        from helpers.structural_validator import validate_schema
        result = validate_schema(
            users,
            expected_columns=["user_id", "signup_date", "acquisition_channel",
                              "country", "device_primary"],
        )
        assert result["severity"] == "PASS"
        assert result["valid"] is True
        assert len(result["missing_columns"]) == 0

    def test_users_primary_key_valid(self, users):
        from helpers.structural_validator import validate_primary_key
        result = validate_primary_key(users, key_columns=["user_id"])
        assert result["severity"] == "PASS"
        assert result["null_count"] == 0
        assert result["duplicate_count"] == 0

    def test_orders_primary_key_valid(self, orders):
        from helpers.structural_validator import validate_primary_key
        result = validate_primary_key(orders, key_columns=["order_id"])
        assert result["severity"] == "PASS"

    def test_products_primary_key_valid(self, products):
        from helpers.structural_validator import validate_primary_key
        result = validate_primary_key(products, key_columns=["product_id"])
        assert result["severity"] == "PASS"

    def test_orders_users_referential_integrity(self, users, orders):
        from helpers.structural_validator import validate_referential_integrity
        result = validate_referential_integrity(
            parent_df=users, child_df=orders,
            parent_key="user_id", child_key="user_id",
        )
        # Expect low orphan rate (seed data is clean)
        assert result["orphan_rate"] < 0.05
        assert result["severity"] in ("PASS", "WARNING")

    def test_events_users_referential_integrity(self, users, events):
        from helpers.structural_validator import validate_referential_integrity
        result = validate_referential_integrity(
            parent_df=users, child_df=events,
            parent_key="user_id", child_key="user_id",
        )
        assert result["orphan_rate"] < 0.05

    def test_users_completeness(self, users):
        from helpers.structural_validator import validate_completeness
        result = validate_completeness(
            users,
            required_columns=["user_id", "signup_date", "acquisition_channel",
                              "country", "device_primary"],
        )
        # Core columns should have low null rates
        assert result["overall_severity"] in ("PASS", "WARNING")
        for col_info in result["columns"]:
            if col_info["name"] == "user_id":
                assert col_info["null_rate"] == 0.0

    def test_orders_completeness(self, orders):
        from helpers.structural_validator import validate_completeness
        result = validate_completeness(
            orders,
            required_columns=["order_id", "user_id", "order_date", "total_amount"],
        )
        # order_id and user_id should be 100% complete
        for col_info in result["columns"]:
            if col_info["name"] in ("order_id", "user_id"):
                assert col_info["null_rate"] == 0.0


# ============================================================
# Layer 2: Logical Validation
# ============================================================

class TestLogicalValidation:
    """Layer 2: Aggregation, segment, temporal, trend checks."""

    def test_orders_aggregate_by_status(self, orders):
        """Re-aggregate order totals by status and verify consistency."""
        from helpers.logical_validator import validate_aggregation_consistency

        detail = orders[["status", "total_amount"]].copy()
        summary = (
            detail.groupby("status")["total_amount"]
            .sum()
            .reset_index()
        )
        result = validate_aggregation_consistency(
            detail, summary,
            group_col="status", metric_col="total_amount", agg="sum",
        )
        assert result["valid"] is True
        assert result["severity"] == "PASS"
        assert len(result["mismatches"]) == 0

    def test_users_segment_exhaustiveness(self, users):
        """Verify acquisition_channel segments cover all users."""
        from helpers.logical_validator import validate_segment_exhaustiveness

        # Create a simple metric column (count proxy: all 1s)
        working = users.copy()
        working["count"] = 1
        result = validate_segment_exhaustiveness(
            working, segment_col="acquisition_channel", metric_col="count",
        )
        assert result["severity"] == "PASS"
        assert result["missing_rows"] == 0
        assert result["diff_pct"] < 0.001

    def test_daily_order_volume_temporal(self, orders):
        """Check temporal consistency of daily order counts."""
        from helpers.logical_validator import validate_temporal_consistency

        daily = (
            orders.groupby("order_date")
            .agg(order_count=("order_id", "count"))
            .reset_index()
        )
        result = validate_temporal_consistency(
            daily, date_col="order_date", metric_col="order_count",
            expected_freq="D",
        )
        # Seed data should have continuous dates
        assert result["severity"] in ("PASS", "WARNING")
        assert len(result["duplicate_dates"]) == 0

    def test_monthly_revenue_trend_continuity(self, orders):
        """Check monthly revenue for structural breaks."""
        from helpers.logical_validator import validate_trend_continuity

        orders_with_date = orders.copy()
        orders_with_date["order_date"] = pd.to_datetime(
            orders_with_date["order_date"]
        )
        monthly = (
            orders_with_date
            .set_index("order_date")
            .resample("ME")["total_amount"]
            .sum()
        )
        result = validate_trend_continuity(monthly, max_gap_pct=1.0)
        # Allow some seasonal variation but no extreme breaks
        assert result["severity"] in ("PASS", "WARNING")


# ============================================================
# Layer 3: Business Rules
# ============================================================

class TestBusinessRules:
    """Layer 3: Range validation, rate validation."""

    def test_product_price_ranges(self, products):
        from helpers.business_rules import validate_ranges

        rules = [
            {"column": "price", "min": 0, "max": 1000, "name": "product_price"},
        ]
        result = validate_ranges(products, rules)
        assert result["valid"] is True
        for v in result["violations"]:
            assert v["severity"] == "PASS"
            assert v["out_of_range_count"] == 0

    def test_order_total_ranges(self, orders):
        from helpers.business_rules import validate_ranges

        rules = [
            {"column": "total_amount", "min": 0, "max": 50000,
             "name": "order_total"},
        ]
        result = validate_ranges(orders, rules)
        # All order totals should be non-negative
        for v in result["violations"]:
            assert v["min_seen"] >= 0

    def test_session_purchase_rate(self, sessions):
        """Validate session-level conversion rate is between 0 and 1."""
        from helpers.business_rules import validate_rates

        working = sessions.copy()
        working["purchases"] = working["had_purchase"].astype(int)
        working["session_count"] = 1
        # Aggregate to get a rate dataset
        result = validate_rates(
            working, numerator_col="purchases",
            denominator_col="session_count",
            expected_range=(0, 1), name="session_conversion",
        )
        assert result["severity"] in ("PASS", "WARNING")
        assert result["rate_stats"]["min"] >= 0
        assert result["rate_stats"]["max"] <= 1

    def test_yoy_change_plausible(self):
        """Validate YoY change logic with synthetic values."""
        from helpers.business_rules import validate_yoy_change

        # Plausible 20% growth
        result = validate_yoy_change(120, 100, max_change_pct=2.0,
                                     metric_name="revenue")
        assert result["valid"] is True
        assert result["severity"] == "PASS"
        assert result["direction"] == "up"

        # Implausible 500% growth
        result = validate_yoy_change(600, 100, max_change_pct=2.0,
                                     metric_name="revenue")
        assert result["severity"] == "BLOCKER"


# ============================================================
# Layer 4: Simpson's Paradox
# ============================================================

class TestSimpsonsParadox:
    """Layer 4: Simpson's Paradox detection on NovaMart data."""

    def test_scan_dimensions_runs(self, orders, users):
        """Scan for Simpson's Paradox across key dimensions."""
        from helpers.simpsons_paradox import scan_dimensions

        # Merge orders with user attributes for segmentation
        merged = orders.merge(users[["user_id", "device_primary", "country"]],
                              on="user_id", how="left")
        # Use completed vs cancelled as groups, total_amount as metric
        result = scan_dimensions(
            merged, metric_col="total_amount", group_col="status",
            candidate_segments=["device_primary", "country"],
        )
        assert result["scanned"] == 2
        assert isinstance(result["paradoxes_found"], int)
        assert len(result["results"]) == 2
        # Each result should have the expected structure
        for r in result["results"]:
            assert "paradox_detected" in r
            assert "aggregate_direction" in r
            assert "severity" in r

    def test_check_single_dimension(self, orders, users):
        """Check one dimension for paradox."""
        from helpers.simpsons_paradox import check_simpsons_paradox

        merged = orders.merge(users[["user_id", "device_primary"]],
                              on="user_id", how="left")
        result = check_simpsons_paradox(
            merged, metric_col="total_amount",
            group_col="status", segment_col="device_primary",
        )
        assert "paradox_detected" in result
        assert "explanation" in result
        assert result["severity"] in ("PASS", "INFO", "BLOCKER")


# ============================================================
# Confidence Scoring (Synthesis)
# ============================================================

class TestConfidenceScoring:
    """Confidence scoring on real NovaMart validation results."""

    def test_full_pipeline_confidence(self, users, orders, products):
        """Run all 4 layers and compute confidence score."""
        from helpers.structural_validator import (
            validate_schema, validate_primary_key,
            validate_referential_integrity, validate_completeness,
        )
        from helpers.logical_validator import (
            validate_aggregation_consistency,
            validate_segment_exhaustiveness,
        )
        from helpers.business_rules import validate_ranges
        from helpers.simpsons_paradox import scan_dimensions
        from helpers.confidence_scoring import (
            score_confidence, format_confidence_badge,
        )

        # --- Layer 1: Structural ---
        schema_result = validate_schema(
            orders,
            expected_columns=["order_id", "user_id", "order_date",
                              "total_amount", "status"],
        )
        pk_result = validate_primary_key(orders, ["order_id"])
        ri_result = validate_referential_integrity(
            users, orders, "user_id", "user_id",
        )
        completeness_result = validate_completeness(
            orders,
            required_columns=["order_id", "user_id", "order_date",
                              "total_amount"],
        )

        # --- Layer 2: Logical ---
        detail = orders[["status", "total_amount"]].copy()
        summary = (
            detail.groupby("status")["total_amount"]
            .sum()
            .reset_index()
        )
        agg_result = validate_aggregation_consistency(
            detail, summary, "status", "total_amount",
        )
        working = orders.copy()
        working["count"] = 1
        seg_result = validate_segment_exhaustiveness(
            working, "status", "count",
        )

        # --- Layer 3: Business rules ---
        range_result = validate_ranges(orders, [
            {"column": "total_amount", "min": 0, "max": 50000,
             "name": "order_total"},
        ])

        # --- Layer 4: Simpson's ---
        merged = orders.merge(
            users[["user_id", "device_primary", "country"]],
            on="user_id", how="left",
        )
        simpsons_result = scan_dimensions(
            merged, "total_amount", "status",
            ["device_primary", "country"],
        )

        # --- Synthesize ---
        validation_results = {
            "schema": schema_result,
            "primary_key": pk_result,
            "referential_integrity": ri_result,
            "completeness": completeness_result,
            "aggregation": agg_result,
            "segment_exhaustiveness": seg_result,
            "ranges": range_result,
            "simpsons": simpsons_result,
        }
        confidence = score_confidence(
            validation_results,
            metadata={"row_count": len(orders)},
        )

        # --- Assertions ---
        assert isinstance(confidence["score"], int)
        assert 0 <= confidence["score"] <= 100
        assert confidence["grade"] in ("A", "B", "C", "D", "F")
        assert isinstance(confidence["factors"], dict)
        assert len(confidence["factors"]) == 7
        assert isinstance(confidence["blockers"], list)
        assert isinstance(confidence["interpretation"], str)
        assert isinstance(confidence["recommendation"], str)

        # NovaMart seed data is clean — expect at least a passing grade
        assert confidence["grade"] in ("A", "B", "C"), \
            f"Expected passing grade, got {confidence['grade']}: {confidence['interpretation']}"

        # --- Badge formatting ---
        badge = format_confidence_badge(confidence)
        assert "Confidence:" in badge
        assert confidence["grade"] in badge
        assert str(confidence["score"]) in badge

    def test_empty_results_returns_f(self):
        from helpers.confidence_scoring import score_confidence
        result = score_confidence({})
        assert result["score"] == 0
        assert result["grade"] == "F"

    def test_partial_results_caps_at_c(self, orders):
        """With only one validator layer, grade should be capped at C."""
        from helpers.structural_validator import validate_primary_key
        from helpers.confidence_scoring import score_confidence

        pk = validate_primary_key(orders, ["order_id"])
        result = score_confidence(
            {"primary_key": pk},
            metadata={"row_count": len(orders)},
        )
        # Partial results → grade capped at C regardless of factor score
        assert result["grade"] in ("C", "D", "F")

    def test_merge_confidence_scores(self, users, orders):
        """Test merging scores from two analysis steps."""
        from helpers.structural_validator import (
            validate_primary_key, validate_completeness,
        )
        from helpers.confidence_scoring import (
            score_confidence, merge_confidence_scores,
        )

        # Step 1: orders validation
        pk1 = validate_primary_key(orders, ["order_id"])
        comp1 = validate_completeness(orders, ["order_id", "user_id"])
        s1 = score_confidence(
            {"primary_key": pk1, "completeness": comp1},
            metadata={"row_count": len(orders)},
        )

        # Step 2: users validation
        pk2 = validate_primary_key(users, ["user_id"])
        comp2 = validate_completeness(users, ["user_id", "signup_date"])
        s2 = score_confidence(
            {"primary_key": pk2, "completeness": comp2},
            metadata={"row_count": len(users)},
        )

        merged = merge_confidence_scores([s1, s2])
        assert isinstance(merged["score"], int)
        assert 0 <= merged["score"] <= 100
        assert merged["grade"] in ("A", "B", "C", "D", "F")


# ============================================================
# Lineage Tracking
# ============================================================

class TestLineageTracking:
    """Lineage tracking integration with NovaMart pipeline."""

    def test_pipeline_lineage_chain(self):
        """Simulate a 3-step pipeline and verify lineage chain."""
        from helpers.lineage_tracker import LineageTracker

        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = LineageTracker(output_dir=tmpdir)

            # Step 1: Data Explorer
            tracker.record(
                step=4, agent="data-explorer",
                inputs=["data/novamart/orders.csv",
                        "data/novamart/users.csv"],
                outputs=["working/data_inventory.md"],
                metadata={"tables_profiled": 2},
            )

            # Step 2: Descriptive Analytics (consumes inventory)
            tracker.record(
                step=5, agent="descriptive-analytics",
                inputs=["working/data_inventory.md",
                        "data/novamart/orders.csv"],
                outputs=["working/analysis_report.md"],
                metadata={"tables_used": 2, "findings_count": 5},
            )

            # Step 3: Validation (consumes analysis)
            tracker.record(
                step=7, agent="validation",
                inputs=["working/analysis_report.md"],
                outputs=["working/validation_report.md"],
                metadata={"layers_run": 4, "confidence_grade": "B"},
            )

            # --- Verify chain ---
            lineage = tracker.get_lineage()
            assert len(lineage) == 3

            # Step 2 should have Step 1 as parent
            assert lineage[1]["parent_ids"] == ["lin_001"]

            # Step 3 should have Step 2 as parent
            assert lineage[2]["parent_ids"] == ["lin_002"]

            # Trace ancestry of the validation report
            chain = tracker.get_lineage_for_output(
                "working/validation_report.md"
            )
            assert len(chain) == 3  # validation → analytics → explorer
            agents_in_chain = [e["agent"] for e in chain]
            assert "validation" in agents_in_chain
            assert "descriptive-analytics" in agents_in_chain
            assert "data-explorer" in agents_in_chain

    def test_lineage_save_load_roundtrip(self):
        """Save lineage to disk and reload it."""
        from helpers.lineage_tracker import LineageTracker

        with tempfile.TemporaryDirectory() as tmpdir:
            # Write
            tracker = LineageTracker(output_dir=tmpdir)
            tracker.record(
                step=1, agent="test-agent",
                inputs=["input.csv"], outputs=["output.md"],
            )
            tracker.save()

            # Verify file exists
            assert os.path.isfile(os.path.join(tmpdir, "lineage.json"))

            # Reload
            tracker2 = LineageTracker(output_dir=tmpdir)
            tracker2.load()
            loaded = tracker2.get_lineage()
            assert len(loaded) == 1
            assert loaded[0]["agent"] == "test-agent"
            assert loaded[0]["step"] == 1

    def test_singleton_track_function(self):
        """Test the module-level track() convenience function."""
        from helpers.lineage_tracker import track, get_tracker

        # Reset singleton
        import helpers.lineage_tracker as lt
        lt._singleton_tracker = None

        track(step=1, agent="singleton-test",
              inputs=["a.csv"], outputs=["b.md"])

        tracker = get_tracker()
        entries = tracker.get_lineage()
        assert len(entries) >= 1
        last = entries[-1]
        assert last["agent"] == "singleton-test"

        # Cleanup
        tracker.clear()


# ============================================================
# Full Pipeline Chain (the capstone test)
# ============================================================

class TestFullPipelineChain:
    """Capstone: Run the entire validation pipeline end-to-end."""

    def test_capstone_e2e(self, users, orders, products, events):
        """Full chain: load data → 4 layers → confidence → lineage."""
        from helpers.structural_validator import (
            validate_schema, validate_primary_key,
            validate_referential_integrity, validate_completeness,
        )
        from helpers.logical_validator import (
            validate_aggregation_consistency,
            validate_segment_exhaustiveness,
            validate_temporal_consistency,
        )
        from helpers.business_rules import validate_ranges, validate_rates
        from helpers.simpsons_paradox import scan_dimensions
        from helpers.confidence_scoring import (
            score_confidence, format_confidence_badge,
        )
        from helpers.lineage_tracker import LineageTracker

        # === LAYER 1: Structural ===
        schema = validate_schema(
            orders,
            expected_columns=["order_id", "user_id", "order_date",
                              "total_amount", "status"],
        )
        pk = validate_primary_key(orders, ["order_id"])
        ri = validate_referential_integrity(
            users, orders, "user_id", "user_id",
        )
        comp = validate_completeness(
            orders, ["order_id", "user_id", "order_date", "total_amount"],
        )

        # === LAYER 2: Logical ===
        detail = orders[["status", "total_amount"]].copy()
        summary = detail.groupby("status")["total_amount"].sum().reset_index()
        agg = validate_aggregation_consistency(
            detail, summary, "status", "total_amount",
        )

        working = orders.copy()
        working["count"] = 1
        seg = validate_segment_exhaustiveness(working, "status", "count")

        daily = (
            orders.groupby("order_date")
            .agg(order_count=("order_id", "count"))
            .reset_index()
        )
        temporal = validate_temporal_consistency(
            daily, "order_date", "order_count", expected_freq="D",
        )

        # === LAYER 3: Business Rules ===
        ranges = validate_ranges(orders, [
            {"column": "total_amount", "min": 0, "max": 50000,
             "name": "order_total"},
        ])

        # === LAYER 4: Simpson's ===
        merged = orders.merge(
            users[["user_id", "device_primary", "country"]],
            on="user_id", how="left",
        )
        simpsons = scan_dimensions(
            merged, "total_amount", "status",
            ["device_primary", "country"],
        )

        # === CONFIDENCE SCORING ===
        validation_results = {
            "schema": schema,
            "primary_key": pk,
            "referential_integrity": ri,
            "completeness": comp,
            "aggregation": agg,
            "segment_exhaustiveness": seg,
            "temporal": temporal,
            "ranges": ranges,
            "simpsons": simpsons,
        }
        confidence = score_confidence(
            validation_results,
            metadata={"row_count": len(orders)},
        )

        # Score is computed and reasonable
        assert isinstance(confidence["score"], int)
        assert confidence["score"] > 0, "Score should be >0 for clean data"
        assert confidence["grade"] in ("A", "B", "C")

        # Badge is formatted
        badge = format_confidence_badge(confidence)
        assert len(badge) > 0

        # All 7 factors are present
        assert len(confidence["factors"]) == 7
        for factor_name, factor in confidence["factors"].items():
            assert "score" in factor
            assert "max" in factor
            assert "status" in factor
            assert "detail" in factor

        # === LINEAGE TRACKING ===
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = LineageTracker(output_dir=tmpdir)

            tracker.record(
                step=4, agent="data-explorer",
                inputs=["data/novamart/orders.csv"],
                outputs=["working/data_inventory.md"],
                metadata={"tables_profiled": 5},
            )
            tracker.record(
                step=5, agent="descriptive-analytics",
                inputs=["working/data_inventory.md"],
                outputs=["working/analysis_report.md"],
                metadata={"findings": 3},
            )
            tracker.record(
                step=7, agent="validation",
                inputs=["working/analysis_report.md"],
                outputs=["working/validation_report.md"],
                metadata={
                    "confidence_score": confidence["score"],
                    "confidence_grade": confidence["grade"],
                },
            )

            tracker.save()

            # Reload and verify
            tracker2 = LineageTracker(output_dir=tmpdir)
            tracker2.load()
            chain = tracker2.get_lineage_for_output(
                "working/validation_report.md"
            )
            assert len(chain) == 3
            assert chain[0]["agent"] == "validation"

            # Metadata carries through
            assert chain[0]["metadata"]["confidence_score"] == confidence["score"]

        # === FINAL: Print summary for CI ===
        print(f"\n{'='*60}")
        print(f"DQ-4.4 E2E VALIDATION COMPLETE")
        print(f"Score: {confidence['score']}/100  Grade: {confidence['grade']}")
        print(f"Blockers: {len(confidence['blockers'])}")
        print(f"Factors scored: {len(confidence['factors'])}")
        print(f"Lineage chain length: 3")
        print(f"{'='*60}")
