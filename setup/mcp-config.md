# MCP Configuration Guide

## What is MCP?

MCP (Model Context Protocol) is how Claude Code connects to external services -- databases, file systems, APIs, and more. When you configure an MCP connection, Claude Code can directly query your data warehouse, read files, or interact with tools like Slack and GitHub, all from within a conversation. Think of it as giving Claude Code hands to reach into your tools.

---

## How MCP Configuration Works

MCP connections are defined in a JSON configuration file. Claude Code reads this file at startup and establishes the connections automatically.

**Configuration file location:**

```
your-repo/
└── .claude/
    └── mcp.json       <-- MCP configuration lives here
```

The file contains a `mcpServers` object where each key is a connection name and each value defines how to start and configure that MCP server.

**Basic structure:**

```json
{
  "mcpServers": {
    "connection-name": {
      "command": "command-to-start-the-server",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

- `command` -- The executable that starts the MCP server
- `args` -- Arguments passed to the command
- `env` -- Environment variables the server needs (tokens, connection strings)

---

## Database Connection: MotherDuck / DuckDB

This is the primary data connection for the bootcamp. It lets Claude Code query your data warehouse directly.

### Full Configuration

Create or edit `.claude/mcp.json` in the repo root:

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

Replace `your-motherduck-token-here` with the token you created during setup (see [prerequisites.md](prerequisites.md#step-4-create-a-motherduck-account)).

### How to Get Your MotherDuck Token

1. Log in at https://app.motherduck.com
2. Click your profile icon (top right)
3. Go to **Settings > Tokens**
4. Click **Create Token**
5. Name it `bootcamp-token`
6. Copy the token

### Local DuckDB Fallback

If MotherDuck is unavailable (no internet, firewall issues), you can use a local DuckDB file instead. Replace the motherduck config with:

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

This runs DuckDB locally with no cloud connection required.

### Verify the Database Connection

After configuring, start Claude Code:

```bash
claude
```

Then ask:

```
List all tables in the database.
```

If connected to MotherDuck with the bootcamp data loaded, you should see tables from the demo dataset (e.g., `novamart.events`, `novamart.users`, `novamart.products`).

If you see an error, check [troubleshooting.md](troubleshooting.md#motherduck-wont-connect).

---

## File System Access

Claude Code can read and write files in your repo by default. No additional MCP configuration is needed for local file access -- it works out of the box.

Claude Code can:
- Read CSV, JSON, Parquet, and text files in your repo
- Write outputs to `outputs/` and `working/`
- Create charts and save them as images

If you need Claude Code to access files outside the repo directory, you can configure a filesystem MCP server:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-filesystem",
        "/path/to/your/data/directory"
      ]
    }
  }
}
```

Replace `/path/to/your/data/directory` with the absolute path to the directory you want Claude Code to access.

---

## Optional Connections

These are not required for the bootcamp, but they demonstrate how MCP extends Claude Code's capabilities. Add any of these to the `mcpServers` object in your `.claude/mcp.json`.

### Slack

Post analysis results directly to a Slack channel.

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-slack"
      ],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-slack-bot-token"
      }
    }
  }
}
```

**Setup:** Create a Slack app at https://api.slack.com/apps, add the `chat:write` scope, install it to your workspace, and copy the Bot User OAuth Token.

**Verify:** Ask Claude Code: `Send a test message to the #general channel.`

### GitHub

Commit analysis results, create issues, or open PRs from Claude Code.

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-github"
      ],
      "env": {
        "GITHUB_TOKEN": "ghp_your-github-personal-access-token"
      }
    }
  }
}
```

**Setup:** Create a personal access token at https://github.com/settings/tokens with `repo` scope.

**Verify:** Ask Claude Code: `List my recent GitHub repositories.`

### Notion

Create pages or databases in Notion with analysis results.

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-notion"
      ],
      "env": {
        "NOTION_API_KEY": "ntn_your-notion-integration-token"
      }
    }
  }
}
```

**Setup:** Create an integration at https://www.notion.so/my-integrations, copy the Internal Integration Token, and share the relevant Notion pages with the integration.

**Verify:** Ask Claude Code: `List my Notion pages.`

---

## Combining Multiple Connections

You can have multiple MCP servers active at once. Here is an example with MotherDuck and Slack configured together:

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
    },
    "slack": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-slack"
      ],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-slack-bot-token"
      }
    }
  }
}
```

---

## Adding Your Own MCP Connections

The MCP ecosystem is growing. To add a new connection:

1. **Find the MCP server package.** Search npm for `mcp-server-` or check the MCP directory at https://github.com/anthropics/mcp.

2. **Add it to your config.** Follow the same pattern:
   ```json
   {
     "mcpServers": {
       "your-connection": {
         "command": "npx",
         "args": ["-y", "package-name"],
         "env": {
           "REQUIRED_TOKEN": "your-token"
         }
       }
     }
   }
   ```

3. **Restart Claude Code.** MCP connections are loaded at startup. After changing `.claude/mcp.json`, exit Claude Code (`/exit`) and start it again.

4. **Test the connection.** Ask Claude Code to perform a simple operation with the new connection.

5. **Document it.** Add a description of the new data source to the "Available Data" section of your `CLAUDE.md` so Claude Code knows what it can access.

---

## Troubleshooting MCP Connections

| Symptom | Likely Cause | Fix |
|---|---|---|
| "MCP connection failed" on startup | Invalid JSON in mcp.json | Run `python3 -c "import json; json.load(open('.claude/mcp.json'))"` to find the error |
| "tool not available" during use | MCP server not installed or failed to start | Run the `npx` command from your config manually to check for errors |
| Connection timeout | Network or firewall blocking the service | Check connectivity with `curl` (see [troubleshooting.md](troubleshooting.md#firewall-blocks-connections)) |
| Token expired or invalid | Credentials changed or were revoked | Generate a new token from the service's settings page |
| Changes not taking effect | Claude Code uses config from startup | Exit Claude Code and restart it after any config change |

For detailed troubleshooting steps, see [troubleshooting.md](troubleshooting.md).
