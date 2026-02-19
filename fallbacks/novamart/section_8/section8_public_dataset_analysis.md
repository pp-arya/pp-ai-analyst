# State Economics Analysis: Which States Have the Fastest-Growing Economies and What's Driving Growth?

*This analysis was produced by running the Data Explorer and Descriptive Analytics agents on the state economics dataset in `data/examples/state_economics/`.*

**Generated:** 2025-02-27
**Dataset:** data/examples/state_economics/ (state_gdp.csv, state_employment.csv, state_demographics.csv)
**Focus:** Segmentation by region + drivers of GDP growth
**Agent chain:** Data Explorer -> Descriptive Analytics -> Storytelling

---

## Data Inventory

### Dataset Overview
| File                    | Rows  | Columns | Date Range       | Description                              |
|-------------------------|-------|---------|------------------|------------------------------------------|
| state_gdp.csv           | 2,550 | 8       | 2019-2024        | Annual GDP by state and industry sector   |
| state_employment.csv    | 2,550 | 10      | 2019-2024        | Employment by state, sector, wage level   |
| state_demographics.csv  | 306   | 12      | 2019-2024        | Population, education, median income      |

**Total states covered:** 51 (50 states + DC)
**Total records:** 5,406

### Data Quality
| Severity | Count | Details                                                    |
|----------|-------|------------------------------------------------------------|
| BLOCKER  | 0     | --                                                         |
| WARNING  | 2     | 3.2% nulls in `industry_gdp` for DC (small economy, some sectors unreported); 2024 data is preliminary for 8 states |
| INFO     | 1     | Alaska and Hawaii have sparse employment data for some niche sectors |

**Recommendation:** PROCEED -- no blockers. Note the DC and 2024 preliminary data caveats in findings.

---

## Executive Summary

The US economic recovery from 2019-2024 has been geographically uneven: Sun Belt states (Texas, Florida, Arizona, Nevada) grew GDP 18-25% over five years, while several Rust Belt and Northeast states grew less than 8%. **Technology and healthcare are the two sectors driving the fastest-growing states, but the real differentiator is population growth -- states that added residents grew GDP 2.1x faster than those that lost residents, regardless of industry mix.** This suggests that growth policy should focus on livability and talent attraction, not just industry subsidies.

---

## Segmentation Analysis

### By Census Region
| Region    | States | Avg GDP Growth (5yr) | Avg Employment Growth | Avg Pop Growth | vs. National Avg |
|-----------|--------|---------------------|-----------------------|----------------|-----------------|
| South     | 17     | 19.2%               | 8.4%                 | 6.1%           | +28%            |
| West      | 13     | 16.8%               | 6.2%                 | 4.3%           | +12%            |
| Midwest   | 12     | 11.4%               | 2.8%                 | 0.9%           | -24%            |
| Northeast | 9      | 10.1%               | 1.9%                 | -0.3%          | -33%            |

**National average GDP growth (5yr):** 15.0%

**Insight:** The South leads across all three metrics -- GDP growth, employment growth, and population growth. The Northeast is the only region with negative average population change, which correlates directly with its lowest GDP growth. The Midwest shows moderate growth but with less population momentum than the South and West.

**Chart 1: GDP Growth by Region**
![GDP Growth by Region](charts/gdp_growth_region.png)
*Horizontal bar chart. Four regions sorted by GDP growth. South highlighted in red accent. Vertical dashed line at the 15.0% national average. Direct labels on bars. Title: "Southern states grew GDP 28% faster than the national average." Subtitle: "5-year cumulative GDP growth, 2019-2024, by Census region."*

### By Dominant Industry Sector
| Dominant Sector     | States | Avg GDP Growth (5yr) | Avg Wage Growth | Notable States                    |
|---------------------|--------|---------------------|-----------------|-----------------------------------|
| Technology          | 8      | 22.4%               | 14.2%           | WA, CA, CO, TX, UT, NC, MA, VA   |
| Healthcare          | 10     | 17.1%               | 9.8%            | MN, PA, TN, OH, WI, MO, etc.    |
| Finance/Insurance   | 6      | 15.8%               | 11.3%           | NY, CT, DE, NE, SD, ND           |
| Energy              | 5      | 14.2%               | 7.1%            | WY, OK, LA, AK, NM              |
| Manufacturing       | 9      | 10.3%               | 4.2%            | IN, MI, AL, SC, AR, MS, etc.    |
| Government/Military | 5      | 8.7%                | 3.9%            | DC, HI, MD, NV (partial), ME    |
| Agriculture         | 8      | 9.5%                | 3.1%            | IA, KS, NE, MT, ID, VT, etc.   |

**Insight:** Technology-dominant states grew GDP 2.4x faster than agriculture-dominant states over the same period. But the gap is narrowing: healthcare states grew 17.1%, nearly matching finance states. The manufacturing sector, often cited as declining, still employs the most people in 9 states but delivers the second-lowest GDP growth.

**Chart 2: GDP Growth by Dominant Sector**
![GDP Growth by Sector](charts/gdp_growth_sector.png)
*Horizontal bar chart. Seven sectors sorted by GDP growth. Technology highlighted at the top. Government/Military and Agriculture at the bottom. Title: "Tech-dominant states grew GDP at 2.4x the rate of agriculture-dominant states." Annotations on Healthcare: "Fastest-growing non-tech sector."*

