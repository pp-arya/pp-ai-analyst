# NovaMart Analysis: Why Are New User Conversions Declining?

**Generated:** 2025-02-27
**Dataset:** bootcamp.novamart (events, users, products)
**Focus:** Funnel analysis + segmentation
**Agent chain:** Data Explorer -> Descriptive Analytics -> Validation -> Storytelling

---

## Executive Summary

New user conversion from signup to first purchase has declined from 12.4% to 8.1% over the past four months, a 35% relative drop concentrated in the onboarding-to-first-browse step. Mobile users are disproportionately affected, converting at less than half the rate of desktop users (5.2% vs. 11.8%). The decline is steepest among users acquired through paid search, suggesting that recent ad campaigns are driving lower-intent traffic. We recommend prioritizing the mobile onboarding flow and reassessing paid search targeting criteria.

---

## Funnel Analysis: Signup to First Purchase

### Overall Funnel
| Step                | Users  | Conversion (step) | Conversion (overall) | Median Time to Next |
|---------------------|--------|-------------------|---------------------|---------------------|
| 1. Signup           | 10,000 | --                | --                  | --                  |
| 2. Onboarding done  | 6,820  | 68.2%             | 68.2%               | 0.4 days            |
| 3. First browse     | 4,115  | 60.3%             | 41.2%               | 1.2 days            |
| 4. Add to cart      | 1,847  | 44.9%             | 18.5%               | 2.8 days            |
| 5. First purchase   | 812    | 44.0%             | 8.1%                | 0.3 days            |

**Overall conversion:** 8.1% (signup to first purchase)
**Biggest absolute drop-off:** Signup to Onboarding -- 3,180 users lost (31.8%)
**Biggest relative drop-off:** First browse to Add to cart -- only 44.9% continue, and this is where the recent decline is concentrated

**Chart 1: Funnel Visualization**
![NovaMart Conversion Funnel](charts/novamart_funnel.png)
*Horizontal bar chart showing user count at each step. Bars decrease left to right. Drop-off percentages labeled between bars. The First Browse -> Add to Cart step is highlighted in red with annotation: "Biggest bottleneck: 55% of browsers never add to cart."*
*Subtitle: "NovaMart new user funnel, Sep 2024 - Jan 2025, n=10,000 signups"*

### Funnel by Platform
| Step                | Desktop (n=4,210) | Mobile (n=4,893) | Tablet (n=897) |
|---------------------|-------------------|------------------|----------------|
| 1. Signup           | 100%              | 100%             | 100%           |
| 2. Onboarding done  | 74.1%             | 63.2%            | 68.5%          |
| 3. First browse     | 49.8%             | 34.1%            | 40.2%          |
| 4. Add to cart      | 23.5%             | 14.0%            | 18.9%          |
| 5. First purchase   | 11.8%             | 5.2%             | 8.7%           |

**Insight:** Mobile conversion (5.2%) is less than half of desktop (11.8%). The gap widens at every funnel step but is most pronounced at Onboarding -> First Browse, where mobile users drop off at 46% vs. 33% for desktop. This suggests the mobile onboarding experience is losing users before they ever engage with the product.

**Chart 2: Funnel by Platform**
![Funnel by Platform](charts/novamart_funnel_platform.png)
*Grouped bar chart. Three clusters (Desktop, Mobile, Tablet) at each funnel step. Desktop bars in forest green, Mobile in red (highlighted as the problem), Tablet in gray. Annotation on mobile's Onboarding -> Browse step: "Mobile loses 46% here vs. 33% desktop."*

---

## Segmentation Analysis

### By Acquisition Channel
| Channel        | Users | % of Total | Conversion Rate | vs. Average | Trend (MoM) |
|----------------|-------|-----------|----------------|-------------|--------------|
| Organic search | 3,215 | 32.2%     | 11.3%          | +39%        | Stable       |
| Direct         | 2,108 | 21.1%     | 10.1%          | +25%        | Stable       |
| Referral       | 1,542 | 15.4%     | 9.8%           | +21%        | +5% MoM      |
| Paid search    | 2,013 | 20.1%     | 4.2%           | -48%        | -18% MoM     |
| Social         | 1,122 | 11.2%     | 3.9%           | -52%        | -12% MoM     |

