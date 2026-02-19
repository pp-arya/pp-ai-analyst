# .knowledge/ -- AI Analyst Knowledge System

This directory is the AI Analyst's persistent memory. It stores structured
knowledge about datasets, metrics, analyses, and user preferences across
sessions.

## Directory Contract

```
.knowledge/
  active.yaml              # Points to the active dataset (set by /switch-dataset)
  README.md                # This file
  user/
    profile.md             # User preferences and expertise profile (gitignored)
  datasets/
    _metric_schema.yaml    # Shared metric entry format definition
    _analysis_schema.yaml  # Shared analysis entry format definition
    .gitignore             # Ignores */last_profile.md and user-created datasets
    {dataset_name}/        # One directory per connected dataset
      manifest.yaml        # Dataset identity, connection config, summary stats
      schema.md            # Table/column documentation (generated from YAML)
      quirks.md            # Dataset-specific data quirks and gotchas
      last_profile.md      # Most recent DQ profiling results (gitignored)
      preferences.md       # Dataset-specific analysis preferences (optional)
      metrics/
        index.yaml         # Metric index for this dataset
        *.yaml             # Individual metric spec files
  analyses/                # Global analysis archive (gitignored)
    index.yaml             # Analysis index with dataset_id tags
    _patterns.yaml         # Extracted patterns across analyses
    _schema.yaml           # Analysis entry format definition
    {date}_{slug}/         # Individual analysis runs
      summary.yaml         # Tagged with dataset_id
  global/                  # Cross-dataset observations (gitignored)
    cross_dataset_observations.yaml
```

## Rules

1. **Structured data in YAML, prose in Markdown.** Manifests, metrics, and
   indices are YAML. Schema docs, quirks, and profiles are Markdown.
2. **Per-dataset isolation.** Each dataset has its own brain under
   `datasets/{name}/`. Never mix data from different datasets in one file.
3. **active.yaml is the single source of truth** for which dataset is active.
   Read it at analysis start. Update it only via /switch-dataset or /connect-data.
4. **Never modify .knowledge/ files during analysis** except `last_profile.md`
   and the `analyses/` archive (which are append-only or overwrite-only).
5. **Committed vs gitignored:** NovaMart brain files are committed (seed data).
   User-created dataset brains, profiles, and analysis archives are gitignored.

## File Ownership

| File / Directory | Owner | Created by | Updated by |
|-----------------|-------|-----------|-----------|
| `active.yaml` | Knowledge system | PORT-1 bootstrap | `/switch-dataset`, `/connect-data` |
| `datasets/{name}/manifest.yaml` | Knowledge system | `/connect-data` or bootstrap | Manual or re-profile |
| `datasets/{name}/schema.md` | Knowledge system | Bootstrap or K-2 rendering | Re-profile or manual edit |
| `datasets/{name}/quirks.md` | Knowledge system | Bootstrap or manual | Manual edit |
| `datasets/{name}/last_profile.md` | DQ system | Data Quality Check skill | Re-profile |
| `datasets/{name}/metrics/` | Metric system | `/metric-spec` or K-3 | Pipeline auto-capture, manual |
| `user/profile.md` | User | Bootstrap (auto-created) | Auto-updated from corrections |
| `analyses/` | Archive system | Pipeline completion | Append-only |
| `global/` | Cross-dataset system | Pattern extraction | Append-only |

## Versioning Policy

- **Seed files** (NovaMart brain) are version-controlled and committed.
- **Generated files** (`last_profile.md`, `analyses/`, `global/`, `user/`)
  are gitignored — they are session artifacts, not source of truth.
- **User-created dataset brains** are gitignored by `.knowledge/datasets/.gitignore`
  (except the seed NovaMart dataset).

## Cleanup

- `last_profile.md` is overwritten on each re-profile. No cleanup needed.
- `analyses/` entries accumulate. Future K-4 will add archive management.
- `user/profile.md` is a single file, updated in place.

## User Profile System

### Overview
The user profile (`user/profile.md`) stores learned preferences about the user
to personalize analysis outputs. It is auto-created by the Knowledge Bootstrap
skill on first session and updated when the user corrects system assumptions.

### Profile Fields
- **Role & Expertise** — role, technical level, SQL/stats comfort, domain
- **Communication Preferences** — detail level, chart preference, narrative style
- **Corrections Log** — timestamped record of user corrections

### Lifecycle
1. **Creation:** Bootstrap skill creates from template if missing
2. **Reading:** Bootstrap loads profile at session start; applies preferences
   to response verbosity, chart count, and narrative style
3. **Updating:** When user corrects a preference (e.g., "give me more detail"),
   the system updates the relevant field and logs the correction
4. **Integration:** Question Router (UX-1.1, Wave 2) will read the profile to
   adapt classification thresholds and response format

### Update Rules
- Only update when user **explicitly** corrects or states a preference
- Never infer preferences from silence
- Always log corrections with date, what was wrong, what was right
- Profile is gitignored — each user gets their own
