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


def strip_yaml_comment(line: str) -> str:
    """Supprime les commentaires YAML en fin de ligne en préservant le contenu entre guillemets."""
    in_single = False
    in_double = False
    escaped = False
    for idx, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_double:
            escaped = True
            continue
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:idx].rstrip()
    return line


def _split_flow_tokens(content: str) -> list[str]:
    """Divise une chaîne flow-style YAML au niveau d'imbrication 0."""
    tokens: list[str] = []
    depth = 0
    in_single = False
    in_double = False
    escaped = False
    current: list[str] = []

    for char in content:
        if escaped:
            escaped = False
            current.append(char)
            continue
        if char == "\\" and in_double:
            escaped = True
            current.append(char)
            continue
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif not in_single and not in_double:
            if char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
            elif char == "," and depth == 0:
                tok = "".join(current).strip()
                if tok:
                    tokens.append(tok)
                current = []
                continue
        current.append(char)

    last_tok = "".join(current).strip()
    if last_tok:
        tokens.append(last_tok)
    return tokens


def _extract_key_from_flow_pair(pair: str) -> str | None:
    """Extrait la clé d'une paire flow-style au niveau 0 d'imbrication."""
    p_depth = 0
    p_in_single = False
    p_in_double = False
    p_escaped = False
    for idx, char in enumerate(pair):
        if p_escaped:
            p_escaped = False
            continue
        if char == "\\" and p_in_double:
            p_escaped = True
            continue
        if char == "'" and not p_in_double:
            p_in_single = not p_in_single
        elif char == '"' and not p_in_single:
            p_in_double = not p_in_double
        elif not p_in_single and not p_in_double:
            if char in "[{":
                p_depth += 1
            elif char in "]}":
                p_depth -= 1
            elif char == ":" and p_depth == 0:
                return pair[:idx].strip()
    return None


def parse_inline_yaml_triggers(val: str) -> set[str]:
    """Parse une valeur inline YAML (flow-style sequence, flow-style mapping, ou scalaire)."""
    trimmed = val.strip()
    if not trimmed:
        return set()

    if trimmed.startswith("[") and trimmed.endswith("]"):
        items = _split_flow_tokens(trimmed[1:-1])
        return {decode_yaml_key(item) for item in items if item}

    if trimmed.startswith("{") and trimmed.endswith("}"):
        pairs = _split_flow_tokens(trimmed[1:-1])
        keys: set[str] = set()
        for pair in pairs:
            raw_k = _extract_key_from_flow_pair(pair)
            if raw_k:
                keys.add(decode_yaml_key(raw_k))
        return keys

    return {decode_yaml_key(trimmed)}


def is_complete_flow_collection(value: str) -> bool:
    depth = 0
    in_single = False
    in_double = False
    escaped = False
    saw_collection = False

    for char in value:
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_double:
            escaped = True
            continue
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif not in_single and not in_double:
            if char in "[{":
                depth += 1
                saw_collection = True
            elif char in "]}":
                depth -= 1

    return saw_collection and depth == 0