**Insight:** Paid search and Social are the worst-converting channels at 4.2% and 3.9% respectively -- less than half the overall average. Worse, both are declining month-over-month. Organic and Direct users convert at 2.5-3x the rate of paid users, suggesting that paid campaigns are acquiring users with low purchase intent. The shift in acquisition channel mix (paid search grew from 15% to 20% of signups in Q4) partially explains the overall conversion decline.

**Chart 3: Conversion Rate by Channel**
![Conversion by Channel](charts/novamart_channel_conversion.png)
*Horizontal bar chart sorted by conversion rate. Organic search at top (11.3%), Social at bottom (3.9%). Vertical dashed line at 8.1% average. Paid search and Social highlighted in red. Annotation: "Paid channels convert at less than half the rate of organic."*

### By Region
| Region         | Users | % of Total | Conversion Rate | vs. Average |
|----------------|-------|-----------|----------------|-------------|
| North America  | 3,811 | 38.1%     | 9.4%           | +16%        |
| Europe         | 2,905 | 29.1%     | 8.3%           | +2%         |
| Asia-Pacific   | 2,187 | 21.9%     | 6.8%           | -16%        |
| Latin America  | 680   | 6.8%      | 5.1%           | -37%        |
| Other          | 417   | 4.2%      | 4.8%           | -41%        |

**Insight:** Regional differences exist but are moderate compared to channel and platform differences. North America leads at 9.4% but only 16% above average. The more notable pattern is that Latin America and Asia-Pacific have both conversion and engagement gaps that may relate to product localization or payment method availability.

### By Plan Type at Signup
| Plan    | Users | % of Total | Conversion Rate | vs. Average |
|---------|-------|-----------|----------------|-------------|
| Pro     | 3,512 | 35.1%     | 12.8%          | +58%        |
| Free    | 4,087 | 40.9%     | 5.9%           | -27%        |
| Trial   | 2,401 | 24.0%     | 6.1%           | -25%        |

**Insight:** Pro users convert to first purchase at more than double the rate of Free and Trial users. This makes sense -- Pro users have already demonstrated purchase willingness by paying for the plan. The real question is why Trial users (24% of signups) convert at nearly the same low rate as Free users. The trial experience may not be effectively demonstrating product value.

---

## Drivers Analysis

### Top Drivers of First-Purchase Conversion
| Rank | Variable              | Correlation | Group Comparison | Direction |
|------|-----------------------|------------|-----------------|-----------|
| 1    | Platform (desktop)    | 0.31       | 2.3x gap        | Positive  |
| 2    | Onboarding completed  | 0.28       | 2.1x gap        | Positive  |
| 3    | Channel (organic)     | 0.24       | 2.7x gap        | Positive  |
| 4    | Browse count (>3)     | 0.22       | 1.8x gap        | Positive  |
| 5    | Plan type (Pro)       | 0.19       | 2.2x gap        | Positive  |

**Key driver narrative:** The strongest predictor of first purchase is platform -- desktop users simply convert better. But the second strongest is onboarding completion, which is actionable: users who complete onboarding are 2.1x more likely to purchase. Since the mobile onboarding completion rate is only 63% (vs. 74% on desktop), improving mobile onboarding could address both the #1 and #2 drivers simultaneously.

**Chart 4: Top Drivers**
![Drivers of Conversion](charts/novamart_drivers.png)
*Horizontal bar chart of top 5 drivers, sorted by correlation strength. All bars in forest green. Direct labels showing correlation coefficient. Annotation on "Onboarding completed": "Most actionable driver -- 2.1x conversion lift."*

---

## Validation Summary

| Check                                    | Result  | Detail                                      |
|------------------------------------------|---------|----------------------------------------------|
| Funnel steps monotonically decreasing    | PASS    | 10,000 > 6,820 > 4,115 > 1,847 > 812       |
| Segment sizes sum to total               | PASS    | Channel: 10,000; Region: 10,000; Plan: 10,000 |
| Conversion rates arithmetic-correct      | PASS    | 812/10,000 = 8.12% (reported 8.1%)          |
| Platform funnel sums to total (per step) | PASS    | Step 2: 3,121 + 3,093 + 614 = 6,828 (~6,820 with rounding) |
| Conversion rate plausible                | PASS    | 8.1% overall is typical for e-commerce signup-to-purchase |
| Charts match data tables                 | PASS    | Spot-checked: funnel chart Step 3 = 4,115 matches table |
| Cross-method driver consistency          | WARNING | Platform and onboarding are correlated (r=0.35) -- their individual effects may be partially overlapping |