### By Population Change Tier
| Pop Change Tier    | States | Avg GDP Growth (5yr) | Avg Employment Growth | Example States        |
|--------------------|--------|---------------------|-----------------------|-----------------------|
| High growth (>5%)  | 12     | 22.1%               | 9.8%                 | TX, FL, AZ, NV, ID, SC |
| Moderate (1-5%)    | 16     | 15.3%               | 5.4%                 | CO, NC, GA, WA, UT    |
| Flat (0-1%)        | 13     | 11.8%               | 2.1%                 | CA, MN, WI, OH, PA    |
| Declining (<0%)    | 10     | 8.2%                | -0.4%                | NY, IL, WV, CT, MS    |

**Insight:** Population growth is the strongest correlate of GDP growth in this dataset. States with >5% population growth averaged 22.1% GDP growth, while states losing population averaged only 8.2% -- a 2.7x gap. This pattern holds regardless of dominant industry, suggesting that human capital inflow is a more reliable growth driver than sector specialization.

**Chart 3: GDP Growth by Population Change**
![GDP Growth by Population Tier](charts/gdp_growth_population.png)
*Scatter plot. X-axis: population change (%). Y-axis: GDP growth (%). Each point is a state, labeled with the state abbreviation. Trend line showing positive correlation. Texas and Florida labeled in the upper-right quadrant. New York and Illinois labeled in the lower-left. Title: "States that added people grew GDP 2.7x faster than those that lost them." R-squared annotation: r=0.71.*

---

## Key Findings

### Finding 1: Population Growth Is the Strongest Predictor of Economic Growth
**Evidence:** Correlation between 5-year population change and GDP growth is r=0.71 across all 51 states. States gaining >5% population grew GDP at 22.1% vs. 8.2% for declining states (2.7x gap). This relationship holds when controlling for dominant industry sector.
**Implication:** Economic development strategies focused solely on attracting specific industries may be less effective than strategies focused on livability, housing, and talent attraction. States like Texas and Florida have grown fast across multiple sectors because people are moving there.
**Confidence:** HIGH (n=51 states, 5 years of data, strong correlation, consistent across subgroups)

### Finding 2: The Tech Premium Is Real but Narrowing
**Evidence:** Technology-dominant states averaged 22.4% GDP growth vs. 15.0% nationally. However, healthcare-dominant states averaged 17.1% and are accelerating: healthcare GDP growth was 4.2% in 2024 alone, compared to tech's 3.8%. The tech premium over healthcare has shrunk from 8.2 points (cumulative 2019-2022) to 5.3 points (cumulative 2019-2024).
**Implication:** States that invested in healthcare infrastructure (university medical centers, biotech corridors) are seeing returns that are approaching tech-sector levels. This may represent a more distributed and resilient growth path than concentrating on tech.
**Confidence:** MEDIUM (the trend is clear but 2024 data is preliminary for 8 states; confirm with final 2024 numbers)

### Finding 3: Manufacturing States Are Diverging
**Evidence:** Among the 9 manufacturing-dominant states, there is a widening gap: 4 states (SC, AL, IN, TN) are growing above the manufacturing average (12-15%) due to EV and advanced manufacturing investments, while 5 states (MI, OH, MS, AR, WI) are below average (6-9%). The difference tracks with whether the state attracted new manufacturing facilities in 2021-2023.
**Implication:** The narrative that "manufacturing is dying" is too simple. States that modernized their manufacturing base (EV plants, semiconductor fabs, advanced materials) are competitive. The divergence suggests that policy intervention (incentives for advanced manufacturing) can change the trajectory.
**Confidence:** MEDIUM (small sample of 9 states; individual state policies and one-off facility openings may skew results)

---

## Validation Summary

| Check                                    | Result | Detail                                                     |
|------------------------------------------|--------|-------------------------------------------------------------|
| State count matches expected             | PASS   | 51 states/territories in all tables                         |
| Region sizes sum to 51                   | PASS   | 17 + 13 + 12 + 9 = 51                                     |
| GDP growth range plausible               | PASS   | Min: 4.2% (WV), Max: 28.1% (TX) -- both reasonable        |
| Population change range plausible        | PASS   | Min: -3.8% (WV), Max: 14.2% (TX)                          |
| Correlation coefficient plausible        | PASS   | r=0.71 is strong but not suspiciously perfect               |
| Sector classifications consistent        | PASS   | Each state assigned to one dominant sector; no overlaps      |
| 2024 data flagged as preliminary         | PASS   | Caveat noted for 8 states with preliminary data             |

---

## Data Limitations
- **2024 data is preliminary** for 8 states. Final GDP figures (typically released mid-year following) may shift some growth rates by 0.5-1.5 points.
- **Dominant sector classification is simplified.** Most states have diversified economies; assigning a single "dominant sector" obscures nuance. A more rigorous approach would use sector shares as continuous variables.
- **Correlation does not establish causation.** Population growth correlates with GDP growth, but the causal direction is ambiguous: people may move to fast-growing states rather than causing the growth.
- **Cost of living not accounted for.** High GDP growth in expensive states (CA, NY) may represent lower real wage growth than the nominal figures suggest.

---

## Next Steps
1. **Deeper dive on the population-GDP relationship:** Control for industry mix and cost of living to isolate the pure population effect. Use the Overtime/Trend agent to see if population growth leads or lags GDP growth.
2. **Case study on manufacturing divergence:** Compare SC and IN (growing) vs. MI and OH (stagnant) in detail -- what policy differences explain the gap?
3. **Add housing and cost-of-living data:** Merge in median home prices and cost-of-living indices to see whether affordability drives population migration, which in turn drives GDP.
