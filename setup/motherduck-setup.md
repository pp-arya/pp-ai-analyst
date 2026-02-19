# MotherDuck Setup Guide

Everything you need to connect to MotherDuck, load the bootcamp data, and start querying. Budget 10 minutes.

---

## What is MotherDuck?

MotherDuck is a cloud data warehouse built on DuckDB. It lets you run SQL queries on cloud-hosted data without installing a database, managing servers, or configuring infrastructure. You get a generous free tier with no credit card required -- just sign up and start querying. If you have used BigQuery, Snowflake, or Redshift before, MotherDuck will feel familiar, but lighter and faster to get started with.

---

## Why MotherDuck?

We chose MotherDuck as the bootcamp data warehouse for five reasons:

1. **Fast.** Queries run in milliseconds to seconds, even on millions of rows. No waiting for clusters to spin up.
2. **SQL-based.** You write standard SQL -- the same patterns you would use in Snowflake, BigQuery, or Postgres. Skills transfer directly.
3. **Free.** The free tier is more than enough for everything in this bootcamp. No credit card, no trial countdown.
4. **MCP connector.** MotherDuck has an official MCP server, which means Claude Code can query your data warehouse directly from the terminal. No copy-pasting query results.
5. **Bring your own data.** You can upload CSVs, Parquet files, or load data from URLs at any time. During the bootcamp, you will analyze the NovaMart dataset we provide -- but you can also load your own data and analyze it the same way.

---

## Step 1: Create Your Account

