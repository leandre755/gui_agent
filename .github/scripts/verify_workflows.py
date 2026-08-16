#!/usr/bin/env python3
"""Vérifie les invariants de sécurité des fichiers GitHub Actions du dépôt cible.

Le script ne dépend que de la bibliothèque standard afin de pouvoir être exécuté
localement et dans le workflow de maintenance. Il traite les workflows comme des
fichiers texte : son rôle est de bloquer les références manifestement dangereuses,
non de remplacer un parseur YAML complet.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
USES = re.compile(r"^\s*(?:-\s*)?uses:\s*([^@\s]+)@([^\s#]+)(?:\s+#\s*(.+))?\s*$")


def fail(message: str) -> None:
    print(f"ERROR: {message}")


def check_workflow(path: Path) -> int:
    errors = 0
    lines = path.read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines)

    if re.search(r"^\s*pull_request_target\s*:", text, flags=re.MULTILINE):
        fail(f"{path}: pull_request_target est interdit dans ce starter kit.")
        errors += 1

    if not re.search(r"^permissions:\s*(?:#.*)?$", text, flags=re.MULTILINE):
        fail(f"{path}: bloc permissions top-level manquant.")
        errors += 1

    for number, line in enumerate(lines, start=1):
        if "persist-credentials: true" in line:
            fail(f"{path}:{number}: persist-credentials: true est interdit par défaut.")
            errors += 1
        match = USES.match(line)
        if not match:
            continue
        action, ref, comment = match.groups()
        if action.startswith("./") or action.startswith("docker://"):
            continue
        if not SHA.fullmatch(ref):
            fail(f"{path}:{number}: {action}@{ref} doit être épinglée sur un SHA de 40 caractères.")
            errors += 1
        elif not comment or not comment.startswith("v"):
            print(f"WARNING: {path}:{number}: ajoutez un commentaire de version, par exemple '# v4.0.0'.")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(".github/workflows")
    if not root.is_dir():
        print(f"ERROR: répertoire introuvable : {root}")
        return 2

    workflows = sorted([*root.glob("*.yml"), *root.glob("*.yaml")])
    if not workflows:
        print(f"ERROR: aucun workflow YAML dans : {root}")
        return 2

    errors = sum(check_workflow(path) for path in workflows)
    if errors:
        print(f"Validation refusée : {errors} erreur(s) détectée(s).")
        return 1
    print(f"Validation réussie : {len(workflows)} workflow(s) conformes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
