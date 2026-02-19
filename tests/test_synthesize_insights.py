"""Smoke tests for synthesize_insights()."""

import sys
import os

# Ensure the repo root is on the path so helpers can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers.analytics_helpers import synthesize_insights


def _result(label, passed):
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: {label}")
    return passed


def test_empty_findings():
    """Empty findings list returns safe defaults."""
    result = synthesize_insights([])
    checks = [
        _result("headline mentions 'No findings'",
                "No findings" in result["headline"]),
        _result("theme_groups is empty list",
                result["theme_groups"] == []),
        _result("contradictions is empty list",
                result["contradictions"] == []),
        _result("narrative_flow is empty list",
                result["narrative_flow"] == []),
        _result("meta_insights is empty list",
                result["meta_insights"] == []),
        _result("action_items is empty list",
                result["action_items"] == []),
        _result("interpretation is non-empty string",
                isinstance(result["interpretation"], str) and len(result["interpretation"]) > 0),
    ]
    return all(checks)


def test_single_finding():
    """Single finding produces correct structure."""
    findings = [{
        "description": "Checkout conversion dropped 15% MoM",
        "metric_value": 0.12,
        "baseline_value": 0.14,
        "affected_pct": 0.60,
        "actionable": True,
        "confidence": 0.92,
        "category": "funnel",
        "direction": "down",
        "metric_name": "checkout_conversion",
    }]
    result = synthesize_insights(findings)
    checks = [
        _result("headline is a non-empty string",
                isinstance(result["headline"], str) and len(result["headline"]) > 0),
        _result("exactly 1 theme group",
                len(result["theme_groups"]) == 1),
        _result("contradictions is empty (only 1 finding)",
                result["contradictions"] == []),
        _result("narrative_flow is non-empty",
                len(result["narrative_flow"]) > 0),
        _result("action_items has 1 item",
                len(result["action_items"]) == 1),
        _result("interpretation is non-empty",
                len(result["interpretation"]) > 0),
    ]
    return all(checks)


def test_contradictions_detected():
    """Multiple findings with opposite directions on same metric are flagged."""
    findings = [
        {
            "description": "Overall conversion rate is up 5% MoM",
            "metric_value": 0.15,
            "baseline_value": 0.143,
            "affected_pct": 1.0,
            "actionable": True,
            "confidence": 0.95,
            "category": "trend",
            "direction": "up",
            "metric_name": "conversion_rate",
        },
        {
            "description": "Mobile conversion rate is down 12% MoM",
            "metric_value": 0.08,
            "baseline_value": 0.091,
            "affected_pct": 0.45,
            "actionable": True,
            "confidence": 0.90,
            "category": "segment",
            "direction": "down",
            "metric_name": "conversion_rate",
        },
    ]
    result = synthesize_insights(findings)
    checks = [
        _result("at least 1 contradiction detected",
                len(result["contradictions"]) >= 1),
        _result("contradiction has finding_a and finding_b",
                all(
                    "finding_a" in c and "finding_b" in c
                    for c in result["contradictions"]
                )),
        _result("contradiction has resolution_hint",
                all(
                    "resolution_hint" in c and len(c["resolution_hint"]) > 0
                    for c in result["contradictions"]
                )),
    ]
    return all(checks)


