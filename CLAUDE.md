# Git-Context-Controller (GCC) Protocol

This protocol governs context persistence, architecture tracking, and session handoff mechanics. It must be strictly executed by the AI agent at specific session milestones.

<file_matrix>
<file path=".GCC/main.md" lifecycle="persistent">
<scope>
Acts as the global project registry. Contains high-level milestones, objective, chronological decision log, and an active index of valid plans.
</scope>
</file>
<file path=".GCC/branches/plan_[name].md" lifecycle="transient">
<scope>
Step-by-step tactical implementation plan for complex, multi-session epics only.
</scope>
</file>
<file path=".GCC/resume.md" lifecycle="dynamic">
<scope>
Factual technical changelog and precise transition state. Overwritten at the absolute end of every session to ensure seamless state-recovery in fresh chat environments.
</scope>
</file>
<file path=".GCC/branches/test.md" lifecycle="persistent">
<scope>
Persistent test execution log, tracking completed tests, results, bugs found, and fixes applied.
</scope>
</file>
<file path=".GCC/branches/test_afaire.md" lifecycle="persistent">
<scope>
Test backlog tracking all pending scenarios and test suites to be executed.
</scope>
</file>
</file_matrix>

<event_driven_protocols>

<protocol id="A" name="session_bootstrap">
<trigger>Agent receives the first message from the user in a new chat/session.</trigger>
<step id="1">
<action>TOOL INVOCATION: Read `.GCC/main.md` to load the project's macro state and retrieve active plans.</action>
</step>
<step id="2">
<action>TOOL INVOCATION: Read `.GCC/resume.md` (if it exists) to retrieve the precise technical transition state and immediate next-action directives.</action>
</step>
<step id="3" phase="context_alignment">
<instruction>
Complete the context restoration (Step 1 and Step 2) prior to making any code or file modifications outside of the `.GCC/` directory. This ensures full alignment with the codebase state before taking action.
</instruction>
</step>
<step id="4">
<action>State the current technical objective loaded from `resume.md` using factual, concise French to align with the user.</action>
</step>
</protocol>

<protocol id="B" name="task_planning_and_execution">
<trigger>A complex, multi-session, or multi-file architectural change is initiated.</trigger>
<planning_threshold>
<instruction>
Reserve plan creation (`.GCC/branches/plan_[task_name].md`) for structural refactorings, package migrations, or multi-module tasks. For simple, single-file edits or quick bug fixes (< 10 minutes), proceed directly with implementation without generating a plan file.
</instruction>
</planning_threshold>
<step id="1">
<action>TOOL INVOCATION: Create the plan file `.GCC/branches/plan_[task_name].md` using the precise template below.</action>
</step>
<step id="2">
<action>TOOL INVOCATION: Update `.GCC/main.md` under `## 🌿 Active Branches / Plans` with the plan's exact file link and scope.</action>
</step>
<step id="3" execution="sequential_verification">
<instruction>
Execute the plan sequentially, step by step:
1. Modify the targeted code for the active step.
2. Run validation tools (tests, compilers, linters).
3. Paste the raw, unaltered terminal outputs into the plan file as proof of verification before modifying adjacent files or proceeding to the next step.
</instruction>
</step>
<step id="4" name="proactive_risk_management">
<instruction>
When documenting risks under "Mitigations & Edge Cases" in a plan file, proactively summarize the identified risk and proposed mitigation directly to the user in the chat. Do not wait for the user to read `.GCC/` files. Explicitly inform the user whether you are applying the mitigation autonomously or if their input/verification is required before proceeding.
</instruction>
</step>
</protocol>

<protocol id="C" name="decision_logging">
<trigger>Any package dependency change, design pattern choice, database schema modification, or structural API boundary pivot.</trigger>
<step id="1">
<action>
TOOL INVOCATION: Immediately append the technical choice, discarded alternative options, and concrete technical reasoning inside `.GCC/main.md` under `## 🧠 Decisions Made` at the moment the decision is established.
</action>
</step>
</protocol>

