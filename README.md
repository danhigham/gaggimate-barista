# Gaggimate Barista

An AI espresso coach for [Pi](https://pi.dev) and other tool-capable agents, with [Gaggimate](https://gaggimate.com/) hardware integration. Choose your own model/provider; Claude is optional.

<img width="2816" height="1536" alt="Gaggimate Barista" src="https://github.com/user-attachments/assets/ae48eed2-c88a-49ae-8580-a8bf3fa2e148" />

## What it does

- Researches coffees and recommends starting grind, temperature, ratio, and profiles.
- Designs extraction profiles and uploads them **after your approval**.
- Correlates shot telemetry with taste feedback.
- Records grind settings, equipment preferences, and per-coffee tasting notes.

This is an agent project, not a standalone app. [`AGENTS.md`](AGENTS.md) defines the barista's behavior; [Agent Skills](.agents/skills/) define five workflows; `knowledge/` provides espresso references. The included Python MCP server (based on [Julian Leopold's gaggimate-mcp](https://github.com/julianleopold/gaggimate-mcp)) connects the agent to the machine. No model API is embedded in that server.

## Prerequisites

- **Pi with native MCP support** (migration validated against `@earendil-works/pi-coding-agent` **1.2.0**) and a configured model/provider. Check `pi --version` and `pi mcp --help`; older Pi builds may need updating.
- Node.js **22.19+** for current Pi; [`uv`](https://docs.astral.sh/uv/) and Python **3.13+** for the MCP server (`uv` can provision Python).
- Bash on Linux/macOS, or WSL on Windows, for the setup/launcher scripts.
- A Gaggimate-equipped machine on your network for live telemetry and profile management. Knowledge advice and local drafting work without it.

Install Pi following [pi.dev](https://pi.dev), or:

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

## Setup with Pi

### 1. Clone and enter the project

Clone this repository (or your fork), then:

```bash
cd gaggimate-barista
```

**Start Pi from this root directory**, not `mcp/`. Project MCP configuration is relative to the session directory.

### 2. Set up your personal data

**Local-only** (quickest start; run only for files you don't already have):

```bash
cp user-setup.example.md user-setup.md
cp grind-map.example.md grind-map.md
mkdir -p coffees
```

Edit `user-setup.md` with your machine, grinder, basket, scale, and preferences. These files are gitignored; back them up yourself or use a private repo.

**Private repo** (optional, for cross-machine sync): prepare a separate Git repo containing `coffees/`, `user-setup.md`, and `grind-map.md`. Start from the examples if needed. Then:

```bash
bin/setup-data-repo.sh /absolute/path/to/gaggimate-barista-data
```

Back up/move existing local data before running this script: it replaces the two Markdown files with symlinks and refuses to replace a real `coffees/` directory. It configures `GAGGIMATE_STORAGE_PATH` in `mcp/.env` and writes `.data-repo-path`. Data-writing workflows then commit and push to that **private** repo; configure its remote and credentials first. Without `.data-repo-path`, no automatic Git sync happens.

### 3. Install and configure the MCP server

```bash
uv sync --directory mcp --frozen
```

If `mcp/.env` does **not** exist, copy the example:

```bash
cp mcp/.env.example mcp/.env
```

If the private-data setup already created it, **edit it instead of overwriting it**. Preserve `GAGGIMATE_STORAGE_PATH` and add/update:

```dotenv
GAGGIMATE_HOST=gaggimate.local
GAGGIMATE_PROTOCOL=ws
```

Replace the hostname with your machine's IP if mDNS is unavailable. Use a hostname/IP only, not `http://...` or `/ws`. Use `wss` only if the device is configured for TLS. Environment variables override `.env`. The historical double-prefixed `GAGGIMATE_GAGGIMATE_HOST` / `GAGGIMATE_GAGGIMATE_PROTOCOL` names remain supported, but prefer the documented names above.

### 4. Enable the Pi MCP configuration

For a new configuration:

```bash
cp .pi/mcp.json.example .pi/mcp.json
```

If `.pi/mcp.json` already exists, merge the `gaggimate` entry instead of replacing other servers. The example runs `bash bin/gaggimate-mcp.sh`; the launcher changes to `mcp/` so `.env` and local storage resolve consistently. It requires `uv` on the client's `PATH`.

Configuration is intentionally opt-in and gitignored. No machine address, credentials, or model choice is committed. No MCP adapter extension is needed on current Pi.

### 5. Start Pi and verify

```bash
pi
```

Review and trust the project when prompted so Pi can load the project skills and MCP configuration. Use `/login` to configure your provider and `/model` to select a model. No Anthropic subscription is required unless you choose that provider.

- `/mcp` should show `gaggimate` connected with five tools.
- `/skill:consult What temperature should I use for a light roast?` checks skill loading without device operations.
- Ask for connection diagnostics or recent shots when you're ready to access the device.
- `/reload` reloads changed skills/configuration.

After trusting the project, `pi mcp list` checks MCP startup from the shell. A connected MCP server proves the **client/server handshake**, not that the espresso machine is reachable. Use `diagnose_connection` for device reachability; it does not brew or upload profiles.

For knowledge-only work, use `pi --no-mcp`.

## Workflows

| Pi command | Purpose |
|---|---|
| `/skill:new-coffee` | Research a bag, choose starting parameters, save coffee notes and optionally upload/activate a profile |
| `/skill:gaggimate-profiles` | Design, save, and optionally upload extraction profiles |
| `/skill:diagnose` | Analyze shot telemetry and recommend a targeted adjustment |
| `/skill:shot-feedback` | Record taste/rating/grind, update the journal, and sync shot notes |
| `/skill:consult` | Answer espresso questions from the knowledge library |

Natural language also works: “I've got a new bag” or “That shot was sour.” For bag photos, choose a vision-capable model; otherwise provide label text. Pi does not supply a web search tool by default: add your preferred search integration or provide roaster information. Without search, the agent must distinguish supplied facts from inferences.

The core loop: pull a shot yourself → give taste feedback → change one primary variable → repeat. Profiles are saved in `coffees/` **before** device upload; creating/uploading/activating profiles requires clear approval. Feedback recording and shot-note sync are normal parts of the requested feedback workflow.

## Other agents and migration

See [`docs/AGENT_COMPATIBILITY.md`](docs/AGENT_COMPATIBILITY.md) for:

- migrating an existing Claude Code checkout;
- Claude Code compatibility and generic MCP client configuration;
- model/capability requirements and graceful fallbacks;
- **safety differences**: Claude hooks do not run in Pi, and prompt instructions are not enforced permission gates;
- offline validation and troubleshooting.

“Model-independent” means a capable model in a host with the needed tools, **not** that every chat model can operate the machine. A plain chat interface can offer advice from supplied files, but cannot persist data or call MCP without a tool-enabled host.

## Project structure

```text
gaggimate-barista/
├── AGENTS.md                 # Canonical, provider-neutral barista instructions
├── CLAUDE.md                 # Compatibility import + optional Cortex authorization
├── .agents/skills/           # Five portable workflows and bundled references
├── .pi/mcp.json.example      # Opt-in Pi native MCP configuration
├── .claude/skills            # Symlink to ../.agents/skills (no duplicate content)
├── .claude/hooks/            # Legacy Claude-only guards; NOT active in Pi
├── bin/
│   ├── gaggimate-mcp.sh      # Stable stdio launcher for any MCP host
│   └── setup-data-repo.sh    # Wire a private data repo via symlinks
├── docs/AGENT_COMPATIBILITY.md
├── user-setup.example.md     # Equipment/preferences template
├── grind-map.example.md      # Grind-history template
├── user-setup.md             # Local or symlinked private data (gitignored)
├── grind-map.md              # Local or symlinked private data (gitignored)
├── coffees/                  # Per-coffee research, profiles, tasting notes (gitignored)
├── knowledge/                # Quick references, grinder guides, Automatic Pro profiles
│   └── reference/            # Deep-dive material, loaded on demand
├── mcp/                      # Python MCP server, tests, firmware regression fixtures
└── cortex/                   # Historical development plans/research; not a runtime dependency
```

## Data and customization

`coffees/`, `grind-map.md`, and `user-setup.md` may be local or symlinked to a private repo. MCP ratings/profile backups use `GAGGIMATE_STORAGE_PATH` (default `mcp/data/` when launched via the script). Keep it consistent when moving machines. The setup script points it at `{private-repo}/mcp-data/`. The public repo never needs your personal data.

- **Grinder:** set the Grinder field in `user-setup.md`. Sette and DF64V are mapped in `AGENTS.md`; another grinder needs a map entry and its quick-reference file, optionally a deep reference. Don't replace a different grinder's guide.
- **Basket/preferences:** edit `user-setup.md`; profile targets scale to dose × ratio.
- **Knowledge:** add concise guides to `knowledge/` and route them from `AGENTS.md`/skills. Deep material goes in `knowledge/reference/` and loads only when needed.
- **Model:** select it in your host, not in the skills. Critics use the configured model or a sequential self-review fallback.

To follow upstream improvements from a template/fork, add the original repository as an `upstream` remote, fetch, and merge its main branch after reviewing changes.

## Development checks (no machine required)

From the repository root:

```bash
uv sync --directory mcp --extra dev --frozen
uv run --project mcp --extra dev pytest mcp/tests
```

Tests include portable skill/configuration checks and a mocked launcher check. See [`mcp/README.md`](mcp/README.md) for firmware analyzer parity and fixture maintenance. Do not regenerate/capture live fixtures just to validate an agent migration.
