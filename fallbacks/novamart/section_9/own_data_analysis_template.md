# [YOUR COMPANY/PRODUCT] Analysis: [YOUR QUESTION]

*Replace all [PLACEHOLDERS] below with your own context, question, and domain knowledge. Even without data, you can fill in the structure using what you know about your product.*

**Generated:** [TODAY'S DATE]
**Dataset:** [YOUR DATA SOURCE -- e.g., "internal events table", "Salesforce export", "Google Analytics"]
**Focus:** [ANALYSIS TYPE -- segmentation / funnel / drivers / trend]
**Status:** Template -- fill in with your data or domain knowledge

---

## Executive Summary

[Write 3-5 sentences answering these questions:]
- What question did you ask? [e.g., "We wanted to understand why trial-to-paid conversion dropped in Q4."]
- What was the most important finding? [e.g., "Users who complete the onboarding tutorial within 24 hours convert at 3x the rate of those who don't."]
- What does it mean? [e.g., "The tutorial is the critical activation moment, and we're not driving enough users to it."]
- What should we do? [e.g., "Add a tutorial prompt to the first-login experience and measure completion rate weekly."]

---

## Context

[Write 1-2 paragraphs explaining:]
- What is the business problem? [e.g., "Our trial-to-paid conversion rate dropped from 18% to 12% between Q3 and Q4 2024."]
- Why does it matter now? [e.g., "This represents ~$200K/month in unrealized revenue and is our #1 growth bottleneck."]
- What data are we looking at? [e.g., "We analyzed 6 months of user event data covering 15,000 trial signups."]

---

## Key Findings

### Finding 1: [YOUR HEADLINE -- the most important discovery]
**Evidence:** [What numbers support this? e.g., "Tutorial completers convert at 34% vs. 11% for non-completers (n=8,200 and n=6,800 respectively)."]
**Implication:** [What should we do about it? e.g., "Improving tutorial completion from 55% to 70% could add ~$85K/month in conversions."]
**Confidence:** [HIGH / MEDIUM / LOW -- why?]

### Finding 2: [YOUR HEADLINE -- the surprise or second most important finding]
**Evidence:** [What numbers support this?]
**Implication:** [What should we do about it?]
**Confidence:** [HIGH / MEDIUM / LOW -- why?]

### Finding 3: [YOUR HEADLINE -- the opportunity]
**Evidence:** [What numbers support this?]
**Implication:** [What should we do about it?]
**Confidence:** [HIGH / MEDIUM / LOW -- why?]

---

## Segmentation (if applicable)

### By [YOUR SEGMENTATION DIMENSION -- e.g., Plan Type, Industry, Company Size]
| Segment      | Count | % of Total | [KEY METRIC]  | vs. Average |
|--------------|-------|-----------|---------------|-------------|
| [Segment A]  | [n]   | [%]       | [value]       | [+/- %]     |
| [Segment B]  | [n]   | [%]       | [value]       | [+/- %]     |
| [Segment C]  | [n]   | [%]       | [value]       | [+/- %]     |
| [Segment D]  | [n]   | [%]       | [value]       | [+/- %]     |

**Insight:** [What does the segmentation reveal?]

---

## Funnel (if applicable)

### [YOUR FUNNEL NAME -- e.g., Trial Activation Funnel]
| Step               | Users | Conversion (step) | Conversion (overall) |
|--------------------|-------|-------------------|---------------------|
| [Step 1]           | [n]   | --                | --                  |
| [Step 2]           | [n]   | [%]               | [%]                 |
| [Step 3]           | [n]   | [%]               | [%]                 |
| [Step 4]           | [n]   | [%]               | [%]                 |

**Biggest drop-off:** [Which step? Why?]

---

## Insight

[Write 1 paragraph: What do the findings mean TOGETHER? What's the "so what?" that emerges when you look across all findings?]

[e.g., "The conversion decline isn't about product quality -- users who engage deeply love the product. It's about activation: we're not getting enough users past the first meaningful interaction. The tutorial is the gateway, and most users never reach it."]

---

## Implication

[Write 1 paragraph: What happens if we do nothing? Quantify the cost of inaction if possible.]

[e.g., "At the current trajectory, trial conversion will drop below 10% by Q2, costing ~$300K/month in unrealized revenue. The longer we wait, the more we train our acquisition channels to bring in users who never convert."]

---

## Recommendations

1. **[ACTION 1]:** [Description. Connect to a finding. State confidence level.]
   [e.g., "Add a tutorial prompt to the first-login screen. Based on Finding 1, this is the highest-leverage intervention. High confidence."]

2. **[ACTION 2]:** [Description. Connect to a finding. State confidence level.]
   [e.g., "Segment our paid acquisition by tutorial completion rate and pause campaigns that drive low-activation users. Based on Finding 3. Medium confidence -- needs 2 weeks of data."]

3. **[ACTION 3]:** [Description. Connect to a finding. State confidence level.]
   [e.g., "Run an A/B test on a simplified onboarding flow for mobile users. Based on Finding 2. High confidence on the problem, medium on the specific solution."]

---

## Supporting Data
- **Charts referenced:** [List any charts you created or plan to create]
- **Key metrics cited:** [List the primary metrics and their sources]
- **Caveats:** [Any limitations, assumptions, or data quality issues]

---

## What I'd Do Monday Morning

[Write 2-3 sentences about what you would actually do with this analysis when you get back to work. This is for your own reference and for Show & Tell discussion.]

[e.g., "I'd pull the actual tutorial completion rates from our Mixpanel data and validate whether the pattern holds. If it does, I'd bring this to our next product review as a proposal to redesign the first-login flow. The sizing ($85K/month opportunity) should be compelling enough to get it prioritized."]
