"""Offline checks for the shared agent contract and stdio client setup."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".agents" / "skills"
NAMES = {"consult", "diagnose", "gaggimate-profiles", "new-coffee", "shot-feedback"}


def test_canonical_skills_and_frontmatter():
    assert {p.name for p in SKILLS.iterdir() if p.is_dir()} == NAMES
    for name in NAMES:
        path = SKILLS / name / "SKILL.md"
        text = path.read_text()
        assert text.startswith("---\n")
        header = text.split("---", 2)[1]
        assert f"name: {name}\n" in header
        assert "description:" in header
        assert "../../../AGENTS.md" in text
        assert (path.parent / "../../../AGENTS.md").resolve() == ROOT / "AGENTS.md"
        assert f"/skill:{name}" in text
        # Literal bundled references must survive the move (ignore placeholders).
        for reference in re.findall(r"references/([A-Z_]+\.md)", text):
            assert (path.parent / "references" / reference).is_file()


def test_no_mandatory_claude_runtime_in_shared_skills():
    for path in SKILLS.rglob("*.md"):
        text = path.read_text()
        for obsolete in ("Task tool", "subagent_type", "model: opus", "model: sonnet",
                         "Spawn Sonnet", "Spawn Opus", "CLAUDE.md", "<command-name>"):
            assert obsolete not in text, (path, obsolete)
    for name in ("new-coffee", "diagnose"):
        text = (SKILLS / name / "references" / "SELF_CHECK.md").read_text()
        assert "sequentially in-session" in text
        assert "STATUS: CLEAR" in text and "STATUS: OBJECTIONS" in text


def test_grinder_contract_kept_in_sync():
    agents = (ROOT / "AGENTS.md").read_text()
    sentence = re.search(r'\*"(Per the AGENTS\.md Active Grinder.*?)"\*', agents).group(1)
    for name in ("consult", "new-coffee", "shot-feedback"):
        assert sentence in (SKILLS / name / "SKILL.md").read_text()


def test_claude_compatibility_uses_shared_source():
    link = ROOT / ".claude" / "skills"
    assert link.is_symlink()
    assert link.resolve() == SKILLS.resolve()
    assert "@AGENTS.md" in (ROOT / "CLAUDE.md").read_text()
    assert "cortex-managed" not in (ROOT / "AGENTS.md").read_text()


def test_pi_mcp_example():
    config = json.loads((ROOT / ".pi" / "mcp.json.example").read_text())
    server = config["mcpServers"]["gaggimate"]
    assert server["command"] == "bash"
    assert server["args"] == ["bin/gaggimate-mcp.sh"]
    assert server["cwd"] == "."
    assert server["exposure"] == "direct"
    assert (ROOT / server["args"][0]).is_file()
    ignored = (ROOT / ".gitignore").read_text().splitlines()
    assert ".pi/mcp.json" in ignored
    assert ".env" in ignored


@pytest.mark.skipif(shutil.which("bash") is None, reason="launcher requires Bash")
@pytest.mark.parametrize("exit_code", [0, 23])
def test_launcher_cwd_arguments_and_exit_status(tmp_path, exit_code):
    # A checkout containing spaces, launched from an unrelated directory.
    checkout = tmp_path / "checkout with spaces"
    (checkout / "bin").mkdir(parents=True)
    (checkout / "mcp").mkdir()
    launcher = checkout / "bin" / "gaggimate-mcp.sh"
    shutil.copyfile(ROOT / "bin" / launcher.name, launcher)
    fake_bin = tmp_path / "fake bin"
    fake_bin.mkdir()
    uv = fake_bin / "uv"
    uv.write_text(f'#!/bin/sh\nprintf "%s\\n" "$PWD" "$@"\nexit {exit_code}\n')
    uv.chmod(0o755)
    env = {**os.environ, "PATH": str(fake_bin) + os.pathsep + os.environ["PATH"]}
    result = subprocess.run(
        [shutil.which("bash"), str(launcher)], cwd=tmp_path, env=env,
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == exit_code
    assert result.stderr == ""
    assert result.stdout.splitlines() == [
        str(checkout / "mcp"), "run", "--frozen", "mcp", "run",
        "src/gaggimate_mcp/server.py",
    ]


@pytest.mark.skipif(shutil.which("bash") is None, reason="setup requires Bash")
def test_private_data_setup_is_idempotent_with_storage_only_env(tmp_path):
    checkout = tmp_path / "public checkout"
    private = tmp_path / "private data"
    (checkout / "bin").mkdir(parents=True)
    (checkout / "mcp").mkdir()
    (private / ".git").mkdir(parents=True)
    (private / "coffees").mkdir()
    for name in ("user-setup.md", "grind-map.md"):
        (private / name).write_text(f"Original {name}\n")
    setup = checkout / "bin" / "setup-data-repo.sh"
    shutil.copyfile(ROOT / "bin" / setup.name, setup)
    for _ in range(2):
        subprocess.run([shutil.which("bash"), str(setup), str(private)],
                       check=True, capture_output=True, text=True, timeout=10)
    assert (checkout / "mcp" / ".env").read_text() == (
        f"GAGGIMATE_STORAGE_PATH={private}/mcp-data\n"
    )
    assert (checkout / ".data-repo-path").read_text() == str(private)
    for name in ("user-setup.md", "grind-map.md", "coffees"):
        assert (checkout / name).resolve() == private / name
    assert (private / "user-setup.md").read_text() == "Original user-setup.md\n"
    assert (private / "mcp-data").is_dir()
