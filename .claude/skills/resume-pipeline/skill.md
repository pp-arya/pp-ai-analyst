# Skill: Resume Pipeline

## Purpose
Resume an interrupted analysis pipeline by reading `working/pipeline_state.json`, determining which agents completed, and continuing from the next READY agents using the DAG walker.

## When to Use
Invoke as `/resume-pipeline` when:
- A previous analysis session was interrupted (context limit, user break, connection issue)
- The user wants to continue an analysis started in a prior conversation
- Pipeline state file exists from a partially completed run
- A pipeline failed and the underlying issue has been fixed

## Instructions

### Step 1: Read pipeline state

Check for `working/pipeline_state.json`:
- If it exists → read it and proceed to Step 2
- If it does NOT exist → fall back to artifact scanning (Step 1b)

**Pipeline state fields to extract:**
- `pipeline_id` — identifies this run
- `dataset` — active dataset
- `question` — the business question
- `status` — `running`, `paused`, or `failed`
- `steps` — map of step statuses (completed, running, pending, failed, skipped)

### Step 1b: Artifact-based fallback (no pipeline_state.json)

If no state file exists, scan `working/` and `outputs/` for artifacts:

| Agent | Expected Artifact | Directory |
|-------|-------------------|-----------|
| question-framing | `question_brief_*.md` | `outputs/` |
| hypothesis | `hypothesis_doc_*.md` | `outputs/` |
| data-explorer | `data_inventory_*.md` | `outputs/` |
| source-tieout | `tieout_*.md` | `working/` |
| descriptive-analytics | `analysis_report_*.md` | `outputs/` |
| root-cause-investigator | `investigation_*.md` | `working/` |
| validation | `validation_*.md` | `outputs/` |
| opportunity-sizer | `sizing_*.md` | `working/` |
| story-architect | `storyboard_*.md` | `working/` |
| narrative-coherence-reviewer | `coherence_review_*.md` | `working/` |
| chart-maker | `charts/*.png` | `outputs/` |
| visual-design-critic | `design_review_*.md` | `working/` |
| storytelling | `narrative_*.md` | `outputs/` |
| deck-creator | `deck_*.md` | `outputs/` |

Walk the list top to bottom. If an artifact exists and looks complete (not empty, no "NEEDS REVISION" markers), mark that agent as completed. Reconstruct a pipeline_state.json from this scan.

### Step 2: Compute READY set from DAG

1. Read `agents/registry.yaml` to build the dependency graph
2. For each agent in the registry:
   - If its status is `completed` or `skipped` in the state → leave it
   - If its status is `failed` → reset to `pending` (will be retried)
   - If its status is `running` → reset to `pending` (was interrupted)
3. Compute READY agents: those with `status: pending` whose every dependency is `completed`

### Step 3: Build context summary

Read each completed agent's output files and extract a brief summary:
- From question brief: the framed question and decision context
- From analysis report: key findings (top 3)
- From storyboard: narrative beats and visual plan
- From validation: confidence grade

Compile into a context block for the resumed session.

### Step 4: Present resume plan

Display:

```
Resuming pipeline {pipeline_id}

Completed agents: {count}
  - {agent_name}: {one-line summary from outputs}
  - ...

Failed/interrupted agents (will retry): {count}
  - {agent_name}: {error or "interrupted"}

Next READY agents: {list}

Resume execution?
```

### Step 5: Resume via DAG walker

On confirmation:
1. Update pipeline_state.json: set `status: running`, reset failed/running to pending
2. Hand off to the DAG walker in run-pipeline skill (Phase 2)
3. The walker will pick up from the READY set and continue tier-by-tier
4. All existing completed outputs are preserved — only pending agents execute

## Special Cases

- **Storyboard with "NEEDS ADDITIONS":** Mark story-architect as `pending`, not completed
- **Partial chart generation:** Count generated charts vs storyboard beats. If incomplete, mark chart-maker as `pending`
- **Source tie-out FAIL:** Mark as `failed`. User must investigate before resuming
- **Stale data (>24h gap):** Warn that underlying data may have changed since the original run

## Limitations

- **Context gap:** Resuming restores artifacts but not conversational reasoning. The resumed analysis may be slightly less coherent than a single-session run.
- **No partial step recovery:** If an agent was interrupted mid-execution, the entire agent must re-run.
- **Pipeline state is authoritative:** If pipeline_state.json and artifacts disagree, trust pipeline_state.json.
