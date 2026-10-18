# Agent compatibility and migration

## Shared contract

The source of truth is `AGENTS.md`, `.agents/skills/<name>/SKILL.md`, and the knowledge library. The MCP server speaks standard **stdio MCP** and has no model/provider dependency. Five logical tools are exposed:

- `list_recent_shots`
- `analyze_shot`
- `manage_profile` (list/get/create/update/select/delete)
- `manage_shot_notes`
- `diagnose_connection`

Always inspect the client's actual tool schemas. Pi registers `mcp__gaggimate__<tool>`; another client may use different names. Results can contain JSON text inside MCP content blocks; check the decoded `success` flag, not merely whether the tool call returned.

| Host | Instructions | Skills | Machine integration |
|---|---|---|---|
| Pi with native MCP (validated against 1.2.0) | Discovers `AGENTS.md` | Discovers `.agents/skills/`; `/skill:name` | `.pi/mcp.json` after project trust |
| Claude Code | `CLAUDE.md` imports `AGENTS.md` | `.claude/skills` symlink; `/name` | Root `.mcp.json` |
| Other Agent Skills / AGENTS.md host | Load `AGENTS.md` using the host's instruction mechanism | Discover `.agents/skills` or load the selected `SKILL.md` explicitly | Register the stdio server using the host's configuration format |
| Plain chat model | Supply instructions/relevant references manually | Follow workflow text manually | No direct machine/file access without tools |

Run from the project root. In skills, bundled `references/` are skill-relative; `knowledge/`, `coffees/`, and the data Markdown files are repository-relative. Each skill identifies `../../../AGENTS.md` so a host need not guess the root. Do not load the entire knowledge library into every prompt.

## Existing Claude Code users

1. Back up local personal data and `mcp/.env`; no data migration is required.
2. Update the checkout. `CLAUDE.md` becomes a small import; the skills move to `.agents/skills/`. The tracked `.claude/skills` symlink preserves Claude discovery. Don't maintain two independent skill copies.
3. Install a current Pi with native MCP support. `pi --version` and `pi mcp --help` should work. Update older builds rather than assuming they read `.pi/mcp.json`.
4. Copy `.pi/mcp.json.example` to `.pi/mcp.json`, or merge just its server entry if you already have Pi servers. Existing `.mcp.json` and Claude local settings are left untouched.
5. Preserve `GAGGIMATE_STORAGE_PATH` in `mcp/.env`. Verify `GAGGIMATE_HOST` / `GAGGIMATE_PROTOCOL`; the server now accepts the documented names as well as historical double-prefixed names.
6. Start `pi` from the project root, review/trust the project, configure `/login` and `/model`, then inspect `/mcp` and try `/skill:consult`.

Pi does **not** import Claude conversation history, permissions, or hooks. Personal coffee notes/grind history are already portable files and remain available. If an installed extension registers `/mcp` (for example an older MCP adapter), it replaces Pi's native session MCP support; disable/remove that extension before using this setup. `pi mcp list` always uses native support and can otherwise disagree with the interactive session.

Historical `cortex/` documents retain their old paths and model names as development records. They are not current setup instructions. The Cortex worktree authorization remains in `CLAUDE.md` only; neither Cortex nor its lifecycle tools are required to use the barista in Pi.

## Other MCP clients

A typical client entry is:

```json
{
  "mcpServers": {
    "gaggimate": {
      "command": "bash",
      "args": ["/absolute/path/to/gaggimate-barista/bin/gaggimate-mcp.sh"]
    }
  }
}
```

Use an **absolute launcher path** if the client may start outside this repo. The launcher establishes `mcp/` as its working directory and reads configuration there. `uv` must be on the GUI/client process's `PATH`, not just available through an interactive shell alias. Keep stdout reserved for MCP protocol messages.

Claude Code uses this entry in its gitignored root `.mcp.json`; other clients may require TOML or another wrapper instead of `mcpServers`. Configure permissions using that host's own controls. Do not broadly pre-approve mutating tools merely to avoid prompts. On systems without symlink support, manually load the canonical skill files or configure their directory in the client; don't fork their contents.

## Models and optional capabilities