def test_full_diverse():
    """Full diverse findings list populates all output fields."""
    findings = [
        {
            "description": "Checkout funnel drop-off at payment step increased 20%",
            "metric_value": 0.35,
            "baseline_value": 0.29,
            "affected_pct": 0.70,
            "actionable": True,
            "confidence": 0.95,
            "category": "funnel",
            "direction": "down",
            "metric_name": "checkout_dropoff",
            "p_value": 0.002,
            "effect_size": 0.6,
        },
        {
            "description": "Mobile users have 40% lower engagement than desktop",
            "metric_value": 3.2,
            "baseline_value": 5.3,
            "affected_pct": 0.55,
            "actionable": True,
            "confidence": 0.88,
            "category": "segment",
            "direction": "down",
            "metric_name": "sessions_per_user",
        },
        {
            "description": "Revenue trend is up 8% YoY driven by enterprise",
            "metric_value": 1080000,
            "baseline_value": 1000000,
            "affected_pct": 0.30,
            "actionable": False,
            "confidence": 0.99,
            "category": "trend",
            "direction": "up",
            "metric_name": "revenue",
        },
        {
            "description": "Unusual spike in API errors on Feb 3",
            "metric_value": 450,
            "baseline_value": 50,
            "affected_pct": 0.15,
            "actionable": True,
            "confidence": 0.97,
            "category": "anomaly",
            "direction": "up",
            "metric_name": "api_errors",
        },
        {
            "description": "Mobile retention at day-7 dropped from 25% to 18%",
            "metric_value": 0.18,
            "baseline_value": 0.25,
            "affected_pct": 0.55,
            "actionable": True,
            "confidence": 0.85,
            "category": "engagement",
            "direction": "down",
            "metric_name": "d7_retention",
        },
        {
            "description": "Desktop conversion rate improved by 3%",
            "metric_value": 0.22,
            "baseline_value": 0.213,
            "affected_pct": 0.45,
            "actionable": False,
            "confidence": 0.70,
            "category": "segment",
            "direction": "up",
            "metric_name": "conversion_rate",
        },
    ]
    metadata = {
        "dataset_name": "NovaMart",
        "date_range": "2025-01 to 2025-06",
        "question": "Why is mobile underperforming?",
    }
    result = synthesize_insights(findings, metadata=metadata)

    checks = [
        _result("headline is non-empty",
                isinstance(result["headline"], str) and len(result["headline"]) > 0),
        _result("multiple theme groups",
                len(result["theme_groups"]) >= 3),
        _result("each theme group has theme, findings, summary",
                all(
                    "theme" in tg and "findings" in tg and "summary" in tg
                    for tg in result["theme_groups"]
                )),
        _result("narrative_flow has Context, Tension, Resolution",
                any("[Context]" in b for b in result["narrative_flow"])
                and any("[Tension]" in b for b in result["narrative_flow"])
                and any("[Resolution]" in b for b in result["narrative_flow"])),
        _result("meta_insights is non-empty (mobile repeated)",
                len(result["meta_insights"]) >= 1),
        _result("action_items is non-empty",
                len(result["action_items"]) >= 1),
        _result("action_items have priority field",
                all(
                    a["priority"] in ("high", "medium", "low")
                    for a in result["action_items"]
                )),
        _result("interpretation mentions NovaMart",
                "NovaMart" in result["interpretation"]),
        _result("interpretation mentions business question",
                "mobile" in result["interpretation"].lower()
                or "question" in result["interpretation"].lower()),
    ]
    return all(checks)


def test_score_findings_called():
    """Verify score_findings is called internally (ranked findings have scores)."""
    findings = [
        {
            "description": "Finding A",
            "metric_value": 100,
            "baseline_value": 80,
            "affected_pct": 0.50,
            "actionable": True,
            "confidence": 0.90,
        },
        {
            "description": "Finding B",
            "metric_value": 50,
            "baseline_value": 48,
            "affected_pct": 0.10,
            "actionable": False,
            "confidence": 0.60,
        },
    ]
    result = synthesize_insights(findings)

    # The theme_groups contain findings that should have 'score' and 'rank'
    all_grouped_findings = []
    for tg in result["theme_groups"]:
        all_grouped_findings.extend(tg["findings"])

    checks = [
        _result("grouped findings have 'score' key",
                all("score" in f for f in all_grouped_findings)),
        _result("grouped findings have 'rank' key",
                all("rank" in f for f in all_grouped_findings)),
        _result("grouped findings have 'factors' key",
                all("factors" in f for f in all_grouped_findings)),
        _result("scores are within 0-100 range",
                all(0 <= f["score"] <= 100 for f in all_grouped_findings)),
    ]
    return all(checks)


if __name__ == "__main__":
    print("=" * 60)
    print("Smoke Tests: synthesize_insights()")
    print("=" * 60)

    tests = [
        ("1. Empty findings", test_empty_findings),
        ("2. Single finding", test_single_finding),
        ("3. Contradictions detected", test_contradictions_detected),
        ("4. Full diverse findings", test_full_diverse),
        ("5. score_findings called internally", test_score_findings_called),
    ]

    results = []
    for name, test_fn in tests:
        print(f"\n{name}:")
        try:
            passed = test_fn()
        except Exception as e:
            print(f"  FAIL: Exception — {e}")
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
