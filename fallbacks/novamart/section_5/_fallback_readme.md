# Fallback: Section 5 — Build Your First Skill + Agent

## When to Use
If you're stuck on the skill build (after 8 minutes) or the agent build (after 12 minutes), use these pre-built examples to catch up and participate in Show & Tell.

## How to Use

### If you're stuck on the Skill:
1. Create the skill directory and copy the fallback skill:
   ```
   mkdir -p .claude/skills/brand-theme
   cp fallbacks/novamart/section_5/brand_theme_skill.md .claude/skills/brand-theme/skill.md
   ```
2. Verify it worked: ask Claude Code `Create a bar chart of the top 5 categories from the novamart data using the brand-theme skill.`
3. You should see a chart using warm brand colors (forest green, saddle brown, goldenrod).
4. Move on to Phase 2 (Agent build) or load the agent fallback below.

### If you're stuck on the Agent:
1. Copy the fallback agent:
   ```
   cp fallbacks/novamart/section_5/quick_segmentation_agent.md agents/quick-segmentation.md
   ```
2. Run it:
   ```
   Run the quick-segmentation agent on the novamart data. The question is: "Which user segments have the highest engagement?"
   ```
3. You should see analysis output with segments, metrics, and findings.

### If the agent run also fails:
1. Copy the pre-built output:
   ```
   cp fallbacks/novamart/section_5/segmentation_analysis_output.md outputs/segmentation_analysis.md
   ```
2. Read through it -- this is what a successful agent run produces.
3. Continue to Show & Tell -- you can discuss the findings.

## What's Included
- `brand_theme_skill.md`: A complete brand-theme visualization skill with warm colors, font choices, and styling rules.
- `quick_segmentation_agent.md`: A complete quick-segmentation agent with 5-step workflow, inputs, and output format.
- `segmentation_analysis_output.md`: The output from running the segmentation agent on NovaMart data.

## Note
These are example outputs. Your own skill and agent might look very different -- that's fine. The goal is to have SOMETHING working so you can keep going.
