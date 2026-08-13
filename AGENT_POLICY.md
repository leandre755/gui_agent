# Politique : agent accompagné

## Objet et frontière

Cette politique est le choix par défaut pour un développeur travaillant avec un agent dans son IDE ou terminal. L’agent peut explorer le dépôt, modifier des fichiers dans le workspace et exécuter les vérifications explicitement autorisées. La personne garde la responsabilité des opérations qui modifient l’historique Git, publient du code ou changent les règles de contrôle.

## Autorisations

L’agent peut lire les sources non sensibles, créer ou modifier les fichiers applicatifs dans le workspace, appliquer formatage/lint/tests/build, inspecter `git status` et `git diff`, et produire une proposition de message Conventional Commits ainsi qu’une description de PR. Les commandes de vérification doivent être celles documentées dans le dépôt et rester dans le workspace.

## Refus obligatoires

L’agent ne doit pas exécuter `git commit`, `git push`, `git tag`, `git merge`, `git rebase`, `gh pr create`, `gh pr merge`, `npm publish`, `docker push`, les déploiements ou toute commande de modification d’accès. Il ne doit jamais utiliser une option de contournement, notamment `--no-verify`, `--force`, `--force-with-lease`, `--skip-hooks`, `git reset --hard` ou `git clean -fd`.

L’agent ne lit ni n’écrit des secrets, fichiers `.env` réels, clés, certificats, jetons, fichiers de l’hôte hors workspace, `.git/`, politiques d’agents, configurations de permissions, `CODEOWNERS`, workflows CI, hooks ou scripts d’installation. Si la tâche exige une modification de gouvernance, l’agent prépare un plan et un diff proposé, puis attend une action humaine distincte.

## Boucle de travail

1. Vérifier que le workspace est le dépôt attendu et lire `AGENTS.md` ainsi que les instructions locales applicables.
2. Confirmer le résultat demandé et le critère observable de succès. En cas d’ambiguïté matérielle, poser une question avant d’éditer.
3. Examiner les fichiers et tests pertinents, puis annoncer un plan court.
4. Apporter le changement minimal dans le workspace.
5. Exécuter les vérifications applicables et communiquer les résultats bruts utiles, les contrôles non exécutés et les risques.
6. Fournir un diff synthétique, un message de commit suggéré et une proposition de description de PR. La personne relit puis effectue elle-même commit, push et PR.

## Réponse aux incidents

Arrêter immédiatement et demander de l’aide si un secret est détecté, si une commande sort du workspace, si une permission supplémentaire est nécessaire, si une vérification critique échoue, si la tâche touche un chemin protégé ou si l’opération peut entraîner une conséquence externe. Ne pas tenter une solution de contournement.
