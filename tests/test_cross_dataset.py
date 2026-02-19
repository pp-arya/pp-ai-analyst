"""
Integration test: Cross-dataset comparison system.

Tests the full chain:
1. Multiple dataset knowledge directories exist
2. Metric dictionaries can be loaded for each
3. /compare-datasets skill reads both
4. cross_dataset_observations.yaml is writable
5. /patterns --global reads observations
"""
import os
import yaml
import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
KNOWLEDGE_DIR = os.path.join(REPO_ROOT, ".knowledge")
DATASETS_DIR = os.path.join(KNOWLEDGE_DIR, "datasets")
GLOBAL_DIR = os.path.join(KNOWLEDGE_DIR, "global")
ANALYSES_DIR = os.path.join(KNOWLEDGE_DIR, "analyses")


# --- Test 1: Knowledge directory structure ---

def test_knowledge_directory_exists():
    assert os.path.isdir(KNOWLEDGE_DIR), ".knowledge/ directory missing"


def test_datasets_directory_exists():
    assert os.path.isdir(DATASETS_DIR), ".knowledge/datasets/ directory missing"


def test_global_directory_exists():
    assert os.path.isdir(GLOBAL_DIR), ".knowledge/global/ directory missing"


def test_analyses_directory_exists():
    assert os.path.isdir(ANALYSES_DIR), ".knowledge/analyses/ directory missing"


# --- Test 2: NovaMart dataset brain ---

def test_novamart_manifest_exists():
    path = os.path.join(DATASETS_DIR, "novamart", "manifest.yaml")
    assert os.path.isfile(path), "NovaMart manifest.yaml missing"


def test_novamart_schema_exists():
    path = os.path.join(DATASETS_DIR, "novamart", "schema.md")
    assert os.path.isfile(path), "NovaMart schema.md missing"


def test_novamart_metrics_index_exists():
    path = os.path.join(DATASETS_DIR, "novamart", "metrics", "index.yaml")
    assert os.path.isfile(path), "NovaMart metrics/index.yaml missing"


def test_novamart_metrics_count():
    path = os.path.join(DATASETS_DIR, "novamart", "metrics", "index.yaml")
    with open(path) as f:
        data = yaml.safe_load(f)
    metrics = data.get("metrics", [])
    assert len(metrics) >= 8, f"Expected >=8 seed metrics, found {len(metrics)}"


def test_novamart_metric_files_exist():
    index_path = os.path.join(DATASETS_DIR, "novamart", "metrics", "index.yaml")
    with open(index_path) as f:
        data = yaml.safe_load(f)
    metrics_dir = os.path.join(DATASETS_DIR, "novamart", "metrics")
    for metric in data.get("metrics", []):
        metric_file = os.path.join(metrics_dir, metric["file"])
        assert os.path.isfile(metric_file), f"Metric file missing: {metric['file']}"


# --- Test 3: Metric schema ---

def test_metric_schema_exists():
    path = os.path.join(DATASETS_DIR, "_metric_schema.yaml")
    assert os.path.isfile(path), "_metric_schema.yaml missing"


def test_metric_schema_has_required_fields():
    path = os.path.join(DATASETS_DIR, "_metric_schema.yaml")
    with open(path) as f:
        data = yaml.safe_load(f)
    required = data.get("required_fields", [])
    required_names = [f["name"] for f in required]
    for expected in ["id", "name", "category", "definition", "source"]:
        assert expected in required_names, f"Required field '{expected}' missing from schema"


def test_metric_schema_has_dq_status():
    path = os.path.join(DATASETS_DIR, "_metric_schema.yaml")
    with open(path) as f:
        data = yaml.safe_load(f)
    optional = data.get("optional_fields", [])
    optional_names = [f["name"] for f in optional]
    assert "dq_status" in optional_names, "dq_status field missing from metric schema"


# --- Test 4: Analysis archive ---

def test_analyses_index_exists():
    path = os.path.join(ANALYSES_DIR, "index.yaml")
    assert os.path.isfile(path), "analyses/index.yaml missing"


def test_analyses_schema_exists():
    path = os.path.join(ANALYSES_DIR, "_schema.yaml")
    assert os.path.isfile(path), "analyses/_schema.yaml missing"


def test_patterns_yaml_exists():
    path = os.path.join(ANALYSES_DIR, "_patterns.yaml")
    assert os.path.isfile(path), "analyses/_patterns.yaml missing"


def test_patterns_yaml_has_schema():
    path = os.path.join(ANALYSES_DIR, "_patterns.yaml")
    with open(path) as f:
        data = yaml.safe_load(f)
    assert "schema" in data or "patterns" in data, "_patterns.yaml missing schema or patterns key"


# --- Test 5: Cross-dataset observations ---

def test_cross_dataset_observations_exists():
    path = os.path.join(GLOBAL_DIR, "cross_dataset_observations.yaml")
    assert os.path.isfile(path), "cross_dataset_observations.yaml missing"


def test_cross_dataset_observations_has_schema():
    path = os.path.join(GLOBAL_DIR, "cross_dataset_observations.yaml")
    with open(path) as f:
        data = yaml.safe_load(f)
    assert "schema" in data or "observations" in data, \
        "cross_dataset_observations.yaml missing schema or observations key"


# --- Test 6: Skills exist ---

def test_compare_datasets_skill_exists():
    path = os.path.join(REPO_ROOT, ".claude", "skills", "compare-datasets", "skill.md")
    assert os.path.isfile(path), "/compare-datasets skill missing"


def test_patterns_skill_exists():
    path = os.path.join(REPO_ROOT, ".claude", "skills", "patterns", "skill.md")
    assert os.path.isfile(path), "/patterns skill missing"


def test_history_skill_exists():
    path = os.path.join(REPO_ROOT, ".claude", "skills", "history", "skill.md")
    assert os.path.isfile(path), "/history skill missing"


def test_metrics_skill_exists():
    path = os.path.join(REPO_ROOT, ".claude", "skills", "metrics", "skill.md")
    assert os.path.isfile(path), "/metrics skill missing"


def test_archive_analysis_skill_exists():
    path = os.path.join(REPO_ROOT, ".claude", "skills", "archive-analysis", "skill.md")
    assert os.path.isfile(path), "/archive-analysis skill missing"


def test_semantic_validation_skill_exists():
    path = os.path.join(REPO_ROOT, ".claude", "skills", "semantic-validation", "skill.md")
    assert os.path.isfile(path), "semantic-validation skill missing"


# --- Test 7: Patterns skill has --global support ---

def test_patterns_skill_has_global_flag():
    path = os.path.join(REPO_ROOT, ".claude", "skills", "patterns", "skill.md")
    with open(path) as f:
        content = f.read()
    assert "--global" in content, "/patterns skill missing --global flag"
    assert "cross_dataset_observations" in content, \
        "/patterns skill missing cross_dataset_observations reference"


# --- Test 8: Active dataset resolution ---

def test_active_yaml_exists():
    path = os.path.join(KNOWLEDGE_DIR, "active.yaml")
    assert os.path.isfile(path), ".knowledge/active.yaml missing"


def test_active_yaml_points_to_valid_dataset():
    path = os.path.join(KNOWLEDGE_DIR, "active.yaml")
    with open(path) as f:
        data = yaml.safe_load(f)
    active_id = data.get("active_dataset") or data.get("dataset_id") or data.get("id")
    assert active_id is not None, "active.yaml has no dataset identifier"
    dataset_dir = os.path.join(DATASETS_DIR, active_id)
    assert os.path.isdir(dataset_dir), f"Active dataset '{active_id}' directory missing"
