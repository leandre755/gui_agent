#!/usr/bin/env python3
"""Vérifie la logique métier et les invariants de sécurité des workflows GitHub Actions.

Ce script utilise uniquement la bibliothèque standard Python pour garantir
une portabilité totale en local (scripts CI, hooks) et en environnement GitHub Actions.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
USES_PATTERN = re.compile(r"^\s*(?:-\s*)?uses:\s*([^@\s]+)@([^\s#]+)(?:\s+#\s*(.+))?\s*$")
JOB_HEADER_PATTERN = re.compile(r"^ {2}([a-zA-Z0-9_-]+):\s*$")
TIMEOUT_PATTERN = re.compile(r"^\s*timeout-minutes:\s*([0-9]+)\s*$")
RUNS_ON_PATTERN = re.compile(r"^\s*runs-on:\s*([a-zA-Z0-9_.-]+)\s*$")


class WorkflowVerifier:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lines: list[str] = path.read_text(encoding="utf-8").splitlines()
        self.text: str = "\n".join(self.lines)
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def log_error(self, message: str, line_no: int | None = None) -> None:
        prefix = f"{self.path}:{line_no}: " if line_no is not None else f"{self.path}: "
        self.errors.append(f"{prefix}{message}")

    def log_warning(self, message: str, line_no: int | None = None) -> None:
        prefix = f"{self.path}:{line_no}: " if line_no is not None else f"{self.path}: "
        self.warnings.append(f"{prefix}{message}")

    def verify_forbidden_triggers(self) -> None:
        for idx, line in enumerate(self.lines, start=1):
            if re.search(r"^\s*pull_request_target\s*:", line):
                self.log_error(
                    "pull_request_target est formellement interdit pour des raisons de sécurité.",
                    line_no=idx,
                )

    def verify_top_level_permissions(self) -> None:
        # Vérifie la présence d'un bloc top-level permissions
        has_top_permissions = bool(re.search(r"^permissions:\s*(?:#.*)?$", self.text, flags=re.MULTILINE))
        if not has_top_permissions:
            self.log_error("Bloc top-level 'permissions:' manquant (least-privilege obligatoire).")

        # Interdiction absolue de write-all
        for idx, line in enumerate(self.lines, start=1):
            if re.search(r"permissions:\s*write-all\b", line):
                self.log_error("L'utilisation de 'permissions: write-all' est strictement interdite.", line_no=idx)

    def verify_concurrency(self) -> None:
        # Si le workflow écoute sur pull_request ou push, la clé concurrency top-level doit être définie
        has_pr_or_push = bool(re.search(r"^\s*(?:pull_request|push)\s*:", self.text, flags=re.MULTILINE))
        if has_pr_or_push:
            has_concurrency = bool(re.search(r"^concurrency:\s*(?:#.*)?$", self.text, flags=re.MULTILINE))
            if not has_concurrency:
                self.log_error("Bloc top-level 'concurrency:' manquant pour un workflow déclenché par PR ou push.")

    def verify_jobs_and_steps(self) -> None:
        in_jobs_block = False
        current_job: str | None = None
        job_lines: dict[str, list[tuple[int, str]]] = {}

        for idx, line in enumerate(self.lines, start=1):
            if re.match(r"^jobs:\s*(?:#.*)?$", line):
                in_jobs_block = True
                continue

            if in_jobs_block:
                # Si on rencontre une nouvelle clé de premier niveau (non indentée)
                if line and not line.startswith(" ") and not line.startswith("#"):
                    in_jobs_block = False
                    current_job = None
                    continue

                job_match = JOB_HEADER_PATTERN.match(line)
                if job_match:
                    current_job = job_match.group(1)
                    job_lines[current_job] = []
                    continue

                if current_job is not None:
                    job_lines[current_job].append((idx, line))

        if not job_lines:
            self.log_error("Aucun job défini sous la section 'jobs:'.")
            return

        for job_name, lines in job_lines.items():
            has_timeout = False
            has_runs_on = False

            for _idx, line in lines:
                if TIMEOUT_PATTERN.match(line):
                    has_timeout = True
                if RUNS_ON_PATTERN.match(line):
                    has_runs_on = True

            if not has_runs_on:
                self.log_error(f"Job '{job_name}' : directive 'runs-on:' obligatoire manquante.")
            if not has_timeout:
                self.log_error(f"Job '{job_name}' : directive 'timeout-minutes:' obligatoire manquante.")

    def verify_action_pins_and_credentials(self) -> None:
        for idx, line in enumerate(self.lines, start=1):
            if "persist-credentials: true" in line:
                self.log_error("persist-credentials: true est formellement interdit.", line_no=idx)

            match = USES_PATTERN.match(line)
            if not match:
                continue

            action, ref, comment = match.groups()
            if action.startswith("./") or action.startswith("docker://"):
                continue

            if not SHA_PATTERN.fullmatch(ref):
                self.log_error(
                    f"Action externe '{action}@{ref}' doit être immuablement épinglée sur un SHA complet de 40 caractères.",
                    line_no=idx,
                )
            elif not comment or not comment.startswith("v"):
                self.log_warning(
                    f"Action '{action}' : ajoutez un commentaire de version explicite (ex: # v4.4.2).",
                    line_no=idx,
                )

    def verify(self) -> tuple[int, list[str], list[str]]:
        self.verify_forbidden_triggers()
        self.verify_top_level_permissions()
        self.verify_concurrency()
        self.verify_jobs_and_steps()
        self.verify_action_pins_and_credentials()
        return len(self.errors), self.errors, self.warnings


def check_workflow(path: Path) -> tuple[int, list[str], list[str]]:
    verifier = WorkflowVerifier(path)
    return verifier.verify()


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(".github/workflows")
    if not root.is_dir():
        print(f"ERROR: Répertoire introuvable : {root}")
        return 2

    workflows = sorted([*root.glob("*.yml"), *root.glob("*.yaml")])
    if not workflows:
        print(f"ERROR: Aucun fichier de workflow YAML trouvé dans : {root}")
        return 2

    total_errors = 0
    for path in workflows:
        error_count, errors, warnings = check_workflow(path)
        for warn in warnings:
            print(f"WARNING: {warn}")
        for err in errors:
            print(f"ERROR: {err}")
        total_errors += error_count

    if total_errors:
        print(f"\nValidation refusée : {total_errors} erreur(s) détectée(s) dans les workflows.")
        return 1

    print(f"Validation réussie : {len(workflows)} workflow(s) GitHub Actions conformes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
