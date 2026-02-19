# Pre-Bootcamp Setup Guide

Everything you need to do before Day 1. Budget 15-20 minutes.

---

## System Requirements

You need a computer with a terminal. Specifically:

| OS | What You Need |
|---|---|
| **Mac** | Terminal.app (built in) or iTerm2. macOS 12+ recommended. |
| **Linux** | Any terminal. Ubuntu 20.04+, Fedora 36+, or similar. |
| **Windows** | WSL 2 (Windows Subsystem for Linux). Native Windows terminals will not work. See [Install WSL](#windows-install-wsl-first) below. |

**You also need:**
- A stable internet connection (Claude Code and MotherDuck are cloud services)
- At least 2 GB of free disk space
- Admin/sudo access on your machine (for installing software)

---

## Step 1: Install Node.js (if you don't have it)

Claude Code requires Node.js 18 or later.

**Check if you already have it:**

```bash
node --version
```

If you see `v18.x.x` or higher, skip to Step 2.

**Install Node.js:**

- **Mac (recommended):** Install via Homebrew:
  ```bash
  brew install node
  ```
  If you don't have Homebrew: go to https://brew.sh, copy the install command, paste it in your terminal, and run it. Then run `brew install node`.

- **Mac (alternative):** Download the installer from https://nodejs.org (use the LTS version).

- **Linux (Ubuntu/Debian):**
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
  ```

- **Linux (other distros):** Use your package manager or download from https://nodejs.org.

Verify it worked:

```bash
node --version
```

You should see `v18.0.0` or higher.

---

## Step 2: Install Claude Code

Claude Code requires an Anthropic account with a Pro plan ($20/month minimum). If you don't have one yet, sign up at https://claude.ai and upgrade to Pro.

**Install Claude Code globally:**

```bash
npm install -g @anthropic-ai/claude-code
```

If you get a permissions error, see [Troubleshooting: npm permissions](#npm-permissions-error) below.

**Verify the installation:**

```bash
claude --version
```

You should see a version number. If you see "command not found," see [Troubleshooting](#claude-command-not-found).

**Authenticate:**

```bash
claude
```

The first time you run `claude`, it will open a browser window to authenticate with your Anthropic account. Sign in, authorize the connection, and return to your terminal. You should see the Claude Code prompt.

Type `/exit` to leave Claude Code for now.

---

## Step 3: Terminal Basics (if you're new to the terminal)

If you already use a terminal regularly, skip this section.

**What is the terminal?** It's a text-based way to interact with your computer. Instead of clicking icons, you type commands. Claude Code runs inside the terminal.

**Essential commands you'll use during the bootcamp:**

| Command | What It Does | Example |
|---|---|---|
| `cd` | Change directory (navigate to a folder) | `cd ~/Desktop` |
| `ls` | List files in the current directory | `ls` |
| `pwd` | Print working directory (where am I?) | `pwd` |
| `mkdir` | Make a new directory | `mkdir my-project` |
| `code .` | Open current folder in VS Code (if installed) | `code .` |

**Tips:**
- Press Tab to autocomplete file and directory names.
- Press the up arrow to cycle through previous commands.
- If something seems stuck, press Ctrl+C to cancel.
- Copy/paste in terminal: on Mac, use Cmd+C / Cmd+V. On Linux/WSL, use Ctrl+Shift+C / Ctrl+Shift+V.

---

## Step 4: Create a MotherDuck Account

MotherDuck is the cloud data warehouse we use during the bootcamp. The free tier is all you need -- no credit card required.

1. Go to https://motherduck.com
2. Click **Sign Up** (or "Get Started Free")
3. Create an account using your email or GitHub
4. Complete the onboarding flow
5. Once you're in the MotherDuck UI, click your profile icon (top right) and go to **Settings > Tokens**
6. Click **Create Token**
7. Name it something like `bootcamp-token`
8. Copy the token and save it somewhere safe -- you'll need it during the bootcamp

**Do not share your token.** It grants access to your MotherDuck account.

---

## Step 5: Clone the Bootcamp Repo

**Option A: Git clone (recommended)**

If you have `git` installed:

```bash
cd ~/Desktop
git clone https://github.com/your-org/bootcamp.git
cd bootcamp
```

**Option B: Download as ZIP**

If you don't have `git`:
1. Go to the repo URL (provided by your instructor)
2. Click the green "Code" button
3. Click "Download ZIP"
4. Unzip the file
5. Open your terminal and navigate to the unzipped folder:
   ```bash
   cd ~/Desktop/bootcamp
   ```

**Verify the repo structure:**

```bash
ls
```

You should see: `CLAUDE.md`, `README.md`, `agents/`, `data/`, `setup/`, and other directories.

---

## Step 6: Run the Smoke Test

This confirms everything is working together.

**Start Claude Code inside the repo:**

```bash
cd ~/Desktop/bootcamp
claude
```

Claude Code should start and automatically read the `CLAUDE.md` file. You'll know it's working when you see the Claude Code prompt.

**Ask it a simple question:**

```
What files are in this repo?
```

Claude Code should list the repo contents. If it does, your setup is complete.

**Type `/exit` to close Claude Code.**

You're ready for Day 1.

---

## Troubleshooting

### npm permissions error

**Symptom:** `EACCES: permission denied` when running `npm install -g`.

**Fix (Mac/Linux):**

Option A -- Fix npm's default directory:
```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
```

Then add this line to your shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`):
```bash
export PATH=~/.npm-global/bin:$PATH
```

