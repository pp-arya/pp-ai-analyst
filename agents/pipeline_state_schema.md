# Pipeline State Schema (OR-1.3)

## Purpose
Track pipeline execution state for resume capability and progress reporting.
Written to `working/pipeline_state.json` during `/run-pipeline` execution.
Read by `/resume-pipeline` to determine restart point.

## Schema

```json
{
  "pipeline_id": "string — unique run ID (ISO timestamp, e.g. 2026-02-16T09:30:00Z)",
  "dataset": "string — active dataset name (from .knowledge/active.yaml)",
  "question": "string — the business question being analyzed",
  "started_at": "ISO datetime",
  "updated_at": "ISO datetime",
  "status": "running | completed | failed | paused",
  "current_step": "number — pipeline step currently executing (0-18)",
  "steps": {
    "0": {
      "agent": "source-resolution",
      "status": "completed | running | pending | skipped | failed",
      "started_at": "ISO datetime | null",
      "completed_at": "ISO datetime | null",
      "output_files": ["list of files produced"],
      "error": "string | null"
    },
    "1": {
      "agent": "question-framing",
      "status": "completed | running | pending | skipped | failed",
      "started_at": "ISO datetime | null",
      "completed_at": "ISO datetime | null",
      "output_files": ["outputs/question_brief_2026-02-16.md"],
      "error": "string | null"
    },
    "2": {
      "agent": "hypothesis",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "3": {
      "agent": "analysis-design-spec",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "4": {
      "agent": "data-explorer",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "4.5": {
      "agent": "source-tieout",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "5": {
      "agent": "descriptive-analytics | overtime-trend | cohort-analysis",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "6": {
      "agent": "root-cause-investigator",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "7": {
      "agent": "validation",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "8": {
      "agent": "opportunity-sizer",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "9": {
      "agent": "story-architect",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "10": {
      "agent": "narrative-coherence-reviewer",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "11": {
      "agent": "story-architect (revision)",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "12": {
      "agent": "chart-maker",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "13": {
      "agent": "visual-design-critic (chart-level)",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "14": {
      "agent": "chart-maker (fixes)",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "15": {
      "agent": "storytelling",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "16": {
      "agent": "deck-creator",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "17": {
      "agent": "visual-design-critic (slide-level)",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    },
    "18": {
      "agent": "close-the-loop",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "output_files": [],
      "error": null
    }
  }
}
```

## Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `pipeline_id` | string | Unique run identifier, ISO timestamp of pipeline start |
| `dataset` | string | Active dataset name resolved from `.knowledge/active.yaml` |
| `question` | string | The business question driving this pipeline run |
| `started_at` | ISO datetime | When the pipeline was initiated |
| `updated_at` | ISO datetime | Last time any field in this file was modified |
| `status` | enum | Overall pipeline status: `running`, `completed`, `failed`, `paused` |
| `current_step` | number | The step number currently executing (0-18) |
| `steps` | object | Map of step number to step state (keys are strings: "0" through "18") |

### Step Fields

| Field | Type | Description |
|-------|------|-------------|
| `agent` | string | Agent name(s) responsible for this step. Pipe-separated if alternatives exist (e.g. step 5) |
| `status` | enum | `completed`, `running`, `pending`, `skipped`, `failed` |
| `started_at` | ISO datetime or null | When the agent began executing this step |
| `completed_at` | ISO datetime or null | When the agent finished (null if not yet complete) |
| `output_files` | array of strings | Relative paths to files produced by this step |
| `error` | string or null | Error message if status is `failed`, otherwise null |

## Status Transitions

```
pending → running → completed
pending → running → failed
pending → skipped
completed (terminal — no further transitions)
failed (terminal unless pipeline is resumed)
skipped (terminal)
```

Pipeline-level status:
```
running → completed   (all steps completed or skipped)
running → failed      (any step failed and pipeline halted)
running → paused      (user paused or context limit reached)
paused  → running     (resumed via /resume-pipeline)
```

## Lifecycle

1. **Created** at pipeline start (step 0: source resolution). All steps initialized to `pending`.
2. **Updated** after each agent completes or fails. `current_step` and `updated_at` advance.
3. **Read** by `/resume-pipeline` to determine the last completed step and restart from the next one.
4. **Archived** to `.knowledge/analyses/` on successful completion alongside the final outputs.

## Rules

- **Atomic writes**: Always write to a temp file first (`working/pipeline_state.tmp.json`), then rename to `working/pipeline_state.json`. This prevents partial reads if an agent fails mid-write.
- **Never delete**: Overwrite in place during a run. Do not delete and recreate.
- **One active state file**: Only one `working/pipeline_state.json` exists at a time. Starting a new pipeline overwrites the previous state.
- **Step keys are strings**: JSON keys for steps use string representations ("4.5" not 4.5) to support half-steps.
- **output_files are relative**: All paths in `output_files` are relative to the repo root (e.g. `working/storyboard_novamart.md`, `outputs/question_brief_2026-02-16.md`).