class WorkflowVerifier:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lines: list[str] = path.read_text(encoding="utf-8").splitlines()
        self.text: str = "\n".join(self.lines)
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.anchors: dict[str, set[str]] = self._scan_yaml_anchors()

    def _scan_yaml_anchors(self) -> dict[str, set[str]]:
        """Scanne les ancres YAML simples (&anchor_name value) pour résoudre les alias (*anchor_name)."""
        anchors: dict[str, set[str]] = {}
        for idx, line in enumerate(self.lines):
            stripped = strip_yaml_comment(line).strip()
            anchor_match = re.search(r"&([a-zA-Z0-9_-]+)\s*(.*)$", stripped)
            if not anchor_match:
                continue

            name = anchor_match.group(1)
            val = anchor_match.group(2).strip()
            if val:
                anchors[name] = parse_inline_yaml_triggers(val)
                continue

            anchor_indent = len(line) - len(line.lstrip(" "))
            child_lines: list[str] = []
            for child_line in self.lines[idx + 1 :]:
                child_stripped = strip_yaml_comment(child_line).rstrip()
                if not child_stripped.strip():
                    continue
                child_indent = len(child_line) - len(child_line.lstrip(" "))
                if child_indent <= anchor_indent:
                    break
                child_lines.append(child_stripped)

            triggers: set[str] = set()
            for child_line in child_lines:
                child_stripped = child_line.strip()
                key_match = re.match(r"^([^:]+):", child_stripped)
                if key_match:
                    triggers.add(decode_yaml_key(key_match.group(1).strip()))
            anchors[name] = triggers
        return anchors

    def log_error(self, message: str, line_no: int | None = None) -> None:
        prefix = f"{self.path}:{line_no}: " if line_no is not None else f"{self.path}: "
        self.errors.append(f"{prefix}{message}")

    def log_warning(self, message: str, line_no: int | None = None) -> None:
        prefix = f"{self.path}:{line_no}: " if line_no is not None else f"{self.path}: "
        self.warnings.append(f"{prefix}{message}")

    def _resolve_trigger_token(self, token: str) -> set[str]:
        tok = token.strip()
        if not tok:
            return set()
        # Résolution d'alias YAML (ex: *unsafe_events)
        if tok.startswith("*"):
            alias_name = tok[1:].strip()
            return self.anchors.get(alias_name, set())
        # Déclaration inline flow-style
        if (tok.startswith("[") and tok.endswith("]")) or (tok.startswith("{") and tok.endswith("}")):
            return parse_inline_yaml_triggers(tok)
        return {decode_yaml_key(tok)}

    def _parse_triggers(self) -> set[str]:
        """Extrait et décode l'ensemble des événements déclencheurs sous la directive top-level 'on:'."""
        in_on = False
        on_child_lines: list[str] = []
        inline_flow_value: str | None = None

        for line in self.lines:
            stripped_code = strip_yaml_comment(line).rstrip()
            if not stripped_code.strip():
                continue

            current_indent = len(line) - len(line.lstrip(" "))

            if current_indent == 0:
                top_match = re.match(r"^([^:]+):\s*(.*)$", stripped_code)
                if top_match:
                    raw_k = top_match.group(1).strip()
                    if decode_yaml_key(raw_k) == "on":
                        in_on = True
                        inline_val = top_match.group(2).strip()
                        if inline_val:
                            anchor_match = re.fullmatch(r"&[a-zA-Z0-9_-]+(?:\s+(.*))?", inline_val)
                            trigger_value = anchor_match.group(1) if anchor_match else inline_val
                            if trigger_value:
                                if is_complete_flow_collection(trigger_value):
                                    return self._resolve_trigger_token(trigger_value)
                                if trigger_value.startswith(("[", "{")):
                                    inline_flow_value = trigger_value
                                else:
                                    return self._resolve_trigger_token(trigger_value)
                        continue
                    if in_on and inline_flow_value is None:
                        break

            if not in_on:
                continue
            if inline_flow_value is not None:
                inline_flow_value = f"{inline_flow_value} {stripped_code.strip()}"
                if is_complete_flow_collection(inline_flow_value):
                    return parse_inline_yaml_triggers(inline_flow_value)
                continue
            on_child_lines.append(stripped_code)

        if inline_flow_value is not None:
            return parse_inline_yaml_triggers(inline_flow_value)
        if not on_child_lines:
            return set()

        # Identifier le niveau d'indentation direct des événements déclarés sous 'on:'
        min_child_indent: int | None = None
        for line in on_child_lines:
            indent = len(line) - len(line.lstrip(" "))
            if min_child_indent is None or indent < min_child_indent:
                min_child_indent = indent

        triggers: set[str] = set()
        for line in on_child_lines:
            indent = len(line) - len(line.lstrip(" "))
            if min_child_indent is not None and indent == min_child_indent:
                stripped = line.strip()
                # Séquence YAML (ex: '- push' ou '- "push"')
                if stripped.startswith("-"):
                    item = stripped[1:].strip()
                    triggers.update(self._resolve_trigger_token(item))
                elif (stripped.startswith("[") and stripped.endswith("]")) or (
                    stripped.startswith("{") and stripped.endswith("}")
                ):
                    # Block-form flow collection (ex: '  [pull_request_target]' ou '  {push: null}')
                    triggers.update(parse_inline_yaml_triggers(stripped))
                elif stripped.startswith("*"):
                    # Alias YAML en bloc (ex: '  *unsafe_events')
                    triggers.update(self._resolve_trigger_token(stripped))
                else:
                    # Mapping direct (ex: 'push:' ou '"pull_request_target":')
                    key_match = re.match(r"^([^:]+):", stripped)
                    if key_match:
                        raw_event = key_match.group(1).strip()
                        triggers.add(decode_yaml_key(raw_event))

        return triggers

    def verify_forbidden_triggers(self) -> None:
        triggers = self._parse_triggers()
        if "pull_request_target" in triggers:
            self.log_error("pull_request_target est formellement interdit pour des raisons de sécurité.")

    def verify_top_level_permissions(self) -> None:
        has_top_permissions = False
        for idx, line in enumerate(self.lines, start=1):
            stripped_code = strip_yaml_comment(line).rstrip()
            current_indent = len(line) - len(line.lstrip(" "))
            if current_indent == 0:
                top_match = re.match(r"^([^:]+):\s*(.*)$", stripped_code)
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
        triggers = self._parse_triggers()
        has_pr_or_push = bool(triggers.intersection({"pull_request", "push"}))
        if has_pr_or_push:
            has_concurrency_group = False
            for idx, line in enumerate(self.lines):
                stripped_code = strip_yaml_comment(line).rstrip()
                current_indent = len(line) - len(line.lstrip(" "))
                if current_indent != 0:
                    continue

                top_match = re.match(r"^([^:]+):\s*(.*)$", stripped_code)
                if not top_match or decode_yaml_key(top_match.group(1).strip()) != "concurrency":
                    continue

                inline_value = top_match.group(2).strip()
                if inline_value:
                    if inline_value.startswith("{") and inline_value.endswith("}"):
                        group_match = re.search(r"(?:^|,)\s*group\s*:\s*([^,}]+)", inline_value[1:-1])
                        has_concurrency_group = bool(group_match and group_match.group(1).strip())
                    else:
                        has_concurrency_group = True
                    break

                for child_line in self.lines[idx + 1 :]:
                    child_code = strip_yaml_comment(child_line).rstrip()
                    if not child_code.strip():
                        continue
                    child_indent = len(child_line) - len(child_line.lstrip(" "))
                    if child_indent == 0:
                        break
                    group_match = re.match(r"^\s*group:\s*(\S.*)$", child_code)
                    if group_match and group_match.group(1).strip():
                        has_concurrency_group = True
                    break

            if not has_concurrency_group:
                self.log_error(
                    "Bloc top-level 'concurrency:' manquant ou sans groupe non vide pour un workflow déclenché par PR ou push."
                )

    def _parse_job_blocks(self) -> dict[str, list[tuple[int, str]]]:
        in_jobs_block = False
        jobs_indent: int | None = None
        current_job: str | None = None
        job_indent: int | None = None
        job_direct_properties: dict[str, list[tuple[int, str]]] = {}

        for idx, line in enumerate(self.lines, start=1):
            stripped_code = strip_yaml_comment(line).rstrip()
            if not stripped_code.strip():
                continue

            current_line_indent = len(line) - len(line.lstrip(" "))

            # Détection de la section top-level 'jobs:'
            if not in_jobs_block:
                if current_line_indent == 0:
                    top_match = re.match(r"^([^:]+):\s*(?:#.*)?$", stripped_code)
                    if top_match and decode_yaml_key(top_match.group(1).strip()) == "jobs":
                        in_jobs_block = True
                        jobs_indent = current_line_indent
                continue

            # Sortie de la section jobs lors d'une nouvelle clé top-level
            if jobs_indent is not None and current_line_indent <= jobs_indent:
                in_jobs_block = False
                current_job = None
                continue

            # Détection d'un en-tête de job avec gestion des commentaires inline
            header_match = re.match(r"^(\s+)([^:]+):\s*(?:#.*)?$", stripped_code)
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
                    r"^\s*(?:timeout-minutes|\"timeout-minutes\"|'timeout-minutes'):\s*(\d+|\$\{\{.+?\}\})(?:\s*#.*)?\s*$",
                    line,
                ):
                    has_timeout = True

                runs_on_match = re.match(r"^\s*(?:runs-on|\"runs-on\"|'runs-on'):\s*(.*)$", line)
                if runs_on_match:
                    inline_val = runs_on_match.group(1).strip()
                    if inline_val and not inline_val.startswith("#"):
                        has_runs_on = True
                    else:
                        # Forme imbriquée sous runs-on: séquence indentée OU séquence sans indentation (même niveau que runs-on) OU mapping
                        for _next_idx, next_line in lines[i + 1 :]:
                            next_indent = len(next_line) - len(next_line.lstrip(" "))
                            next_stripped = strip_yaml_comment(next_line).strip()
                            if not next_stripped:
                                continue
                            # Si séquence sans indentation supplémentaire ou valeur indentée (séquence/mapping)
                            if (
                                next_indent == direct_prop_indent and next_stripped.startswith("-")
                            ) or next_indent > direct_prop_indent:
                                has_runs_on = True
                                break
                            else:
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
