# Politique agent accompagné

Lire `AGENTS.md` et `AGENT_POLICY.md` avant toute modification. L’agent peut modifier uniquement les fichiers applicatifs non sensibles et exécuter les contrôles documentés. Il restitue ensuite le diff, les commandes exécutées, les résultats et les risques ; la personne effectue commit, push, PR, merge et publication.

Ne jamais utiliser `git commit`, `git push`, `git tag`, `git merge`, `git rebase`, `gh pr`, `gh release`, publication, déploiement, `--no-verify`, `--force`, `--skip-hooks`, `git reset --hard`, `git clean -fd` ou `sudo`. Ne jamais accéder à `.env`, secrets, clés, `.git/`, fichiers de politique, CI, hooks ou scripts de setup.

Cette règle est de la guidance.
