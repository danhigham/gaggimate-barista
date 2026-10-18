# Pi / portable-agent migration

## Goal
Review project documentation and migrate barista instructions, workflows and MCP setup to Pi with portable agent compatibility.

## Phases
1. Documentation and integration audit — complete
2. Implement portable instructions, skills and Pi connectivity — complete
3. Update onboarding and migration documentation — complete
4. Validate configuration, workflows and tests — complete

## Validation
- 257 pytest tests passed (including portability, launcher, data setup rerun, and env alias regressions).
- Pi 1.2.0 RPC discovered all five project skills without model prompts.
- Native Pi MCP connection and Python stdio handshake exposed all five tools using isolated temporary storage; no machine tool calls.
- Shell syntax, local onboarding links, moved-file preservation, managed Cortex block preservation, and git diff whitespace checks passed.
- Live device mutations and model-driven conversational acceptance remain intentionally untested; documented manual checks are available.

## Constraints
Preserve coffee data and safety requirements. Do not connect to or modify the espresso machine during validation. Commit and push only with user authorization (now explicitly granted for this migration).

## Errors
- One multi-edit rejected a non-unique text match in shot-feedback; no partial write. Retried with a newline anchor and succeeded.
- Native `pi mcp list` rejects --approve and ignores defaultProjectTrust for CLI discovery. Retried in an isolated temp agent directory with an explicit saved trust.json decision; project MCP connected successfully. User trust/config was never changed.