Reload your shell:
```bash
source ~/.zshrc   # or ~/.bashrc
```

Then retry:
```bash
npm install -g @anthropic-ai/claude-code
```

Option B -- Use sudo (quick but not recommended long-term):
```bash
sudo npm install -g @anthropic-ai/claude-code
```

### Claude command not found

**Symptom:** `claude: command not found` after installing.

**Cause:** The npm global bin directory is not in your PATH.

**Fix:** Find where npm installed it:
```bash
npm list -g --depth=0
```

Then find the bin path:
```bash
npm config get prefix
```

Add the `bin` subdirectory of that path to your PATH. For example, if `npm config get prefix` returns `/usr/local`:
```bash
export PATH=/usr/local/bin:$PATH
```

Add that line to your `~/.zshrc` or `~/.bashrc` so it persists.

### Authentication fails

**Symptom:** Claude Code opens the browser but authentication doesn't complete.

**Fixes:**
- Make sure you're signed in to claude.ai in your default browser
- Make sure your account has a Pro plan ($20/month) or higher
- Try closing all browser tabs and running `claude` again
- If behind a corporate proxy, see [Corporate firewall / proxy](#corporate-firewall--proxy)

### Corporate firewall / proxy

**Symptom:** Claude Code installs but can't connect. MotherDuck connection times out. Browser authentication hangs.

**Fixes:**
- Ask your IT team if they block outbound connections to `api.anthropic.com`, `app.motherduck.com`, or `claude.ai`
- If you use a proxy, configure it for npm:
  ```bash
  npm config set proxy http://your-proxy:port
  npm config set https-proxy http://your-proxy:port
  ```
- If your company uses a VPN, try disconnecting during setup (reconnect after)
- If your company blocks WebSocket connections, MotherDuck may not work -- use the local DuckDB fallback instead (instructions provided during the bootcamp)

### Windows: Install WSL first

Claude Code does not run natively on Windows. You need WSL 2 (Windows Subsystem for Linux).

1. Open PowerShell as Administrator
2. Run:
   ```powershell
   wsl --install
   ```
3. Restart your computer when prompted
4. After reboot, open the Ubuntu app from the Start menu
5. Create a username and password when prompted
6. You now have a Linux terminal -- follow the Mac/Linux instructions above from within this terminal

**Verify WSL is working:**
```bash
wsl --version
```

You should see WSL version 2.x.

### Node.js version too old

**Symptom:** Claude Code installation fails with a Node version error.

**Fix:** Update Node.js. If you installed with Homebrew:
```bash
brew upgrade node
```

If you installed from nodejs.org, download the latest LTS version and reinstall.

Verify:
```bash
node --version
```

Must be 18.0.0 or higher.

---

## Step 7: Install Marp CLI (for Slide Decks)

The analysis pipeline can produce slide decks using Marp (Markdown Presentation Ecosystem). Node.js (installed in Step 1) is required.

**Verify Marp CLI is available:**

```bash
npx @marp-team/marp-cli --version
```

The first time you run this, npx will download Marp CLI automatically. You should see a version number. If it fails, ensure Node.js 18+ is installed (Step 1).

**Note:** Marp is only needed if you want to generate slide decks from your analysis. All other features work without it.

---

## Pre-Bootcamp Checklist

Before Day 1, confirm all of the following:

- [ ] Node.js 18+ installed (`node --version` shows 18+)
- [ ] Claude Code installed (`claude --version` shows a version number)
- [ ] Claude Code authenticated (running `claude` opens the prompt without errors)
- [ ] MotherDuck account created (you can log in at motherduck.com)
- [ ] MotherDuck token saved somewhere accessible
- [ ] Bootcamp repo cloned/downloaded and on your machine
- [ ] Smoke test passed (Claude Code starts inside the repo and responds to a question)
- [ ] Marp CLI available (`npx @marp-team/marp-cli --version` shows a version number)

If any of these fail, check the [Troubleshooting](#troubleshooting) section above or the full [troubleshooting guide](troubleshooting.md).

---

**Estimated time:** 15-20 minutes (assuming no network issues).

**Having trouble?** Bring your questions to Day 1 -- we have dedicated setup time and instructors to help. You can also post in the course Slack/Discord channel before the bootcamp starts.
