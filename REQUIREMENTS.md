# Enterprise SDD — Requirements & Dependencies

> **Last updated:** April 17, 2026
> **Scope:** Complete inventory of tools, languages, and libraries required to run Enterprise SDD.

---

## 1. Core Prerequisites (Required)

| Software | Min Version | Purpose | Verify | Install |
|----------|-------------|---------|--------|---------|
| **VS Code** | Latest stable | IDE — agent execution environment | Help → About | [code.visualstudio.com](https://code.visualstudio.com) |
| **GitHub Copilot** (extension) | Latest | AI model access for agents | Extensions → "GitHub Copilot" | VS Code Extensions marketplace |
| **GitHub Copilot Chat** (extension) | Latest | Chat UI — `@agent-name` invocation | Extensions → "GitHub Copilot Chat" | VS Code Extensions marketplace |
| **Git** | Any | Feature init, user identity, version control | `git --version` | [git-scm.com](https://git-scm.com) |
| **Python** | ≥ 3.11 | JSON parsing in Bash scripts; MCP servers runtime; `sdd` CLI | `python3 --version` (or `py --version` on Windows) | [python.org](https://www.python.org/downloads/) |

### Platform-specific shell

| Platform | Shell | Notes |
|----------|-------|-------|
| **Windows** | PowerShell 5.1+ (built-in) | Native `.ps1` scripts — no additional shell needed |
| **Windows** (Bash option) | Git Bash / WSL | Required only if using `.sh` scripts instead of `.ps1` |
| **macOS / Linux** | Bash (built-in) | Native `.sh` scripts |
| **macOS / Linux** (PS option) | PowerShell 7+ | Required only if using `.ps1` scripts instead of `.sh` |

---

## 2. Optional Dependencies

### 2.1 MCP Servers (Confluence, Jira, Spec Memory)

Only needed if using the optional MCP integrations for Atlassian access or spec memory.

| Dependency | Type | Version | Purpose |
|------------|------|---------|---------|
| **pip** | Package manager | Bundled with Python | Install MCP server dependencies |
| `mcp` | pip package | ≥1.0.0 | MCP protocol SDK — used by all 3 servers |
| `httpx` | pip package | ≥0.27.0 | HTTP client — used by Confluence and Jira servers |

Install all at once:
```bash
pip install -r mcp-servers/requirements.txt
```

**Environment variables** (set in `.env`, see `.env.example`):

| Variable | Required for | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub repo access | — |
| `CONFLUENCE_URL` | Confluence MCP | — |
| `CONFLUENCE_API_TOKEN` | Confluence MCP | — |
| `CONFLUENCE_USER_EMAIL` | Confluence MCP | — |
| `JIRA_URL` | Jira MPC | — |
| `JIRA_API_TOKEN` | Jira MPC | — |
| `JIRA_USER_EMAIL` | Jira MPC | — |
| `DATABASE_URL` | postgres MCP (future) | — |
| `BRAVE_API_KEY` | Brave web search | — |
| `SPEC_MEMORY_PATH` | spec-memory-server override | `./.specify/memory` |

### 2.2 Third-party MCP: `mcp-atlassian`

The Requirement Analyst agent declares `mcp-atlassian/confluence_get_page` and `mcp-atlassian/jira_get_issue` in its tool list. This is a separate community MCP server — **not** one of the 3 custom servers shipped with Enterprise SDD. Users must install it independently if they want the RA agent to pull Confluence/Jira data directly.

**Install:**
```bash
pip install mcp-atlassian
```

**GitHub:** [https://github.com/sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian)

Configure via VS Code MCP settings — see `.vscode/settings.json` for examples of MCP server configuration.

### 2.3 Download Scripts (Confluence/Jira export)

Located in `ai-framework/scripts/` (sibling to `enterprise-sdd/`, not inside it). These are standalone utilities for bulk-exporting Atlassian content to Markdown.

| Dependency | Type | Version | Purpose |
|------------|------|---------|---------|
| **Python** | Runtime | ≥ 3.8 | Script runtime |
| `atlassian-python-api` | pip package | 3.41.14 | Confluence + Jira API client |
| `html2text` | pip package | 2024.2.26 | HTML → Markdown conversion |
| `openpyxl` | pip package | 3.1.5 | Excel export for Jira data |
| `requests` | pip package | (transitive) | HTTP client — imported directly but installed as transitive dep of `atlassian-python-api` |

---

## 3. Bash Script Dependencies on Unix Tools

The `.sh` scripts use standard Unix commands. These are **built-in** on macOS/Linux and included with Git Bash or WSL on Windows.

| Command | Used by scripts |
|---------|----------------|
| `grep` | validate-gate, analyze-consistency, status, context-bridge, new-feature, resume-feature |
| `sed` | validate-gate, analyze-consistency |
| `awk` | analyze-consistency |
| `find` | validate-gate, generate-report, status |
| `sort` | analyze-consistency |
| `wc` | validate-gate, status |
| `cut` | validate-gate |
| `head` | analyze-consistency |
| `tr` | new-feature |
| `date` | validate-gate, context-bridge, new-feature, resume-feature |
| `basename` | All scripts |
| `mkdir`, `cat`, `test` | All scripts |

> The PowerShell `.ps1` scripts use **zero external commands** — only native cmdlets (`ConvertFrom-Json`, `Test-Path`, `Get-Content`, etc.). The only exception is `git config user.name` as a fallback in `new-feature.ps1`.

---

## 4. Runtime Language: Python Only

Enterprise SDD uses a single runtime language: **Python**.

### What Python does

Python serves three purposes:

#### Purpose A: JSON parsing in Bash scripts

The `.sh` scripts use `python3 -c` as an inline JSON parser because Bash has no native JSON support. Every invocation follows the same pattern:

```bash
value=$(python3 -c "import json; print(json.load(open('file.json',encoding='utf-8-sig')).get('field','default'))" 2>/dev/null || echo "default")
```

**Scripts that call `python3 -c`:**

| Script | # of calls | What it parses |
|--------|:----------:|----------------|
| `validate-gate.sh` | 3 | `.feature-meta.json` (ceremony level), `.lock` files (PID), `config.json` (test directories) |
| `resume-feature.sh` | 7 | `.checkpoint` files (gate, timestamp), `.lock` files (PID, timestamp, agent), `.feature-meta.json` |
| `context-bridge.sh` | 2 | `.checkpoint` (last gate), `.feature-meta.json` (ceremony level) |
| **Total** | **12** | All are simple "read a JSON file, extract one field" operations |

> **The `.ps1` scripts do NOT use Python.** They use PowerShell's native `ConvertFrom-Json` instead.

#### Purpose B: MCP server runtime

The 3 custom MCP servers (`confluence-server`, `jira-server`, `spec-memory-server`) are written in Python and use the `mcp` SDK (PyPI) with `stdio_server` transport.

#### Purpose C: Download scripts (optional)

The standalone download utilities (`download-confluence.py`, `download-jira.py`) in `ai-framework/scripts/` use Python with `atlassian-python-api`, `html2text`, and `openpyxl`.

### Optional: Node.js for contract linting

The validate-gate scripts optionally call `npx @redocly/cli lint` and `npx @asyncapi/cli validate` for OpenAPI/AsyncAPI contract validation. If `npx` (Node.js) is not installed, these checks are skipped with a warning — they are **not required**.

---

## 5. Migration Log: Node.js → Python (March 24, 2026)

Node.js was removed as a dependency. All functionality was migrated to Python.

### What changed

| Component | Before | After |
|-----------|--------|-------|
| **Bash script JSON parsing** (12 calls) | `node -e "console.log(require(...))"` | `python3 -c "import json; print(json.load(...))"` |
| **MCP servers** (3 servers) | JavaScript (`index.js`) + `@modelcontextprotocol/sdk` npm | Python (`server.py`) + `mcp` PyPI SDK |
| **VS Code MCP config** | `"command": "node"` / `"command": "npx"` | `"command": "python"` / `"command": "uvx"` |
| **Official MCP servers** (4: filesystem, github, memory, fetch) | `npx -y @modelcontextprotocol/server-*` | `uvx mcp-server-*` |
| **Install step** | `cd mcp-servers/<server> && npm install` per server | `pip install -r mcp-servers/requirements.txt` (one command) |

### Files modified

| File | Change |
|------|--------|
| `.specify/scripts/validate-gate.sh` | 3× `node -e` → `python3 -c` with `encoding='utf-8-sig'` |
| `.specify/scripts/resume-feature.sh` | 7× `node -e` → `python3 -c` with `encoding='utf-8-sig'` |
| `.specify/scripts/context-bridge.sh` | 2× `node -e` → `python3 -c` with `encoding='utf-8-sig'` |
| `mcp-servers/spec-memory-server/server.py` | New Python MCP server (replaces `index.js`) |
| `mcp-servers/confluence-server/server.py` | New Python MCP server (replaces `index.js`) |
| `mcp-servers/jira-server/server.py` | New Python MCP server (replaces `index.js`) |
| `mcp-servers/requirements.txt` | New shared pip requirements (`mcp`, `httpx`) |
| `.vscode/settings.json` | `node`/`npx` → `python`/`uvx` in all MCP server configs |
| `README.md` | Prerequisites, install steps, troubleshooting updated |
| `PLAYBOOK.md` | Prerequisites, install steps, troubleshooting updated |
| `REQUIREMENTS.md` | This file — full rewrite |

### What was NOT changed

- **PowerShell scripts** (`.ps1`): Never used Node.js — they use native `ConvertFrom-Json`
- **JavaScript source files** (`index.js`, `package.json`): Kept alongside Python files for backward compatibility. Can be deleted once migration is validated.
- **`npx @redocly/cli` / `npx @asyncapi/cli`**: Optional contract linting tools — remain as optional, gracefully skipped if not available
- **Bash scripts** other than the 3 above: `init.sh`, `new-feature.sh`, `status.sh`, `generate-report.sh`, `analyze-consistency.sh`, `sdd` — never used Node.js

---

## 6. Documentation Gaps — Status

Issues found during the dependency audit and their resolution:

| # | Gap | Severity | Status | Resolution |
|---|-----|----------|--------|------------|
| 1 | **PowerShell not in Prerequisites** | Medium | ✅ Fixed | §1 "Platform-specific shell" table documents PowerShell 7+ for macOS/Linux users choosing `.ps1` scripts. |
| 2 | **`mcp-atlassian` install not documented** | Medium | ✅ Fixed | §2.2 now includes `pip install mcp-atlassian` command and GitHub URL. |
| 3 | **GitHub Copilot Chat missing from README** | Low | ✅ Fixed | README now lists both "GitHub Copilot" and "GitHub Copilot Chat". |
| 4 | **`SPEC_MEMORY_PATH` env var not in `.env.example`** | Low | ✅ Fixed | Added to `.env.example` in Wave 14 Phase O. |
| 5 | **`requests` library implicit** | Low | ⏳ Deferred | `requests` is a transitive dependency of `atlassian-python-api`. Adding it to `requirements.txt` would duplicate dependency management. Documented as known caveat. |
| 6 | **Node.js listed as required** | Low | ✅ Fixed | Node.js replaced by Python in all prerequisites and install steps. |

---

## 7. Wave 20 — Operational Contracts (April 26, 2026)

### 7.1 Post-merge gate (`sdd gate post-merge`)

`.specify/config.yaml` MAY define under `gates.post_merge`:

```yaml
gates:
  post_merge:
    build_command: "<shell command>"   # required when post-merge is invoked
    test_command:  "<shell command>"   # required when post-merge is invoked
    fail_fast:     true                # optional, default true
```

Both commands MUST exit `0` on success. Output is captured into the feature's `gate-post-merge.report.md`. Missing keys cause `sdd gate post-merge <feature>` to abort with a clear error referencing this section.

### 7.2 Feature resolution priority

`sdd.utils.feature_resolver.resolve_feature_id(repo_root, explicit=None)` MUST honour this strict precedence:

1. `explicit` argument (e.g. `--feature 042-thing`)
2. `SDD_FEATURE` environment variable
3. `feature.lock.json` in the current/feature directory (`feature_id` field)
4. Branch heuristic (`feature/NNN-...` / `NNN-...`)

Each layer fails over to the next only when its source is absent, never on parse error.

### 7.3 Module manifest hashing

`module-install.{sh,ps1}` MUST record per-installed-file lowercase hex `sha256` plus an aggregate `manifestSha256` in `.sdd-modules/registry.json`:

```json
{
  "name": "<module-id>",
  "version": "<x.y.z>",
  "files": ["path/a", "path/b"],
  "fileHashes": {"path/a": "<sha256>", "path/b": "<sha256>"},
  "manifestSha256": "<sha256(\"path/a:<sha>\\npath/b:<sha>\\n\")>"
}
```

`sdd doctor` MUST surface drift as `WARN` (never `FAIL`); reconciliation is via `sdd module verify --reset` (reinstall) or `--accept` (re-baseline).

### 7.4 CLI deprecation contract

Every deprecated CLI flag/command MUST:

1. Be listed in the **Active** table of [`CLI-DEPRECATIONS.md`](CLI-DEPRECATIONS.md) before it is shipped.
2. Be wrapped with the `@deprecated(replacement=..., removal_version=..., migration=...)` decorator from `sdd.utils.deprecation` (all three kwargs are required).
3. Emit a single-line warning to `stderr` containing the literal tokens `replacement=`, `removal_version=`, and `migration=`.
4. Be removed from the Active table and added to the **Removed** table only at or after the declared `removal_version`.

`sdd doctor` MUST scan `.specify/config.yaml`, `.specify/scripts/*.sh`, and `.specify/scripts/*.ps1` for usage of Active deprecated tokens and surface findings as `WARN`.
