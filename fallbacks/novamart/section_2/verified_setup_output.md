# Setup Verification — Expected Output

This file shows what a successful setup produces at each step. Compare your output to this.

---

## Step 1: `claude --version`

```
claude 1.0.x (or similar version number)
```

If you see a version number, Claude Code is installed.

---

## Step 2: "What files and folders are in this repo?"

Expected Claude Code response (yours will be worded differently):

```
Here's an overview of the repository structure:

- **CLAUDE.md** — The main configuration file that defines my persona, skills, agents,
  and rules. This is the "brain" of the system.

- **.claude/skills/** — Contains 7 skill files that define quality standards I follow
  automatically:
  - visualization-patterns/ — Chart design standards and named themes
  - presentation-themes/ — Slide deck formatting rules
  - data-quality-check/ — Data validation checks with severity ratings
  - question-framing/ — The Question Ladder framework for structuring analytical questions
  - metric-spec/ — Metric definition templates
  - tracking-gaps/ — Identifying missing data
  - triangulation/ — Cross-referencing and sanity checking findings

- **agents/** — Contains 9 agent workflows for multi-step analytical tasks:
  - question-framing.md, hypothesis.md, data-explorer.md,
    descriptive-analytics.md, overtime-trend.md, storytelling.md,
    validation.md, deck-creator.md, chart-maker.md

- **data/** — Data files for analysis:
  - novamart/ — CSV files for the NovaMart dataset (events, users, products)
  - hero/ — Hero dataset for guided exercises
  - examples/ — Curated public datasets

- **outputs/** — Where final analysis deliverables are saved
- **working/** — Where intermediate work files go
- **setup/** — Setup guides and connection instructions
- **fallbacks/** — Pre-built outputs for exercises (safety net)
```

---

## Step 3: "Who are you? What do you specialize in?"

Expected Claude Code response:

```
I am an **AI Product Analyst**. I help product teams answer analytical questions
using data — not in days, but in minutes.

I specialize in:
- Funnel analysis — where users drop off and why
- Segmentation — finding meaningful groups and comparing them
- Drivers analysis — what variables explain the most variance
- Root cause analysis — why a metric changed
- Trend analysis — patterns over time, anomalies, seasonality
- Metric definition — specifying metrics clearly and completely
- Data quality assessment — validating completeness and consistency
- Storytelling — turning findings into narratives and presentations

I think in questions, hypotheses, and evidence. I always explain WHAT I found
and WHY it matters. I validate my own work before presenting it.
```

If Claude Code identifies itself as "AI Product Analyst" and mentions these specializations, CLAUDE.md is being read correctly.

---

## Step 4: MotherDuck MCP Configuration

Expected contents of `.claude/mcp.json` (with your token inserted):

```json
{
  "mcpServers": {
    "motherduck": {
      "command": "npx",
      "args": ["-y", "@motherduck/mcp-server"],
      "env": {
        "MOTHERDUCK_TOKEN": "your_token_here"
      }
    }
  }
}
```

---

## Step 5: "List all the tables in the bootcamp database. How many rows?"

Expected Claude Code response:

```
Here are the tables in the bootcamp.novamart schema:

| Table              | Row Count |
|--------------------|-----------|
| novamart.events     | ~150,000  |
| novamart.users      | ~10,000   |
| novamart.products   | ~500      |

The events table contains user interaction events (page views, clicks, purchases,
etc.), the users table has user profiles with signup dates and plan types, and
the products table has the product catalog with categories and prices.
```

Note: Exact row counts may vary slightly. The key verification is that you see three tables with data.

---

## Step 6: "List the columns in the novamart.events table and show me the first 5 rows"

Expected Claude Code response:

```
The novamart.events table has the following columns:

| Column       | Type      | Description                        |
|--------------|-----------|------------------------------------|
| event_id     | VARCHAR   | Unique event identifier            |
| user_id      | VARCHAR   | User who triggered the event       |
| event_type   | VARCHAR   | Type of event (page_view, click, purchase, etc.) |
| timestamp    | TIMESTAMP | When the event occurred            |
| properties   | JSON      | Additional event properties        |
| session_id   | VARCHAR   | Session identifier                 |
| platform     | VARCHAR   | Device platform (mobile, desktop, tablet) |

Here are the first 5 rows:

| event_id | user_id | event_type | timestamp           | platform |
|----------|---------|-----------|---------------------|----------|
| evt_001  | usr_042 | page_view | 2024-09-15 10:23:41 | mobile   |
| evt_002  | usr_108 | click     | 2024-09-15 10:24:02 | desktop  |
| evt_003  | usr_042 | add_cart  | 2024-09-15 10:25:18 | mobile   |
| evt_004  | usr_215 | signup    | 2024-09-15 10:26:33 | desktop  |
| evt_005  | usr_042 | purchase  | 2024-09-15 10:28:47 | mobile   |
```

If you see column names and sample rows, your data connection is working.

---

## If MotherDuck Isn't Connecting

Try the local CSV fallback instead:

```
Read the CSV file at data/novamart/events.csv and show me the first 5 rows
```

You should see similar output from the local files. You can use these for all exercises — MotherDuck is faster but the CSVs contain the same data.
