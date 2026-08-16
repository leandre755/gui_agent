#!/usr/bin/env python3
"""Vérifie la logique métier et les invariants de sécurité des workflows GitHub Actions.

Ce script utilise uniquement la bibliothèque standard Python pour garantir
une portabilité totale en local (scripts CI, hooks) et en environnement GitHub Actions.
"""

from __future__ import annotations

import codecs
import re
import sys
from pathlib import Path

SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
USES_PATTERN = re.compile(r"^\s*(?:-\s*)?uses:\s*([^@\s]+)@([^\s#]+)(?:\s+#\s*(.+))?\s*$")
PERSIST_CREDENTIALS_TRUE_PATTERN = re.compile(r"^\s*persist-credentials:\s*true\b(?:\s*#.*)?$")


def decode_yaml_key(raw_key: str) -> str:
    """Décode une clé YAML potentiellement entourée de guillemets et contenant des échappements Unicode/Hex."""
    key = raw_key.strip()
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        quote = key[0]
        unquoted = key[1:-1]
        if quote == '"':
            try:
                return codecs.decode(unquoted, "unicode_escape")
            except Exception:
                return unquoted
        return unquoted
    return key


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

    def _extract_on_section(self) -> str:
        """Extrait les lignes correspondant à la directive top-level 'on:'."""
        in_on = False
        on_lines: list[str] = []
        for line in self.lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                if in_on:
                    on_lines.append(line)
                continue

            current_indent = len(line) - len(line.lstrip(" "))

            # Vérification de clé top-level (indentation 0)
            if current_indent == 0:
                top_match = re.match(r"^([^:]+):\s*(.*)$", line)
                if top_match:
                    raw_k = top_match.group(1).strip()
                    decoded_k = decode_yaml_key(raw_k)
                    if decoded_k == "on":
                        in_on = True
                        on_lines.append(line)
                        continue
                    elif in_on:
                        break

            if in_on:
                on_lines.append(line)
        return "\n".join(on_lines)

    def verify_forbidden_triggers(self) -> None:
        on_text = self._extract_on_section()
        if re.search(r"\bpull_request_target\b", on_text):
            self.log_error("pull_request_target est formellement interdit pour des raisons de sécurité.")

    def verify_top_level_permissions(self) -> None:
        has_top_permissions = False
        for idx, line in enumerate(self.lines, start=1):
            current_indent = len(line) - len(line.lstrip(" "))
            if current_indent == 0:
                top_match = re.match(r"^([^:]+):\s*(.*)$", line)
                if top_match:
                    raw_k = top_match.group(1).strip()
                    val = top_match.group(2).strip()
                    decoded_k = decode_yaml_key(raw_k)
                    if decoded_k == "permissions":
                        has_top_permissions = True
                        if re.match(r"^(?:write-all|write)\b", val):
                            self.log_error(
                                "L'utilisation de 'permissions: write-all' ou 'permissions: write' est strictement interdite.",
                                line_no=idx,
                            )

        if not has_top_permissions:
            self.log_error("Bloc top-level 'permissions:' manquant (least-privilege obligatoire).")

    def verify_concurrency(self) -> None:
        on_text = self._extract_on_section()
        has_pr_or_push = bool(re.search(r"\b(?:pull_request|push)\b", on_text))
        if has_pr_or_push:
            has_concurrency = False
            for line in self.lines:
                current_indent = len(line) - len(line.lstrip(" "))
                if current_indent == 0:
                    top_match = re.match(r"^([^:]+):\s*(.*)$", line)
                    if top_match:
                        raw_k = top_match.group(1).strip()
                        decoded_k = decode_yaml_key(raw_k)
                        if decoded_k == "concurrency":
                            has_concurrency = True
                            break

            if not has_concurrency:
                self.log_error("Bloc top-level 'concurrency:' manquant pour un workflow déclenché par PR ou push.")

    def _parse_job_blocks(self) -> dict[str, list[tuple[int, str]]]:
        in_jobs_block = False
        jobs_indent: int | None = None
        current_job: str | None = None
        job_indent: int | None = None
        job_direct_properties: dict[str, list[tuple[int, str]]] = {}

        for idx, line in enumerate(self.lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            current_line_indent = len(line) - len(line.lstrip(" "))

            # Détection de la section top-level 'jobs:'
            if not in_jobs_block:
                if current_line_indent == 0:
                    top_match = re.match(r"^([^:]+):\s*(?:#.*)?$", line)
                    if top_match and decode_yaml_key(top_match.group(1).strip()) == "jobs":
                        in_jobs_block = True
                        jobs_indent = current_line_indent
                continue

            # Sortie de la section jobs lors d'une nouvelle clé top-level
            if jobs_indent is not None and current_line_indent <= jobs_indent:
                in_jobs_block = False
                current_job = None
                continue

            # Détection d'un en-tête de job
            header_match = re.match(r"^(\s+)([^:]+):\s*$", line)
            if header_match and (job_indent is None or current_line_indent == job_indent):
                job_indent = len(header_match.group(1))
                current_job = decode_yaml_key(header_match.group(2).strip())
                job_direct_properties[current_job] = []
                continue

            # Accumulation des propriétés du job en cours
            if current_job is not None and job_indent is not None:
                if current_line_indent < job_indent:
                    in_jobs_block = False
                    current_job = None
                    continue
                job_direct_properties[current_job].append((idx, line))

        return job_direct_properties

    def _validate_single_job(self, job_name: str, lines: list[tuple[int, str]]) -> None:
        has_timeout = False
        has_runs_on = False

        direct_prop_indent: int | None = None
        for _idx, line in lines:
            indent = len(line) - len(line.lstrip(" "))
            if direct_prop_indent is None or indent < direct_prop_indent:
                direct_prop_indent = indent

        for i, (_idx, line) in enumerate(lines):
            indent = len(line) - len(line.lstrip(" "))
            if direct_prop_indent is not None and indent == direct_prop_indent:
                if re.match(
                    r"^\s*(?:timeout-minutes|\"timeout-minutes\"|'timeout-minutes'):\s*(\d+|\$\{\{.+?\}\})(?:\s*#.*)?$",
                    line,
                ):
                    has_timeout = True

                runs_on_match = re.match(r"^\s*(?:runs-on|\"runs-on\"|'runs-on'):\s*(.*)$", line)
                if runs_on_match:
                    inline_val = runs_on_match.group(1).strip()
                    if inline_val and not inline_val.startswith("#"):
                        has_runs_on = True
                    else:
                        for _next_idx, next_line in lines[i + 1 :]:
                            next_indent = len(next_line) - len(next_line.lstrip(" "))
                            if next_indent <= direct_prop_indent:
                                break
                            if next_line.strip().startswith("-"):
                                has_runs_on = True
                                break

        if not has_runs_on:
            self.log_error(f"Job '{job_name}' : directive 'runs-on:' obligatoire manquante au niveau du job.")
        if not has_timeout:
            self.log_error(f"Job '{job_name}' : directive 'timeout-minutes:' obligatoire manquante au niveau du job.")

    def verify_jobs_and_steps(self) -> None:
        job_direct_properties = self._parse_job_blocks()
        if not job_direct_properties:
            self.log_error("Aucun job défini sous la section 'jobs:'.")
            return

        for job_name, lines in job_direct_properties.items():
            self._validate_single_job(job_name, lines)

    def verify_action_pins_and_credentials(self) -> None:
        for idx, line in enumerate(self.lines, start=1):
            if PERSIST_CREDENTIALS_TRUE_PATTERN.match(line):
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
