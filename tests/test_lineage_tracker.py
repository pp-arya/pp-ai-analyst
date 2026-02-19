"""Smoke tests for LineageTracker."""

import json
import os
import sys
import tempfile

# Ensure the repo root is on the path so helpers can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers.lineage_tracker import LineageTracker, get_tracker, track
from helpers import lineage_tracker as lineage_module


def _result(label, passed):
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: {label}")
    return passed


def test_record_and_chain():
    """Create tracker, record 3 steps, verify lineage chain."""
    tracker = LineageTracker(output_dir=tempfile.mkdtemp())

    # Step 1: data explorer reads raw CSV, produces inventory
    tracker.record(
        step=1,
        agent="data-explorer",
        inputs=["data/novamart/orders.csv", "data/novamart/users.csv"],
        outputs=["working/data_inventory.md"],
        metadata={"tables_scanned": 2},
    )

    # Step 2: source tieout reads inventory + raw data
    tracker.record(
        step=2,
        agent="source-tieout",
        inputs=["working/data_inventory.md", "data/novamart/orders.csv"],
        outputs=["working/tieout_report.md"],
    )

    # Step 3: descriptive analytics reads tieout + inventory
    tracker.record(
        step=5,
        agent="descriptive-analytics",
        inputs=["working/tieout_report.md", "working/data_inventory.md"],
        outputs=["working/analysis_descriptive.md"],
        metadata={"row_count": 45000, "tables_used": ["orders", "users"]},
    )

    lineage = tracker.get_lineage()

    checks = [
        _result("lineage has 3 entries", len(lineage) == 3),
        _result("first entry ID is lin_001", lineage[0]["id"] == "lin_001"),
        _result("second entry ID is lin_002", lineage[1]["id"] == "lin_002"),
        _result("third entry ID is lin_003", lineage[2]["id"] == "lin_003"),
        _result(
            "first entry has no parents (raw data inputs)",
            lineage[0]["parent_ids"] == [],
        ),
        _result(
            "second entry parents include lin_001 (inventory match)",
            "lin_001" in lineage[1]["parent_ids"],
        ),
        _result(
            "third entry parents include lin_001 and lin_002",
            "lin_001" in lineage[2]["parent_ids"]
            and "lin_002" in lineage[2]["parent_ids"],
        ),
        _result(
            "metadata preserved on step 3",
            lineage[2]["metadata"].get("row_count") == 45000,
        ),
        _result(
            "agent name preserved",
            lineage[2]["agent"] == "descriptive-analytics",
        ),
        _result(
            "timestamp is present and non-empty",
            isinstance(lineage[0]["timestamp"], str) and len(lineage[0]["timestamp"]) > 0,
        ),
    ]
    return all(checks)


def test_get_lineage_for_output():
    """get_lineage_for_output traces back correctly."""
    tracker = LineageTracker(output_dir=tempfile.mkdtemp())

    tracker.record(
        step=1,
        agent="data-explorer",
        inputs=["data/orders.csv"],
        outputs=["working/inventory.md"],
    )
    tracker.record(
        step=2,
        agent="source-tieout",
        inputs=["working/inventory.md"],
        outputs=["working/tieout.md"],
    )
    tracker.record(
        step=5,
        agent="descriptive-analytics",
        inputs=["working/tieout.md"],
        outputs=["working/analysis.md"],
    )

    chain = tracker.get_lineage_for_output("working/analysis.md")
    chain_ids = [e["id"] for e in chain]

    # Unrelated output returns empty
    empty_chain = tracker.get_lineage_for_output("working/nonexistent.md")

    checks = [
        _result(
            "chain includes all 3 entries (full ancestry)",
            len(chain) == 3,
        ),
        _result(
            "chain starts with the target entry (lin_003)",
            chain_ids[0] == "lin_003",
        ),
        _result(
            "chain includes lin_002 (parent)",
            "lin_002" in chain_ids,
        ),
        _result(
            "chain includes lin_001 (grandparent)",
            "lin_001" in chain_ids,
        ),
        _result(
            "nonexistent output returns empty list",
            empty_chain == [],
        ),
    ]
    return all(checks)


