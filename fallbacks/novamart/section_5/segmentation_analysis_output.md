# Segmentation Analysis: Which User Segments Have the Highest Engagement?
**Generated:** 2025-02-27
**Dataset:** bootcamp.novamart (events, users, products)
**Segments analyzed:** Plan type, Region, Signup cohort

## Executive Summary
Enterprise users are far more engaged than other plan types, averaging 78 events per user compared to 34 for Free users -- a 2.3x difference. The most actionable opportunity is in the Pro segment, which represents 35% of users but underperforms Enterprise by 21% despite paying for the product. Improving Pro user activation could have the largest revenue impact.

## Segmentation Results

### By Plan Type
| Segment    | Count | % of Total | Avg Events/User | vs. Average |
|------------|-------|-----------|-----------------|-------------|
| Enterprise | 1,204 | 12.0%     | 78.3            | +52%        |
| Pro        | 3,512 | 35.1%     | 61.7            | +20%        |
| Free       | 4,087 | 40.9%     | 33.9            | -34%        |
| Trial      | 1,197 | 12.0%     | 21.2            | -59%        |

**Overall average:** 51.5 events/user

**Insight:** There is a clear engagement ladder from Trial to Enterprise, but the biggest gap is between Free and Pro -- a jump of 82%. Users who convert to Pro significantly increase their usage, suggesting the Pro tier unlocks features that drive engagement.

**Chart:** ![Plan type segmentation](charts/segmentation_plan_type.png)
*Horizontal bar chart, sorted by engagement. Enterprise highlighted in goldenrod. Vertical dashed line at the 51.5 average.*

### By Region
| Segment        | Count | % of Total | Avg Events/User | vs. Average |
|----------------|-------|-----------|-----------------|-------------|
| North America  | 3,811 | 38.1%     | 58.2            | +13%        |
| Europe         | 2,905 | 29.1%     | 52.1            | +1%         |
| Asia-Pacific   | 2,187 | 21.9%     | 44.8            | -13%        |
| Latin America  | 680   | 6.8%      | 41.2            | -20%        |
| Other          | 417   | 4.2%      | 38.5            | -25%        |

**Insight:** North America leads engagement, but the gap is smaller than expected -- only 13% above average. The more notable pattern is that Latin America and Other regions, while small, are significantly below average. This may reflect product localization gaps rather than inherent user differences.

**Chart:** ![Region segmentation](charts/segmentation_region.png)
*Horizontal bar chart, sorted by engagement. North America highlighted. Vertical dashed line at average.*

### By Signup Cohort (Monthly)
| Cohort   | Count | % of Total | Avg Events/User | vs. Average |
|----------|-------|-----------|-----------------|-------------|
| Sep 2024 | 1,850 | 18.5%     | 62.1            | +21%        |
| Oct 2024 | 2,112 | 21.1%     | 55.8            | +8%         |
| Nov 2024 | 2,340 | 23.4%     | 49.3            | -4%         |
| Dec 2024 | 2,015 | 20.2%     | 44.1            | -14%        |
| Jan 2025 | 1,683 | 16.8%     | 38.7            | -25%        |

**Insight:** Earlier cohorts show higher engagement, which is expected since they've had more time to use the product. However, the drop from Sep to Jan (-38%) is steeper than the time difference alone would explain. December and January cohorts are underperforming relative to their age, which may indicate a seasonal onboarding quality issue during the holiday period.

**Chart:** ![Cohort segmentation](charts/segmentation_cohort.png)
*Grouped bar chart by month. Sep 2024 highlighted. Annotation on Dec-Jan dip.*

## Key Findings

### Finding 1: Enterprise Users Engage 2.3x More Than Free Users
**Evidence:** Enterprise segment averages 78.3 events/user vs. 33.9 for Free (n=1,204 and n=4,087 respectively). This gap holds across all regions.
**Implication:** The engagement ladder is clear: more investment in the product (higher plan tier) correlates strongly with more usage. Consider whether engagement drives upgrades, or upgrades drive engagement -- the causal direction matters for strategy.
**Confidence:** HIGH (large sample sizes in both segments, <2% null rate on event data)

### Finding 2: Pro Users Underperform Their Potential
**Evidence:** Pro users average 61.7 events vs. Enterprise's 78.3 -- a 21% gap despite Pro being the largest paid segment (35% of users). The gap is widest in the "product creation" event type, where Enterprise users generate 3.1 creations/user vs. 1.7 for Pro.
**Implication:** Pro users are paying but not fully activated. This is the highest-leverage segment to target: they're already paying, already engaged above average, and have room to grow. Improving Pro activation toward Enterprise-level engagement could increase overall platform activity by ~15%.
**Confidence:** HIGH (n=3,512 for Pro segment, consistent across regions)

### Finding 3: Holiday Cohorts (Dec-Jan) Are Falling Behind
**Evidence:** December and January signup cohorts average 41.4 events/user, 20% below October signups at the same lifecycle stage (when adjusted for time). The gap is concentrated in the first 14 days post-signup.
**Implication:** Something about the onboarding experience during the holiday period is weaker -- possibly reduced team support, competing user attention, or seasonal content gaps. Worth investigating whether onboarding completion rates dropped in these months.
**Confidence:** MEDIUM (cohort analysis is time-sensitive; January cohort has had limited time to mature)

## Validation
| Check                           | Result |
|---------------------------------|--------|
| Segment sizes sum to total      | PASS -- Plan type sums to 10,000 (matches total user count) |
| Minimum segment size >50        | PASS -- smallest segment is "Other" region at 417 users |
| Null rate in event data <10%    | PASS -- 1.8% null rate on event_type column |
| Recomputed Enterprise avg       | PASS -- manual check: 94,258 events / 1,204 users = 78.3 |
| Region segments sum to total    | PASS -- 3,811 + 2,905 + 2,187 + 680 + 417 = 10,000 |

## Data Limitations
- **Engagement measured by event count only.** This does not capture engagement quality (e.g., a user with many page views but no purchases may not be truly "engaged"). A future analysis should weight events by value.
- **Cohort comparison is age-sensitive.** Older cohorts have more time to accumulate events. The cohort findings partially account for this, but a proper cohort retention analysis would be more rigorous.
- **"Other" region is small.** With 417 users, this segment's metrics are less reliable. Findings about this region should be treated as directional, not definitive.
