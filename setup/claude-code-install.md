# Claude Code Installation Guide

Claude Code is an AI coding assistant that runs in your terminal. Instead of switching between a chat window and your tools, you type natural language directly into your terminal and Claude Code executes commands, queries databases, writes files, and analyzes data on your behalf. It is the engine that powers everything in this bootcamp.

---

## System Requirements

| Requirement | Details |
|---|---|
| **Operating System** | macOS 12 (Monterey) or later, Linux (Ubuntu 20.04+, Fedora 36+, or similar), or Windows with WSL2 |
| **Node.js** | Version 18 or later |
| **Terminal** | Terminal.app or iTerm2 (Mac), any terminal (Linux), Ubuntu via WSL2 (Windows) |
| **Internet** | Required for authentication and AI features |
| **Anthropic Account** | Claude Pro ($20/month) or Team plan |

---

## Step 1: Install Node.js

Claude Code runs on Node.js. You may already have it installed.

**Check if you already have it:**

```bash
node --version
```

If you see `v18.0.0` or higher (e.g., `v20.11.0`), skip to [Step 2](#step-2-install-claude-code).

If you see `command not found` or a version below 18, follow the instructions for your operating system below.

### macOS

**Option A -- Homebrew (recommended):**

```bash
brew install node
```

If you do not have Homebrew installed, open Terminal and run this first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the prompts, then run `brew install node`.

**Option B -- Download from nodejs.org:**

1. Go to https://nodejs.org
2. Download the **LTS** version (the button on the left)
3. Open the downloaded `.pkg` file and follow the installer
4. Close and reopen your terminal

### Linux (Ubuntu / Debian)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

For other Linux distributions, use your package manager or download the LTS version from https://nodejs.org.

### Windows

Claude Code does not run natively on Windows. You need WSL2 (Windows Subsystem for Linux) first.

**Install WSL2:**

1. Open **PowerShell as Administrator** (right-click PowerShell in the Start menu and select "Run as administrator")
2. Run:
   ```powershell
   wsl --install
   ```
3. Restart your computer when prompted
4. After reboot, the **Ubuntu** app will open automatically. If it does not, find it in the Start menu
5. Create a username and password when prompted

You now have a Linux terminal. All remaining steps in this guide should be run inside this Ubuntu terminal, not in PowerShell.

**Verify WSL2 is working:**

```bash
wsl --version
```

You should see version 2.x.

**Install Node.js inside WSL:**

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Verify Node.js

After installing, confirm it worked:

```bash
node --version
```

You should see `v18.0.0` or higher. If not, close your terminal, open a new one, and try again.

---

## Step 2: Install Claude Code

Run this command to install Claude Code globally:

```bash
npm install -g @anthropic-ai/claude-code
```

This may take a minute. When it finishes, verify the installation:

```bash
claude --version
```

You should see a version number. If you see `command not found`, see [Troubleshooting: command not found](#command-not-found-after-install) below.

If you see a permissions error during install, see [Troubleshooting: permission denied](#permission-denied-during-install) below.

---

## Step 3: Authenticate

Claude Code requires an Anthropic account with a paid plan.

### If you do not have an Anthropic account yet

1. Go to https://claude.ai
2. Click **Sign Up** and create an account
3. After signing in, upgrade to a **Pro plan** ($20/month) or **Team plan**
   - Click your name or profile icon in the bottom-left corner
   - Select **Settings** (or **Upgrade**)
   - Choose the Pro plan and enter payment information

### Authenticate Claude Code

In your terminal, run:

```bash
claude
```

The first time you launch Claude Code, it will open your default web browser and ask you to sign in to your Anthropic account. Sign in, authorize the connection, and return to your terminal.

You should see the Claude Code prompt -- a text input where you can type messages. This means authentication succeeded.

Type `/exit` to close Claude Code for now.

---

## Step 4: Verify Installation

Open your terminal and navigate to the bootcamp repo (adjust the path if you cloned it somewhere else):

```bash
cd ~/Desktop/bootcamp
```

Start Claude Code:

```bash
claude
```

Once the prompt appears, type:

```
What files are in this directory?
```

Claude Code should list the files and folders in the repo (e.g., `CLAUDE.md`, `README.md`, `agents/`, `setup/`). If it does, your installation is working correctly.

Type `/exit` to close Claude Code.

---

## Troubleshooting

### Command not found after install

**Symptom:** You see `claude: command not found` after running `npm install -g`.

**Cause:** The directory where npm installs global packages is not in your shell's PATH.

**Fix:**

1. Find where npm installed Claude Code:
   ```bash
   npm config get prefix
   ```

2. Take the output (e.g., `/usr/local` or `/home/yourname/.npm-global`) and add its `bin` subdirectory to your PATH. For example:
   ```bash
   export PATH=$(npm config get prefix)/bin:$PATH
   ```

3. Make this change permanent by adding that line to your shell profile. Run one of the following depending on your shell:

   **Mac (zsh is the default):**
   ```bash
   echo 'export PATH=$(npm config get prefix)/bin:$PATH' >> ~/.zshrc
   source ~/.zshrc
   ```

   **Linux / WSL (bash is the default):**
   ```bash
   echo 'export PATH=$(npm config get prefix)/bin:$PATH' >> ~/.bashrc
   source ~/.bashrc
   ```

4. Verify:
   ```bash
   claude --version
   ```

### Permission denied during install

**Symptom:** `EACCES: permission denied` when running `npm install -g`.

**Fix (recommended) -- Change npm's default directory:**

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
```

Add the new directory to your PATH. On Mac:

```bash
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

On Linux / WSL:

```bash
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

Then retry the install:

```bash
npm install -g @anthropic-ai/claude-code
```

**Fix (quick alternative) -- Use sudo:**

```bash
sudo npm install -g @anthropic-ai/claude-code
```

This works but is not recommended as a long-term habit.

### Authentication failed

**Symptom:** Claude Code opens the browser but authentication does not complete, or you see an error about your account.

**Fixes:**

1. Make sure you are signed in to https://claude.ai in your default browser before running `claude`
2. Confirm your account has an active Pro ($20/month) or Team plan -- free accounts will not work
3. Close all browser tabs related to Claude, then run `claude` again
4. If the browser window did not open, copy the URL from the terminal and paste it into your browser manually

### Behind a corporate firewall or proxy

**Symptom:** Claude Code installs but hangs when authenticating, or connections fail during use.

**Fixes:**

1. If you use a proxy, configure it for npm and your shell:
   ```bash
   npm config set proxy http://your-proxy:port
   npm config set https-proxy http://your-proxy:port
   export HTTP_PROXY=http://your-proxy:port
   export HTTPS_PROXY=http://your-proxy:port
   ```

2. Ask your IT team to allow outbound HTTPS connections (port 443) to:
   - `api.anthropic.com`
   - `claude.ai`
   - `registry.npmjs.org`

3. If your company uses a VPN, try disconnecting during setup and reconnecting after

### WSL-specific issues

**Symptom:** Commands work in PowerShell but not in WSL, or WSL does not start.

**Fixes:**

1. Make sure you are running all commands inside the Ubuntu terminal (WSL), not in PowerShell or Command Prompt
2. If WSL will not start, open PowerShell as Administrator and run:
   ```powershell
   wsl --update
   ```
3. If the Ubuntu app is missing from the Start menu, install it from the Microsoft Store (search for "Ubuntu")
4. If Node.js installed in WSL but `claude` is not found, you may need to set your PATH inside WSL (see [Command not found after install](#command-not-found-after-install))
5. If your browser does not open for authentication from WSL, copy the authentication URL from the terminal and paste it into a browser on the Windows side

---

## Pre-Bootcamp Checklist

Before Day 1, confirm all of the following:

- [ ] Node.js 18+ installed (`node --version` shows v18 or higher)
- [ ] Claude Code installed (`claude --version` shows a version number)
- [ ] Authenticated successfully (running `claude` opens the prompt without errors)
- [ ] Can run a basic command (Claude Code responds when you ask it a question)
- [ ] Bootcamp repo cloned (`ls` in the repo shows `CLAUDE.md`, `agents/`, `setup/`, etc.)

If any of these fail, check the [Troubleshooting](#troubleshooting) section above or the full [troubleshooting guide](troubleshooting.md).

---

**Estimated time:** 10-15 minutes on a standard setup.

**Having trouble?** Post in the bootcamp Slack/Discord channel before Day 1, or bring your questions to the session -- we build in dedicated setup time.
