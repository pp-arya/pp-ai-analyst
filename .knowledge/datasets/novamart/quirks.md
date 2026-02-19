# NovaMart Data Quirks

Known data characteristics, edge cases, and gotchas for the NovaMart dataset.

## Date and Time
- **Date range:** 2024-01-01 to 2024-12-31 (full calendar year)
- **Timezone:** All timestamps are UTC
- **Weekend gaps:** Some business metrics show natural weekend dips (not missing data)
- **Holiday effects:** Black Friday / Cyber Monday (late November) show large spikes

## Users
- **Bot/test accounts:** No explicit bot flag. Filter by event patterns if needed.
- **Gender:** Includes "unknown" category (~15% of users). Do not exclude from analyses.
- **Country "other":** Catch-all for countries outside US, UK, CA, DE, AU.

## Events
- **Session definition:** Events grouped by session_id. Sessions timeout after 30 min inactivity.
- **Event types:** page_view, product_view, add_to_cart, checkout_start, purchase, search, review.
- **Funnel ordering:** page_view -> product_view -> add_to_cart -> checkout_start -> purchase (not all steps required).
- **Properties column:** JSON — contents vary by event_type. Parse carefully.

## Orders
- **Status values:** completed, cancelled, refunded. Use status='completed' for revenue analysis.
- **Negative revenue:** Refunded orders have status='refunded'. Do NOT include in standard revenue calculations unless analyzing refund rates.
- **Promo_id null:** Most orders have no promotion. Null promo_id = no discount applied.

## Memberships
- **ended_at null:** Means membership is currently active (not churned).
- **Plan types:** monthly and annual. Annual has lower churn rate.
- **Multiple memberships:** A user can have multiple membership records (re-subscriptions).

## NPS
- **Score interpretation:** 0-6 = Detractor, 7-8 = Passive, 9-10 = Promoter.
- **Response bias:** Only users who received and completed the survey are included. Non-respondents are NOT in this table.

## Experiments
- **Two experiments:** Both status='completed'. Check experiment_assignments for variant splits.
- **Assignment timing:** Not all users are in experiments. Only assigned users should be analyzed.

## Common Pitfalls
1. **Don't confuse events.device with users.device_primary** — events.device is per-event, users.device_primary is at signup.
2. **Session counts != user counts** — users have multiple sessions. Always clarify the unit of analysis.
3. **Conversion funnel is not strictly linear** — users can skip steps (e.g., direct purchase from search).
4. **Calendar table is a helper** — join on date for day-of-week and holiday analysis. Don't count calendar rows as data rows.
