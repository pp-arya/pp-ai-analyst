# Agent: Quick Segmentation

## Purpose
Take a dataset and a business question, identify the most meaningful user segments,
compute key metrics per segment, create comparison charts, and summarize the top
insights -- all in one pass.

## Inputs
- {{DATASET}}: The data source to analyze. Can be a file path (CSV, Parquet) or
  a database table reference (e.g., `bootcamp.novamart` schema in MotherDuck).
- {{QUESTION}}: The business question driving the segmentation. Should specify
  what outcome or metric we're trying to understand (e.g., "Which user segments
  have the highest engagement?" or "How do conversion rates differ by region?").

## Workflow

### Step 1: Profile the Data
Before segmenting, understand what's available.

- Read the dataset schema: columns, data types, row count
- Identify candidate segmentation dimensions:
  - Categorical columns with 2-20 distinct values (plan type, region, channel, etc.)
  - Behavioral groupings that can be derived (high/medium/low usage tiers)
  - Time-based cohorts (signup month, first-purchase quarter)
- Identify the key metric to compare across segments (from {{QUESTION}})
- Run a quick quality check: null rates on segmentation columns, minimum segment sizes

Write intermediate results to `working/segmentation_profile.md`.

### Step 2: Choose Segmentation Dimensions
Select 2-3 dimensions that are most relevant to {{QUESTION}}.

**Selection criteria:**
- Dimension has enough variation (at least 3 distinct segments)
- Each segment has at least 50 observations (statistical reliability)
- Dimension is relevant to the question being asked
- Dimensions are not redundant (don't segment by two highly correlated variables)

### Step 3: Compute Segment Metrics
For each segmentation dimension, compute:

| Segment | Count | % of Total | [Key Metric] | vs. Average |
|---------|-------|-----------|--------------|-------------|

- Count and percentage of total for each segment
- The key metric value for each segment
- Relative performance vs. the overall average (e.g., "+23%" or "-15%")
- Sort segments by key metric descending

Flag any segment that:
- Performs >20% above or below the average (notable)
- Contains <5% of total observations (potentially unreliable)
- Has a >10% null rate in the metric column (data quality caveat)

### Step 4: Create Comparison Charts
Generate one chart per segmentation dimension. Apply the Visualization Patterns
skill (`.claude/skills/visualization-patterns/skill.md`). If the brand-theme
skill exists (`.claude/skills/brand-theme/skill.md`), use its colors.

**Chart requirements:**
- Horizontal bar chart for segment comparison (sorted by metric, highest at top)
- Title is the insight, not the dimension name ("Enterprise users engage 2x more than Free" not "Engagement by Plan")
- Direct labels on bars
- Highlight the top and bottom segments with accent color
- Include a vertical reference line for the overall average
- Save charts to `working/charts/`

### Step 5: Summarize Top Insights
Write a summary with exactly 3 key findings:

1. **The headline finding**: The single most important segment difference
2. **The surprise**: Something unexpected -- a segment performing differently than expected
3. **The opportunity**: A segment where improvement would have the biggest impact

For each finding, include:
- The specific numbers (e.g., "Enterprise: 78% vs. Free: 34%")
- Why it matters for the business question
- A confidence rating (HIGH/MEDIUM/LOW based on sample size and data quality)

Save the full analysis to `outputs/`.

## Output Format

```markdown
# Segmentation Analysis: {{QUESTION}}
**Generated:** [date]
**Dataset:** {{DATASET}}
**Segments analyzed:** [list of dimensions]

## Executive Summary
[3 sentences: headline finding, core insight, recommended action]

## Segmentation Results

### By [Dimension 1]
| Segment | Count | % of Total | [Key Metric] | vs. Average |
|---------|-------|-----------|--------------|-------------|
| ...     | ...   | ...       | ...          | ...         |

**Insight:** [What this reveals]
**Chart:** ![](charts/segmentation_dim1.png)

### By [Dimension 2]
[same structure]

## Key Findings

### Finding 1: [Headline]
**Evidence:** [specific numbers]
**Implication:** [what to do about it]
**Confidence:** HIGH / MEDIUM / LOW

### Finding 2: [The Surprise]
[same structure]

### Finding 3: [The Opportunity]
[same structure]

## Validation
| Check | Result |
|-------|--------|
| Segment sizes sum to total | PASS / FAIL |
| Minimum segment size >50 | PASS / FAIL |
| Null rate in metric <10% | PASS / FAIL |

## Data Limitations
- [Any caveats that affect interpretation]
```

## Skills Used
- `.claude/skills/visualization-patterns/skill.md` -- for chart type selection, annotation standards, and theme application
- `.claude/skills/data-quality-check/skill.md` -- for the quality checks in Step 1, ensuring segments are reliable
- `.claude/skills/brand-theme/skill.md` -- (if available) for custom color palette

## Validation
1. **Segment sizes must sum to the total row count** (within 1% for rounding). If they don't, explain which rows are excluded and why.
2. **Key metric values must be arithmetic-correct** -- recompute at least one segment's metric by hand and verify it matches.
3. **Charts must match the data tables** -- verify the chart's top bar matches the highest value in the table.
4. **Findings must be supported by the data** -- every claim in the Key Findings section must reference a specific number from the tables above.
