# Execution Plan: Recreate Project README (Landing Page UX & Multilingual Isomorphism)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: Both `README.md` (EN) and `README.fr.md` (FR) must follow the `build-readme` landing page architecture, adhere strictly to the Emerald & Neon Green palette (`#10B981` / `#34D399` / `#0D1117`), include all 21 tools and requested technical sections, have 0 Unicode emojis in headings, and maintain strict line-for-line isomorphism (`wc -l README.md == wc -l README.fr.md`).
- **Pre-requisites**: `build-readme` skill guidelines, `intelligible-search` benchmark examples, memory check verified (>3GB available), Python 3.10+ FastMCP codebase.

## 🛠️ Step-by-Step Sequence

### Step 1: Initialize Plan and Design Tokens
- [x] **Action**: Create `.GCC/branches/plan_readme_overhaul.md` and update `.GCC/main.md`.
- [x] **Verify**: Ensure design tokens and plan links are properly indexed.
- **Verification Proof**:
```text
Indexed in .GCC/main.md under ## 🌿 Active Branches / Plans
```

### Step 2: Subagent 1 — Architecture & English README Generation (`README.md`)
- [x] **Action**: Launch dedicated subagent to author `README.md` (Hero, Logo, Nav Badges, Meta Badges, Narrative Philosophy, 21 Tools Matrix, How It Works, Installation, MCP Clients Setup, CLI & Tool Details, Env Vars, Clean Uninstall, Dev & Zero-Slop).
- [x] **Verify**: Check file creation, block structure, and line count.
- **Verification Proof**:
```text
File generated at /home/omni/Code/gui_agent/README.md (495 lines, 30,065 bytes).
Compliance verified: Palette #10B981/#34D399/#0D1117, 0 header emojis, 21 FastMCP tools mapped.
```

### Step 3: Subagent 2 — French Localizer & Line-for-Line Isomorphism (`README.fr.md`)
- [x] **Action**: Launch dedicated subagent to author `README.fr.md` strictly aligned line-for-line with `README.md`.
- [x] **Verify**: Verify `wc -l README.md` equals `wc -l README.fr.md`.
- **Verification Proof**:
```text
  495 /home/omni/Code/gui_agent/README.md
  495 /home/omni/Code/gui_agent/README.fr.md
  990 total
Exact line count equality and structural isomorphism verified.
```

### Step 4: Subagent 3 — Quality Assurance, Compliance & Static Verification
- [x] **Action**: Launch QA subagent to verify formatting rules (0 heading emojis, border-radius on images, shields.io flat-square badges) and execute Zero-Slop pre-commit verification.
- [x] **Verify**: `ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit && ./venv/bin/pytest -v`
- **Verification Proof**:
```text
[Pre-Commit] Les 8 couches de validation Zero-Slop (Anti-leak, CVE, Ruff Lint, Format, Mypy, Sonar/Smells, Bandit, Semgrep) sont 100% validées.
============================== 7 passed in 0.95s ===============================
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Line count drift between English and French versions due to differing sentence lengths or wrapped text.
- **Mitigation**: Strictly match paragraph structures, empty lines, and table rows line-by-line. Subagent 3 verified exact line equality (495 lines each).
- **Risk**: Hero and logo images paths provided by user vs local assets.
- **Mitigation**: Standardized `assets/hero.png` and `assets/logo.png` references with `border-radius: 8px;` and inline dimensions allowing direct media drop-in or URL replacement.
