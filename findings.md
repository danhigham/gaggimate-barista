# Findings

- Initial working tree is clean. Repository contains `.claude`, `CLAUDE.md`, Python MCP server, knowledge library and setup scripts.
- Private data links are not present in the root listing; migration must preserve template-based onboarding.
- Inventoried all 180 tracked Markdown documents and indexed documentation (including historical Cortex plans). Runtime instructions are in CLAUDE.md and five .claude/skills workflows.
- Installed Pi supports native MCP via .pi/mcp.json and portable .agents/skills discovery; no third-party MCP bridge or custom extension is needed.
- Portability blockers: Claude Task-tool/Sonnet/Opus review requirements, ambiguous skill-relative paths, Claude-only hooks, and README onboarding that omits device host configuration.
- Preserve historical Cortex records and optional Claude hooks; explicitly document that those hooks are not Pi security controls. Use sequential review fallback for runtimes without subagents.
- Confirmed environment configuration bug: env_prefix plus gaggimate_host/protocol field names formerly required double prefixes despite .env.example documenting single prefixes. Explicit aliases now accept both; all config tests pass.
- Pi 1.2.0 RPC auto-discovers all five canonical skills. Actual native Pi MCP listing connects using the shipped example and reports all five tools; no machine calls were made.
- Native `pi mcp list` requires a saved trust decision, not --approve or defaultProjectTrust. README correctly instructs trusting the project interactively first.
- Full automated suite: 257 passed. MCP handshake, shell syntax and git diff whitespace checks pass. No live upload or model-driven taste workflow was tested.