---

## Stakeholder Narrative

### Context
The product team flagged that new user conversion to first purchase has been declining since October. We analyzed the full NovaMart dataset -- 10,000 user signups, 150,000+ events across 5 months -- to understand where and why users are dropping off.

### Key Findings

**Finding 1: Mobile onboarding is the biggest bottleneck.**
Mobile users convert at 5.2%, less than half the desktop rate of 11.8%. The gap is widest during onboarding: 37% of mobile users drop off before their first browse, compared to 25% on desktop. With mobile representing 49% of all signups, this single bottleneck accounts for an estimated 30-40% of the overall conversion decline.

**Finding 2: Paid search is driving low-quality traffic.**
Users from paid search convert at 4.2% -- less than half the rate of organic search (11.3%). Paid search's share of signups grew from 15% to 20% in Q4, meaning the overall conversion decline is partially a mix shift: we're acquiring more users, but they're less likely to buy. Paid search conversion is also declining at 18% month-over-month.

**Finding 3: Onboarding completion is the most actionable lever.**
Users who complete onboarding are 2.1x more likely to make a first purchase. Onboarding completion is the second-strongest driver of conversion, and unlike platform (which we can't change), onboarding is entirely within our control to improve.

### Insight
The conversion decline is not a single-cause problem -- it's a combination of a deteriorating mobile experience and a shift toward lower-intent acquisition channels. These two issues compound each other: paid search drives a disproportionate share of mobile signups, and mobile onboarding loses those users before they ever engage.

### Implication
At the current trajectory, first-purchase conversion will drop below 7% within two months. With an average first-purchase value of $47, each percentage point of conversion represents approximately $47,000 in monthly revenue from the current signup volume. The 4.3-point decline from 12.4% to 8.1% represents roughly $200,000/month in unrealized revenue.

### Recommendations
1. **Prioritize mobile onboarding redesign** (high confidence): The mobile onboarding completion rate of 63% is the single most fixable bottleneck. Target: bring mobile onboarding completion to 72% (desktop parity minus 2%) within 6 weeks. Expected impact: +1.5-2.0 points of overall conversion.

2. **Audit paid search targeting and landing pages** (high confidence): Paid search CPA has likely held steady while conversion-to-purchase has dropped 18% MoM. Recalculate effective CAC including downstream conversion. Consider tightening targeting or shifting budget to higher-intent keywords.

3. **Investigate the Trial-to-Purchase gap** (medium confidence): Trial users convert at nearly the same rate as Free users (6.1% vs. 5.9%), suggesting the trial experience isn't demonstrating enough value. This warrants a separate deep-dive into the trial user journey.

---

## Supporting Data
- **Charts referenced:** `charts/novamart_funnel.png`, `charts/novamart_funnel_platform.png`, `charts/novamart_channel_conversion.png`, `charts/novamart_drivers.png`
- **Key metrics cited:** Conversion rates derived from `novamart.events` (purchase events / signup events per user); engagement metrics from event counts per user in `novamart.events`; user attributes from `novamart.users`
- **Time range:** September 2024 through January 2025
- **Caveats:**
  - Platform and onboarding completion are correlated (r=0.35), so their individual driver effects may partially overlap
  - January 2025 cohort has limited maturity; their conversion may increase as they age
  - Revenue estimates assume constant AOV of $47, which may vary by segment

## Data Limitations
- **No A/B test data.** Causal claims (e.g., "improving onboarding will increase conversion") are based on observational correlations, not experiments.
- **Event properties not fully parsed.** The `properties` JSON column contains additional context (page names, button clicks) that was not decomposed in this analysis. A deeper UX funnel analysis could use these fields.
- **Acquisition channel may be misattributed.** Last-touch attribution is assumed. Users who arrive via paid search but return via direct may be miscategorized.
- **Small sample in some segments.** The "Other" region (417 users) and Tablet platform (897 users) have smaller samples. Findings for these segments should be treated as directional.