1. Go to [https://motherduck.com](https://motherduck.com)
2. Click **Sign Up** (or "Get Started Free")
3. Create an account using your **email** or **Google account**
4. Complete the short onboarding flow

That is it. The free tier activates automatically -- no credit card, no payment information, no trial expiration.

---

## Step 2: Get Your Token

Claude Code connects to MotherDuck using an access token. You need to create one.

1. Log in at [https://app.motherduck.com](https://app.motherduck.com)
2. Click your **profile icon** (top right corner)
3. Go to **Settings > Tokens**
4. Click **Create Token**
5. Name it `bootcamp-token` (or any name you will remember)
6. Click **Create**
7. **Copy the token immediately** -- you will not be able to see it again after leaving this page

Save the token somewhere secure. You will need it in the next step. Do not share it with anyone -- it grants full access to your MotherDuck account.

---

## Step 3: Connect from Claude Code

Now you will configure Claude Code to talk to MotherDuck using MCP (Model Context Protocol). For full details on MCP, see [mcp-config.md](mcp-config.md).

### Add MotherDuck to your MCP configuration

Open (or create) the file `.claude/mcp.json` in the root of your bootcamp repo:

```json
{
  "mcpServers": {
    "motherduck": {
      "command": "npx",
      "args": [
        "-y",
        "@motherduck/mcp-server-motherduck"
      ],
      "env": {
        "MOTHERDUCK_TOKEN": "your-motherduck-token-here"
      }
    }
  }
}
```

Replace `your-motherduck-token-here` with the token you copied in Step 2.

### Test the connection

Start Claude Code from the bootcamp repo:

```bash
cd ~/Desktop/bootcamp
claude
```

Once the prompt appears, type:

```
Run this SQL query: SELECT 1 AS test
```

If the connection is working, Claude Code will return a result with the value `1`. If you see an error, check the [Troubleshooting](#troubleshooting) section below.

### Important: restart after config changes

Claude Code loads MCP connections at startup. If you change `.claude/mcp.json`, you must exit Claude Code (`/exit`) and start it again for the changes to take effect.

---

## Step 4: Load the Bootcamp Data

The NovaMart demo dataset is pre-loaded in a shared MotherDuck database. You do not need to import anything -- it is already there and ready to query. (After the bootcamp, you can connect your own datasets using `/connect-data`.)

### Verify the data is accessible

In Claude Code, type:

```
Run this SQL query: SELECT COUNT(*) FROM novamart.events
```

You should see a row count (the exact number depends on the dataset version, but it should be in the tens of thousands or more).

### Available tables

The bootcamp database contains three tables:

| Table | Description | Key Columns |
|---|---|---|
| `novamart.events` | User interaction events | `event_type`, `user_id`, `timestamp`, `properties` |
| `novamart.users` | User profiles | `user_id`, `signup_date`, `plan`, `region` |
| `novamart.products` | Product catalog | `product_id`, `category`, `price`, `launch_date` |

To explore any table, ask Claude Code:

```
Describe the novamart.events table. Show me the columns, data types, and a few sample rows.
```

---

## Step 5: Load Your Own Data

One of the best things about MotherDuck is how easy it is to load your own data. You can bring CSVs, Parquet files, or pull data from URLs -- and then analyze it with the same tools and workflows you use for the bootcamp dataset.

### Upload a CSV

If you have a CSV file on your machine, ask Claude Code to load it:

```
Load this CSV into MotherDuck as a new table:

CREATE TABLE my_data AS SELECT * FROM read_csv('path/to/your/file.csv');
```

Replace `path/to/your/file.csv` with the actual path to your file. For example:

```sql
CREATE TABLE my_data AS SELECT * FROM read_csv('/Users/yourname/Desktop/sales_data.csv');
```

### Upload a Parquet file

Same pattern, different function:

```sql
CREATE TABLE my_data AS SELECT * FROM read_parquet('path/to/your/file.parquet');
```

### Load data from a URL

You can load data directly from a public URL without downloading it first:

```sql
CREATE TABLE my_data AS SELECT * FROM read_csv('https://example.com/data/my-dataset.csv');
```

This works with both CSV and Parquet URLs:

```sql
CREATE TABLE my_data AS SELECT * FROM read_parquet('https://example.com/data/my-dataset.parquet');
```

### Tips for loading your own data

- **Name your tables clearly.** Use descriptive names like `sales_2024` or `support_tickets`, not `data1` or `test`.
- **Check the data after loading.** Run `SELECT * FROM my_data LIMIT 10` to make sure it loaded correctly.
- **Large files (>100 MB).** Load them through the MotherDuck web UI at [app.motherduck.com](https://app.motherduck.com) instead of through Claude Code. It handles large uploads more reliably.
- **Update CLAUDE.md.** After loading new data, add a brief description to the "Available Data" section of `CLAUDE.md` so Claude Code knows what the table contains.

---

## Step 6: Local DuckDB Fallback

If MotherDuck is not working for you -- corporate firewall, unstable internet, connectivity issues -- you can use a local DuckDB database instead. You get the exact same SQL, the same query patterns, and the same analysis workflows. The only difference is that the data lives on your machine instead of in the cloud.

### Switch to local DuckDB

Replace the MotherDuck configuration in `.claude/mcp.json` with this:

```json
{
  "mcpServers": {
    "duckdb": {
      "command": "npx",
      "args": [
        "-y",
        "@motherduck/mcp-server-motherduck"
      ],
      "env": {
        "MOTHERDUCK_TOKEN": "",
        "DUCKDB_PATH": "./data/local.duckdb"
      }
    }
  }
}
```

Key differences from the MotherDuck config:
- `MOTHERDUCK_TOKEN` is set to an empty string (no cloud connection)
- `DUCKDB_PATH` points to a local database file

### Load the bootcamp data locally

Since the data is not in the cloud, you need to load the CSV files from the repo:

```sql
CREATE TABLE events AS SELECT * FROM read_csv('data/novamart/events.csv');
CREATE TABLE users AS SELECT * FROM read_csv('data/novamart/users.csv');
CREATE TABLE products AS SELECT * FROM read_csv('data/novamart/products.csv');
```

Ask Claude Code to run these queries after switching to local DuckDB.

### Verify it works

```
Run this SQL query: SELECT COUNT(*) FROM events
```

If you get a row count, you are good to go.

### Same SQL, different connection

Everything else stays the same. The queries you write against local DuckDB are identical to the queries you write against MotherDuck. If you start with local DuckDB and switch to MotherDuck later (or vice versa), your analysis does not change -- only the connection does.

---

## Troubleshooting

### Token expired or invalid

**Symptom:** Queries fail with an authentication error, or Claude Code reports "invalid token."

**Fix:**
1. Go to [https://app.motherduck.com](https://app.motherduck.com)
2. Navigate to **Settings > Tokens**
3. Delete the old token
4. Click **Create Token** to generate a new one
5. Update the token in `.claude/mcp.json`
6. Restart Claude Code (`/exit`, then `claude`)

---

### Connection timeout

**Symptom:** Claude Code hangs when trying to query MotherDuck, or you see a timeout error.

**Fix:**
1. Check your internet connection -- open [https://app.motherduck.com](https://app.motherduck.com) in your browser. If that loads, your internet is fine.
2. If you are behind a corporate firewall, ask IT to allow outbound connections to `app.motherduck.com` on port 443.
3. If you are on a VPN, try disconnecting temporarily.
4. If none of the above works, switch to the [local DuckDB fallback](#step-6-local-duckdb-fallback). You can always switch back to MotherDuck when connectivity improves.

---

### Table not found

**Symptom:** `Table 'novamart.events' not found` or similar error.

**Fix:**
1. Verify the database name. Ask Claude Code:
   ```
   List all databases and tables available in MotherDuck.
   ```
2. Check that you are connected to the right database. The bootcamp data lives in the `bootcamp` database under the `novamart` schema.
3. If using local DuckDB, make sure you loaded the CSV files first (see [Load the bootcamp data locally](#load-the-bootcamp-data-locally)).
4. Table names are case-sensitive in some contexts. Try using the exact casing shown in the [Available tables](#available-tables) section above.

---

### Slow queries

**Symptom:** Queries take longer than expected (more than a few seconds).

**Fix:**
1. Check your data size. Run `SELECT COUNT(*) FROM your_table` to see how many rows you are working with.
2. Add filters to reduce the data being scanned:
   ```sql
   SELECT * FROM novamart.events
   WHERE timestamp >= '2024-01-01'
   LIMIT 1000
   ```
3. Avoid `SELECT *` on large tables. Select only the columns you need:
   ```sql
   SELECT user_id, event_type, timestamp
   FROM novamart.events
   WHERE event_type = 'purchase'
   ```
4. If working with your own large dataset (millions of rows), consider converting CSV files to Parquet format for faster queries:
   ```sql
   COPY (SELECT * FROM my_large_table) TO 'data/my_large_table.parquet' (FORMAT PARQUET);
   ```

---

### MCP configuration errors

**Symptom:** Claude Code fails to start the MotherDuck MCP server, or reports "MCP connection failed."

**Fix:**
1. Validate your JSON. A missing comma or bracket will break the config:
   ```bash
   python3 -c "import json; json.load(open('.claude/mcp.json'))"
   ```
   If this prints an error, fix the JSON syntax.
2. Make sure the MCP server package is available:
   ```bash
   npx -y @motherduck/mcp-server-motherduck --help
   ```
3. If you have multiple entries in `mcpServers`, check that each one has proper JSON formatting (commas between entries, no trailing comma after the last one).
4. Restart Claude Code after any changes to `.claude/mcp.json`.

For more MCP troubleshooting, see [mcp-config.md](mcp-config.md#troubleshooting-mcp-connections).

---

## Quick Reference

| Task | Command |
|---|---|
| Test connection | `SELECT 1 AS test` |
| Count rows | `SELECT COUNT(*) FROM novamart.events` |
| List tables | Ask: "List all tables in the database" |
| Preview a table | `SELECT * FROM novamart.events LIMIT 10` |
| Load a CSV | `CREATE TABLE my_data AS SELECT * FROM read_csv('path/to/file.csv')` |
| Load a Parquet file | `CREATE TABLE my_data AS SELECT * FROM read_parquet('path/to/file.parquet')` |
| Load from URL | `CREATE TABLE my_data AS SELECT * FROM read_csv('https://example.com/data.csv')` |

---

**Estimated time:** 10 minutes (account creation through first successful query).

**Having trouble?** Check the [full troubleshooting guide](troubleshooting.md) or post in the bootcamp Slack/Discord channel. You can also bring questions to the live session -- we build in setup time on Day 1.