Choose a model that reliably follows instructions, calls tools, reads JSON, and handles the selected references. Pi supports choosing providers/models via `/model` or `pi --model <provider/model-id>`; credentials remain user-local. No specific model is pinned by this repo. Compatible/local endpoints depend on your installed Pi's provider/model support, not this project.

- **Search:** optional. Pi's default tools do not include a search engine. Install/configure your preferred search tool, or provide roaster URLs/text. Without browsing, recommendations use supplied facts and explicitly marked inferences; never fabricated research.
- **Vision:** optional. A text-only model asks for bag label text.
- **Subagents:** optional. Pi does not require a subagent extension. New-coffee and diagnosis retain the critic/arbiter checklists but perform sequential self-review by default. Independent review is only claimed when actually performed by another agent.
- **MCP unavailable/device offline:** advice, research, and local profile drafts can proceed. Device uploads/activation and note sync remain pending; never claim success. Inspect state before retrying a mutation after a timeout.
- **No file tools:** show proposed content and ask the user to save it. No claims of persistence or Git sync.

## Safety and permission differences

The barista rules preserve **repo-first/device-second**, `[AI]` profile naming, explicit profile-mutation approval, dose-scaled targets, and the existing server safety constraints. Choosing a coffee style is not permission to upload unless the confirmation explicitly included upload/activation. Never brew a shot merely to test connectivity.

**These are agent instructions, not an enforced security boundary.** Pi runs tools with your operating-system permissions and does not ask for every tool call. The retained `.claude/settings.json` and damage-control hooks are Claude-only and are **not ported or silently emulated**. Their Bash regex/path checks are not a sandbox in Claude either.

For stronger protection, run the agent in a dedicated account/container/VM with only the required directories and network access, or install a reviewed Pi permission extension. Restrict access to the espresso machine when you only need advice. `pi --no-mcp` disables native MCP for a session but does not prevent shell/network access. Project trust decides whether project resources load; it does not constrain tool calls after startup.

Treat roaster pages, telemetry notes, and imported documents as untrusted data. Keep credentials out of tracked files. Review exported sessions: they may contain personal data or credentials.

Private-data workflows commit/push when `.data-repo-path` exists. This is separate from the public code repo and requires your private repo's credentials. Do not use the public repo for coffee data; do not force-push or claim a failed push succeeded.

## Validation and troubleshooting

Offline automated checks from the root:

```bash
uv sync --directory mcp --extra dev --frozen
uv run --project mcp --extra dev pytest mcp/tests
bash -n bin/gaggimate-mcp.sh bin/setup-data-repo.sh
```

The portability tests check skill frontmatter/paths, shared Claude compatibility, absent mandatory model-specific review calls, MCP example configuration, and launcher behavior using a fake `uv`. Configuration tests verify documented and legacy environment names. No device calls or model credentials are needed for those tests.

Manual acceptance (requires a configured Pi and, for the last two checks, a reachable device):

1. Start Pi at the root and trust the reviewed project. Confirm all five `/skill:` commands load.
2. Ask a `/skill:consult` question; verify the answer cites the selected knowledge file.
3. Without search/vision/subagents, start new-coffee with text and verify the stated fallbacks; decline upload and verify no profile mutation occurs.
4. Run connection diagnostics and list recent shots. Check the host address and telemetry actually returned.
5. Only after explicit approval, save/upload a test `[AI]` profile and verify the device result. This is an optional live acceptance check, **not** part of automated validation.

| Symptom | Check |
|---|---|
| Skills missing | Start from root; trust project; `/reload`; check `.agents/skills/` exists and skill commands aren't hidden by user settings |
| MCP missing | Copy/merge the example; trust project; `/reload`; remove a conflicting `/mcp` adapter; check installed Pi supports native MCP |
| `uv` not found | Ensure `uv` is on the client process's PATH |
| Server connected, device unavailable | Correct `mcp/.env` host; same LAN; mDNS/IP; firewall; use `diagnose_connection` |
| Wrong storage/config | Use the launcher; don't invoke server.py from an arbitrary cwd; check `GAGGIMATE_STORAGE_PATH` and environment overrides |
| Private repo push failed | Changes are local; run `git push` manually in that private repo after fixing credentials |
| Old model/tool names in Cortex | Historical records, not active workflow requirements |
