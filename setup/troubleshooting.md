# Troubleshooting Guide

Common problems and fixes organized by category. If you hit an issue during the bootcamp, find it here.

---

## Installation Issues

### Claude Code won't install

**Symptom:** `npm install -g @anthropic-ai/claude-code` fails with errors.

**Cause:** Usually a permissions issue or outdated Node.js version.

**Fix:**

1. Check your Node.js version:
   ```bash
   node --version
   ```
   If below 18.0.0, update Node.js first (see [prerequisites](prerequisites.md#nodejs-version-too-old)).

2. If you see `EACCES: permission denied`:
   ```bash
   mkdir -p ~/.npm-global
   npm config set prefix '~/.npm-global'
   export PATH=~/.npm-global/bin:$PATH
   ```
   Add the `export` line to your `~/.zshrc` or `~/.bashrc`, then retry the install.

3. If you see network errors, check your internet connection. If behind a proxy:
   ```bash
   npm config set proxy http://your-proxy:port
   npm config set https-proxy http://your-proxy:port
   ```

**Prevention:** Install Node.js using the official LTS version from nodejs.org or via Homebrew (`brew install node`). Avoid using `sudo` for npm installs.

---

### Wrong Node.js version

**Symptom:** Installation fails with a message about incompatible Node version, or Claude Code crashes on startup with cryptic errors.

**Cause:** Node.js version is below 18.

**Fix:**

```bash
node --version
```

If below 18, update:

- **Homebrew (Mac):** `brew upgrade node`
- **nvm (any OS):** `nvm install 20 && nvm use 20`
- **Manual:** Download the latest LTS from https://nodejs.org and install over the existing version.

**Prevention:** Use a Node version manager like `nvm` so you can switch versions easily.

---

### npm permissions errors

**Symptom:** `EACCES` errors when installing global packages.

**Cause:** npm's global install directory is owned by root, and you're running as a regular user.

**Fix:**

Reconfigure npm to use a user-owned directory:

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
```

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, or `~/.bash_profile`):

```bash
export PATH=~/.npm-global/bin:$PATH
```

Reload:

```bash
source ~/.zshrc  # or ~/.bashrc
```

Retry the install:

```bash
npm install -g @anthropic-ai/claude-code
```

**Prevention:** Set up the npm global directory before installing any global packages. Do not use `sudo npm install -g` as a habit.

---

### Claude Code command not found after install

**Symptom:** `claude: command not found` even though `npm install -g` succeeded.

**Cause:** The npm global bin directory is not in your PATH.

**Fix:**

Find where npm installs global packages:

```bash
npm config get prefix
```

Take the output (e.g., `/usr/local` or `~/.npm-global`) and add its `bin` subdirectory to your PATH:

```bash
export PATH=$(npm config get prefix)/bin:$PATH
```

Add that line to your `~/.zshrc` or `~/.bashrc`.

Verify:

```bash
claude --version
```

**Prevention:** After changing npm's prefix, always update your PATH in your shell profile.

---

## Connection Issues

### MotherDuck won't connect

**Symptom:** Queries to MotherDuck timeout or return "connection refused."

**Cause:** Token is wrong, expired, or network is blocking the connection.

**Fix:**

1. Verify your token is correct. Go to https://app.motherduck.com, navigate to Settings > Tokens, and confirm the token matches what you're using.

2. Test the connection outside of Claude Code:
   ```bash
   pip3 install duckdb
   python3 -c "import duckdb; conn = duckdb.connect('md:?motherduck_token=YOUR_TOKEN'); print(conn.execute('SELECT 1').fetchall())"
   ```
   If this works, the issue is in your MCP configuration.

3. Check your MCP config file (see [mcp-config.md](mcp-config.md)) for typos in the token or connection string.

4. If behind a corporate firewall, ask IT to allow outbound connections to `app.motherduck.com` on port 443.

**Prevention:** Test the connection immediately after creating your token. Save the token in a secure location.

---

### MCP connection errors

**Symptom:** Claude Code reports "MCP connection failed" or "tool not available" when you try to query data.

**Cause:** MCP server isn't configured correctly, isn't installed, or can't start.

**Fix:**

1. Check your MCP configuration file exists and is valid JSON:
   ```bash
   cat .claude/mcp.json
   ```
   If the file doesn't exist, create it following the instructions in [mcp-config.md](mcp-config.md).

2. Validate the JSON (a trailing comma or missing bracket will break it):
   ```bash
   python3 -c "import json; json.load(open('.claude/mcp.json'))"
   ```
   If this prints an error, fix the JSON syntax.

3. Make sure the MCP server package is installed. For MotherDuck:
   ```bash
   npx -y @motherduck/mcp-server-motherduck --help
   ```
   If this fails, install it:
   ```bash
   npm install -g @motherduck/mcp-server-motherduck
   ```

4. Restart Claude Code after changing MCP configuration. MCP connections are loaded at startup.

**Prevention:** Always validate your MCP JSON after editing it. Restart Claude Code after any MCP config change.

---

### Firewall blocks connections

**Symptom:** Everything installs but Claude Code hangs when trying to authenticate, query data, or connect to external services.

**Cause:** Corporate firewall, VPN, or proxy blocking outbound connections.

**Fix:**

1. Check if you can reach the required services:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://api.anthropic.com
   curl -s -o /dev/null -w "%{http_code}" https://app.motherduck.com
   ```
   If you get `000` or a timeout, the connection is blocked.

2. If using a VPN, try disconnecting temporarily during setup.

3. If using a proxy, configure npm and your shell:
   ```bash
   npm config set proxy http://your-proxy:port
   npm config set https-proxy http://your-proxy:port
   export HTTP_PROXY=http://your-proxy:port
   export HTTPS_PROXY=http://your-proxy:port
   ```

4. Ask your IT department to allow outbound HTTPS (port 443) to:
   - `api.anthropic.com`
   - `claude.ai`
   - `app.motherduck.com`
   - `registry.npmjs.org`

**Prevention:** Test connectivity before the bootcamp. If your workplace blocks these services, plan to use a personal network or mobile hotspot.

---

## Runtime Issues

### Claude Code hangs or is unresponsive

**Symptom:** Claude Code stops responding after you send a message. The cursor blinks but nothing happens.

**Cause:** Network interruption, large context, or a long-running operation.

**Fix:**

1. Wait 30 seconds -- some operations (especially querying large datasets) take time.
2. If still stuck, press Ctrl+C to cancel the current operation.
3. If Claude Code is completely frozen, close the terminal and open a new one:
   ```bash
   cd ~/Desktop/bootcamp
   claude
   ```
4. If it hangs consistently, check your internet connection and try again.

**Prevention:** Keep your queries focused. If analyzing a large dataset, start with `LIMIT 100` to test before running full queries.

---

### Wrong or unexpected output

**Symptom:** Claude Code returns analysis that doesn't match the data, gives wrong numbers, or misunderstands the question.

**Cause:** Ambiguous question, wrong table referenced, or SQL logic error.

**Fix:**

1. Ask Claude Code to show its SQL:
   ```
   Show me the exact SQL query you ran for that result.
   ```

2. Ask it to validate:
   ```
   Validate this result. Check the row counts and make sure the percentages add up.
   ```

3. If the numbers still seem wrong, verify manually with a simple query:
   ```
   Run: SELECT COUNT(*) FROM novamart.events
   ```

4. Rephrase your question more specifically. Instead of "How's the funnel doing?", try "What is the conversion rate from page_view to purchase in the novamart.events table for the last 30 days?"

**Prevention:** Use the Question Framing skill to structure your analytical questions before diving in. Always validate results before presenting them.

---

### Skill not found or not applied

**Symptom:** Claude Code doesn't apply a skill (e.g., charts look plain, no data quality check runs) even though the skill file exists.

**Cause:** The skill file is not in the expected path, CLAUDE.md doesn't reference it, or Claude Code didn't pick up on the trigger condition.

**Fix:**

1. Verify the skill file exists:
   ```bash
   ls .claude/skills/
   ```

2. Check that CLAUDE.md references the skill and its path. Open CLAUDE.md and look for the skills table.

3. Explicitly ask Claude Code to apply the skill:
   ```
   Apply the visualization-patterns skill and regenerate that chart.
   ```

4. If the skill file is empty, it hasn't been built yet. Check the `fallbacks/` directory for pre-built versions.

**Prevention:** After cloning the repo, run `ls .claude/skills/*/` to confirm all skill files are present.

---

### Agent fails or doesn't complete

**Symptom:** You invoke an agent (e.g., "Run the descriptive analytics agent") and it errors out, produces incomplete results, or stops midway.

**Cause:** Missing variable substitution, unavailable data source, or context limit reached.

**Fix:**

1. Check that the agent file exists and has the correct template variables:
   ```bash
   ls agents/
   ```

2. Make sure the data source the agent needs is available. If it needs MotherDuck and the connection is down, switch to local CSV files:
   ```
   Use the CSV files in data/novamart/ instead of the warehouse.
   ```

3. If Claude Code hit a context limit, start a fresh session:
   ```bash
   claude
   ```
   Then retry the agent with a more focused scope.

4. If the agent template has `{{VARIABLES}}`, make sure you provided values. Ask Claude Code:
   ```
   What variables does the descriptive-analytics agent need?
   ```

**Prevention:** Start with the simpler agents (question-framing, data-explorer) before running complex multi-step agents (descriptive-analytics, deck-creator).

---

## Data Issues

### CSV won't load

**Symptom:** Claude Code fails when trying to read a CSV file, or the data looks garbled.

**Cause:** File encoding issues, wrong delimiter, or malformed CSV.

**Fix:**

1. Check the file exists and is readable:
   ```bash
   ls -la data/novamart/
   head -5 data/novamart/events.csv
   ```

2. If the file has encoding issues (garbled characters), convert it:
   ```bash
   iconv -f ISO-8859-1 -t UTF-8 data/your-file.csv > data/your-file-utf8.csv
   ```

3. If the delimiter isn't a comma (some CSVs use tabs or semicolons), tell Claude Code:
   ```
   This CSV uses semicolons as delimiters. Load it accordingly.
   ```

4. If the CSV has inconsistent row lengths, ask Claude Code to inspect it:
   ```
   Read the first 10 rows of data/novamart/events.csv and check if the column count is consistent.
   ```

**Prevention:** Before loading a file, run `head -5 your-file.csv` to verify it looks correct. Use UTF-8 encoding for all data files.

---

### Encoding errors

**Symptom:** `UnicodeDecodeError` or garbled text when reading files.

**Cause:** The file is not UTF-8 encoded.

**Fix:**

1. Check the file encoding:
   ```bash
   file -I data/your-file.csv
   ```

2. Convert to UTF-8:
   ```bash
   iconv -f $(file -I data/your-file.csv | grep -o 'charset=.*' | cut -d= -f2) -t UTF-8 data/your-file.csv > data/your-file-utf8.csv
   ```

3. Replace the original file with the converted version.

**Prevention:** Always use UTF-8 encoding for data files. If exporting from Excel, choose "CSV UTF-8" as the format.

---

### File too large

**Symptom:** Claude Code slows down or errors when working with a large file (>100 MB).

**Cause:** Claude Code loads file contents into context, which has size limits.

**Fix:**

1. If using a CSV, load it into MotherDuck or DuckDB instead of reading it directly:
   ```
   Load data/large-file.csv into MotherDuck and query it from there.
   ```

2. Work with a sample:
   ```
   Read only the first 1000 rows of data/large-file.csv.
   ```

3. Convert large CSVs to Parquet format (much smaller and faster):
   ```
   Convert data/large-file.csv to Parquet format and save it as data/large-file.parquet.
   ```

4. For files over 500 MB, load them into MotherDuck separately (via the MotherDuck UI or DuckDB CLI) rather than through Claude Code.

**Prevention:** Keep data files under 100 MB when possible. Use Parquet format for anything over 50 MB. Use the warehouse (MotherDuck) for large datasets.

---

## Still stuck?

If your issue isn't listed here:

1. **Search for the error message** -- copy the exact error text and search online.
2. **Ask Claude Code** -- describe the problem and paste the error message. It can often diagnose and fix its own issues.
3. **Ask in the bootcamp channel** -- post your error message and a description of what you were doing. Include your OS and the command that failed.
4. **Flag an instructor** -- during live sessions, raise your hand or use the chat. We build in troubleshooting time for a reason.

When reporting an issue, always include:
- Your operating system (Mac, Linux, WSL)
- The exact command you ran
- The full error message (copy/paste, don't paraphrase)
- What you expected to happen vs. what actually happened