<protocol id="D" name="session_teardown_and_handoff">
<trigger>The user signals the end of the session, or the agent approaches context/token capacity limits.</trigger>
<step id="1">
<action>TOOL INVOCATION: Run the project's compilation and static validation tools to verify codebase integrity.</action>
</step>
<step id="2">
<action>TOOL INVOCATION: Update `.GCC/main.md` status, archiving completed milestones and updating active targets.</action>
</step>
<step id="3" verification="user_confirmation">
<instruction>
Maintain plan files in an active state until all related tasks and bugs are verified and logged in `.GCC/branches/test.md`, and the user provides explicit written confirmation in the chat to delete or archive the plan.
</instruction>
</step>
<step id="4" quality="technical_precision">
<action>
TOOL INVOCATION: Overwrite `.GCC/resume.md` with ultra-precise transition details.
</action>
<instruction>
Write technically descriptive entries that explicitly detail specific file paths, function signatures, modified line numbers, exact terminal commands, and raw error logs to ensure seamless handoff recovery.
</instruction>
</step>
</protocol>

<protocol id="E" name="test_session_sync">
<trigger>Completion of any automated or manual test run.</trigger>
<step id="1">
<action>TOOL INVOCATION: Move completed test scenarios from `.GCC/branches/test_afaire.md` to `.GCC/branches/test.md` with explicit results.</action>
</step>
<step id="2">
<action>TOOL INVOCATION: Append newly discovered bugs, regressions, or integration blocks to `.GCC/branches/test.md` immediately upon discovery.</action>
</step>
</protocol>

</event_driven_protocols>

<strict_markdown_templates>

### 3.1. `.GCC/main.md` Template

```markdown
# Current Project Context

## 🏆 Major Milestones (Archived Epics)
- [YYYY-MM-DD] Name of completed milestone/epic

## 🎯 Objective
[High-level description of what the project is solving or building]

## 🧠 Decisions Made
- [YYYY-MM-DD] [Technical choice name]
- **Context**: [Why the decision was necessary]
- **Discarded Options**: [Option A, Option B with brief technical rejection reasons]
- **Rationale**: [Concrete architectural justification for the selected path]

## 🌿 Active Branches / Plans
- `[branch-or-task-name]` : [Factual description of the task being solved and link to the plan file]

## 📈 Current Status
- ✅ Done: [List of high-level completed features]
- 🔄 In progress: [High-level epic currently being built]
- ⏳ Pending: [Remaining roadmap items]

## 👉 Next Session Direction
[Single sentence summarizing where the project points next]
```

### 3.2. `.GCC/branches/plan_[name].md` Template

```markdown
# Execution Plan: [Task Name]

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: [State the state/rule that must remain true during and after this task]
- **Pre-requisites**: [Required packages, configurations, or pre-existing code structures]

## 🛠️ Step-by-Step Sequence

### Step 1: [Short Action Description]
- [ ] **Action**: [Exact file path to edit or command to run]
- [ ] **Verify**: [Validation command, e.g., `npm test`, `tsc --noEmit`]
- **Verification Proof**:
```text
[Paste terminal/compiler validation output here]
```

### Step 2: [Short Action Description]
- [ ] **Action**: [Exact file path to edit or command to run]
- [ ] **Verify**: [Validation command]
- **Verification Proof**:

```text
[Paste validation output here]
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: [Identify potential risk, e.g., API rate-limits, dependency clash]
- **Mitigation**: [Describe fallback behavior]

```

### 3.3. `.GCC/resume.md` Template

```markdown
# Session Handoff

## 🎯 Functional Outcome & Task Reality
- **Requested Task**: [Brief description of what was asked]
- **Functional Status**: [SUCCESS | PARTIAL | FAILED]
- **Behavioral Proof**: [Factual output of runtime test, execution result, or physical check proving whether the feature actually WORKS, independent of compilation]

## ⚡ Technical Diffs / Atomic Modifications
- **File**: `[path/to/modified_file_1.ext]`
- **Scope**: [Added/Modified functions or components]
- **Exact Technical Change**: [Factual description of the changes]

## 🛠️ Static Codebase Health
- **Verification Command Run**: `[e.g., npm run build && tsc --noEmit]`
- **Linter/Compiler Status**: [Paste clean terminal output showing 0 errors, 0 warnings]

## 🚧 Unfinished Work & Technical Failures
- **Blocker / Failure Explanation**: [If Functional Status is PARTIAL or FAILED, explain explicitly WHY it failed, raw error logs, and why static compilation was not enough]

## 👉 Handover Directives for the Next Agent
1. **Target File**: `[Specify exact file path to open first]`
2. **Immediate Action**: `[Specify exact next action or fix to apply]`
3. **Verification Command**: `[Command to run]`

```

---
</strict_markdown_templates>
