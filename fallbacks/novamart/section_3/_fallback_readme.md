# Fallback: Section 3 — Modify CLAUDE.md and Observe the Change

## When to Use
If you're stuck or the exercise isn't working after 8 minutes, use this pre-built modified CLAUDE.md to see what a successful modification looks like.

## How to Use
1. Copy the modified CLAUDE.md over your current one:
   ```
   cp fallbacks/novamart/section_3/CLAUDE_modified.md CLAUDE.md
   ```
2. Restart Claude Code (`/exit` then `claude`)
3. Verify it worked by typing: `Who are you? What do you specialize in?`
4. You should see Claude Code identify as "AI Marketing Analyst" instead of "AI Product Analyst"
5. Test the new rule: `Summarize the key features of this repo.`
6. You should see exactly 3 bullet points in the response.
7. Continue to the next section -- you're caught up.

## What's Included
- `CLAUDE_modified.md`: A complete CLAUDE.md with two modifications from the default:
  1. Persona changed from "AI Product Analyst" to "AI Marketing Analyst"
  2. New rule added: "Always respond with exactly 3 bullet points when summarizing findings."

## Note
These are example modifications. Your own version might look different -- that's fine. The point is to prove that editing CLAUDE.md changes Claude Code's behavior. After the bootcamp, you should change it back to "AI Product Analyst" or set it to whatever persona fits your work.
