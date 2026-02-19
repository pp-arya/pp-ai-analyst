# NovaMart Schema

**Dataset:** NovaMart E-Commerce
**Tables:** 13 (4 dimension, 8 fact/transactional, 1 helper)
**Date range:** 2024-01-01 to 2024-12-31

## Dimension Tables

### users (~50,000 rows)
One row per registered user.

| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER | Primary key |
| signup_date | DATE | Account creation date |
| signup_timestamp | TIMESTAMP | Exact creation time |
| acquisition_channel | TEXT | organic, paid_search, social, referral, email, tiktok_ads |
| country | TEXT | US, UK, CA, DE, AU, other |
| device_primary | TEXT | web, ios, android |
| age_bucket | TEXT | 18-24, 25-34, 35-44, 45-54, 55+ |
| gender | TEXT | M, F, other, unknown |

### products (500 rows)
One row per product SKU.

| Column | Type | Description |
|--------|------|-------------|
| product_id | INTEGER | Primary key |
| product_name | TEXT | Human-readable name |
| category | TEXT | electronics, home, clothing, beauty, sports, books |
| subcategory | TEXT | More specific grouping |
| price | DECIMAL | Retail price USD ($5.99-$499.99) |
| cost | DECIMAL | Unit cost (40-70% of price) |
| is_plus_eligible | BOOLEAN | Qualifies for Plus free shipping |

### promotions (5 rows)
One row per promotion.

| Column | Type | Description |
|--------|------|-------------|
| promo_id | INTEGER | Primary key |
| promo_name | TEXT | e.g., Summer Sale, Black Friday |
| promo_type | TEXT | percentage_off |
| discount_pct | DECIMAL | 0.10 - 0.25 |
| start_date / end_date | DATE | Promotion window |
| target_segment | TEXT | all, new_users |

### experiments (2 rows)
One row per A/B test definition.

| Column | Type | Description |
|--------|------|-------------|
| experiment_id | INTEGER | Primary key |
| experiment_name | TEXT | Machine-readable name |
| hypothesis | TEXT | Testable hypothesis |
| primary_metric | TEXT | What experiment measures |
| start_date / end_date | DATE | Experiment window |
| status | TEXT | completed |

## Fact / Transactional Tables

### events (~6.5M rows)
One row per behavioral event.

| Column | Type | Description |
|--------|------|-------------|
| event_id | INTEGER | Primary key |
| user_id | INTEGER | FK to users |
| session_id | TEXT | Groups events into sessions |
| event_type | TEXT | page_view, product_view, add_to_cart, checkout_start, purchase, search, review |
| timestamp | TIMESTAMP | Event time |
| product_id | INTEGER | FK to products (nullable) |
| device | TEXT | web, ios, android |
| page_url | TEXT | Page path |
| properties | JSON | Event-specific metadata |

### sessions (~1.4M rows)
One row per session summary.

| Column | Type | Description |
|--------|------|-------------|
| session_id | TEXT | Primary key |
| user_id | INTEGER | FK to users |
| session_start / session_end | TIMESTAMP | Session window |
| device | TEXT | web, ios, android |
| page_count | INTEGER | Pages viewed |
| event_count | INTEGER | Total events |
| has_purchase | BOOLEAN | Whether session included purchase |

### orders (~30-50K rows)
One row per order.

| Column | Type | Description |
|--------|------|-------------|
| order_id | INTEGER | Primary key |
| user_id | INTEGER | FK to users |
| order_date | DATE | Order date |
| total_amount | DECIMAL | Order total (USD) |
| status | TEXT | completed, cancelled, refunded |
| promo_id | INTEGER | FK to promotions (nullable) |

### order_items
One row per line item.

| Column | Type | Description |
|--------|------|-------------|
| order_id | INTEGER | FK to orders |
| product_id | INTEGER | FK to products |
| quantity | INTEGER | Units ordered |
| unit_price | DECIMAL | Price per unit |

### memberships
Plus membership state changes.

| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER | FK to users |
| started_at | DATE | Membership start |
| ended_at | DATE | Membership end (null if active) |
| plan_type | TEXT | monthly, annual |

### support_tickets (~20K rows)
One row per ticket.

| Column | Type | Description |
|--------|------|-------------|
| ticket_id | INTEGER | Primary key |
| user_id | INTEGER | FK to users |
| category | TEXT | Ticket category |
| severity | TEXT | low, medium, high, critical |
| status | TEXT | open, resolved, escalated |
| created_at | TIMESTAMP | Ticket creation time |
| resolved_at | TIMESTAMP | Resolution time (nullable) |

### nps_responses (~8K rows)
One row per NPS survey response.

| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER | FK to users |
| score | INTEGER | 0-10 NPS score |
| comment | TEXT | Free-text feedback |
| submitted_at | TIMESTAMP | Response time |
| device | TEXT | web, ios, android |

### experiment_assignments (~20K rows)
One row per user-experiment assignment.

| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER | FK to users |
| experiment_id | INTEGER | FK to experiments |
| variant | TEXT | control, treatment |
| assigned_at | TIMESTAMP | Assignment time |

## Helper Table

### calendar (366 rows)
One row per day in 2024.

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Calendar date |
| day_of_week | TEXT | Monday-Sunday |
| is_weekend | BOOLEAN | Saturday or Sunday |
| is_holiday | BOOLEAN | US holiday flag |

## Key Relationships

- users.user_id -> events, sessions, orders, memberships, support_tickets, nps_responses, experiment_assignments
- products.product_id -> events.product_id, order_items.product_id
- orders.order_id -> order_items.order_id
- orders.promo_id -> promotions.promo_id
- experiments.experiment_id -> experiment_assignments.experiment_id
- events.session_id -> sessions.session_id