def test_save_load_roundtrip():
    """save/load round-trips correctly."""
    tmp_dir = tempfile.mkdtemp()
    tracker = LineageTracker(output_dir=tmp_dir)

    tracker.record(
        step=1,
        agent="data-explorer",
        inputs=["data/orders.csv"],
        outputs=["working/inventory.md"],
        metadata={"tables": 5},
    )
    tracker.record(
        step=2,
        agent="source-tieout",
        inputs=["working/inventory.md"],
        outputs=["working/tieout.md"],
    )

    tracker.save()

    # Load into a fresh tracker
    tracker2 = LineageTracker(output_dir=tmp_dir)
    tracker2.load()

    lineage1 = tracker.get_lineage()
    lineage2 = tracker2.get_lineage()

    # Verify the JSON file exists on disk
    log_path = os.path.join(tmp_dir, "lineage.json")
    file_exists = os.path.exists(log_path)

    # Read back from disk and verify JSON structure
    with open(log_path, "r") as f:
        raw = json.load(f)

    checks = [
        _result("lineage.json file exists on disk", file_exists),
        _result("JSON on disk is a list", isinstance(raw, list)),
        _result("JSON has 2 entries", len(raw) == 2),
        _result(
            "loaded tracker has same number of entries",
            len(lineage2) == len(lineage1),
        ),
        _result(
            "entry IDs match after round-trip",
            [e["id"] for e in lineage2] == [e["id"] for e in lineage1],
        ),
        _result(
            "metadata preserved after round-trip",
            lineage2[0]["metadata"].get("tables") == 5,
        ),
        _result(
            "parent_ids preserved after round-trip",
            lineage2[1]["parent_ids"] == lineage1[1]["parent_ids"],
        ),
    ]
    return all(checks)


def test_clear():
    """clear resets the log."""
    tracker = LineageTracker(output_dir=tempfile.mkdtemp())

    tracker.record(
        step=1,
        agent="data-explorer",
        inputs=["data/orders.csv"],
        outputs=["working/inventory.md"],
    )
    tracker.record(
        step=2,
        agent="source-tieout",
        inputs=["working/inventory.md"],
        outputs=["working/tieout.md"],
    )

    checks_before = [
        _result("has 2 entries before clear", len(tracker.get_lineage()) == 2),
    ]

    tracker.clear()

    checks_after = [
        _result("has 0 entries after clear", len(tracker.get_lineage()) == 0),
    ]

    # Record again after clear -- IDs should restart from 1
    tracker.record(
        step=1,
        agent="fresh-start",
        inputs=["data/new.csv"],
        outputs=["working/fresh.md"],
    )

    checks_post = [
        _result("has 1 entry after re-recording", len(tracker.get_lineage()) == 1),
        _result(
            "new entry ID is lin_001 (counter reset)",
            tracker.get_lineage()[0]["id"] == "lin_001",
        ),
    ]

    return all(checks_before + checks_after + checks_post)


def test_singleton_track():
    """track() convenience function works with singleton."""
    # Reset the module-level singleton so we start clean
    lineage_module._singleton_tracker = None

    tracker = get_tracker()

    checks_init = [
        _result("get_tracker returns a LineageTracker", isinstance(tracker, LineageTracker)),
        _result("singleton starts empty", len(tracker.get_lineage()) == 0),
    ]

    # Use the convenience function
    track(
        step=1,
        agent="data-explorer",
        inputs=["data/orders.csv"],
        outputs=["working/inventory.md"],
    )
    track(
        step=2,
        agent="source-tieout",
        inputs=["working/inventory.md"],
        outputs=["working/tieout.md"],
    )

    singleton = get_tracker()

    checks_usage = [
        _result(
            "get_tracker returns same instance",
            singleton is tracker,
        ),
        _result(
            "singleton has 2 entries from track() calls",
            len(singleton.get_lineage()) == 2,
        ),
        _result(
            "parent linking works through track()",
            "lin_001" in singleton.get_lineage()[1]["parent_ids"],
        ),
    ]

    # Clean up singleton for other tests
    lineage_module._singleton_tracker = None

    return all(checks_init + checks_usage)


if __name__ == "__main__":
    print("=" * 60)
    print("Smoke Tests: LineageTracker")
    print("=" * 60)

    tests = [
        ("1. Record and chain", test_record_and_chain),
        ("2. get_lineage_for_output traces back", test_get_lineage_for_output),
        ("3. save/load round-trip", test_save_load_roundtrip),
        ("4. clear resets the log", test_clear),
        ("5. track() singleton convenience", test_singleton_track),
    ]

    results = []
    for name, test_fn in tests:
        print(f"\n{name}:")
        try:
            passed = test_fn()
        except Exception as e:
            print(f"  FAIL: Exception -- {e}")
            import traceback
            traceback.print_exc()
            passed = False
        results.append((name, passed))

    print("\n" + "=" * 60)
    print("Summary:")
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("All tests PASSED.")
    else:
        print("Some tests FAILED.")
        sys.exit(1)
