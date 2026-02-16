# Veille Technologique : CI/CD

## Mission n°1 :  Comprendre CI/CD

### Qu'est-ce que la CI (Continuous Integration) ?  
    c'est une pratique des rajouts des bouts de code dans le code principale; petit à petit pour rendre la fusion plus fluide et rapide 

### Quels problèmes résout-elle ? 
    CI aide a faciliter la gestion des conflits lors de la fusion des codes des dév diff.
### Quels sont les principes clés ?
    les tests automatisés à chaque commit du code qui est, à son tour, à mettre en place à chaque changement sans accumuler les mises à jour du code
### Donnez 3 exemples d'outils de CI
    Jenkins, GitLab CI/CD, GitHub Actions (part of a dev workflow)
### Qu'est-ce que le CD (Continuous Deployment/Delivery) ? Différence entre Continuous Delivery et Continuous Deployment ?
    la Distribution contunue c'est la publication automatisée du code validé par les tests. 
    le Deployment continu c'est la suite de la Distribution et la fin de la chaîne CI/CD quand les UPD du code sont non seulement intégrés dans le "tronc commun" de l'appli, mais disponibles pour les utilisateurs. 

### Quels sont les risques et bénéfices ?
    le risque est faire passer le code non fonctionnel qui pourrait immobiliser l'application. l'avantag est que les tests automatique aident à ne pas avoir ce genre des pb
### Pourquoi CI/CD est important ?
    ça assure l'integration des bouts de code sans conflits (qui sont trop gros et prenant du temps à rersoudre) pour avoir l'appli non seulement fonctionnel, mais à jour pour les utilisateurs

### Impact sur la qualité du code : 
    moins d'erreurs manquées, le code plus propre et correct
### Impact sur la vitesse de développement : 
    permets de baisser le temps de deployment sans baisser la qualité du code 
### Impact sur la collaboration en équipe : 
    si bien géré, la création et la mise en place de l'appli se passe de manière regulière, stable et prévisible 

## Mission n°2 : Maîtriser uv
### Qu'est-ce que uv ?
    UV est un manager des dependences et des environements (pip install ..)

### En quoi est-ce différent de pip/poetry/pipenv ?
    plus rapide en application 
### Quels sont les avantages ?
    rapide, facile à mettre en place, compatible avec pip, n'a qu'un seul lockfile
### Comment uv fonctionne avec pyproject.toml ?
    c'est ici où les metadonnées du projet sont stockées, c'est aussi ic qu'on liste des dependances


### Structure du fichier
```toml
    [project]
    name = "hello-world"
    version = "0.1.0"
    description = "Add your description here"
    readme = "README.md"
    dependencies = []
```
### Gestion des dépendances (séparé par sections)
    on peut lister les dependances dans requirement.txt et les rajouter avec // uv add -r requirements.txt -c constraints.txt //
### Build backend
    on utilise uv build pour créer une source de distribution, et ensuite le wheel (la distribution binaire) depuis cette source 
### Comment utiliser uv dans GitHub Actions ? Installation
    lors de lancement d'une Action sur Git, on a quelques documents générés automatiquement, donc actions.yml ou nous pouvons mentionner l'installation de l'UV (en précisant la vérsion, c'est encore mieux): 
```yaml
    example.yml

name: example.yml

jobs:
  uv-example:
    name: python
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v6

      - name: Install uv
        uses: astral-sh/setup-uv@v7
        with:
          # Install a specific version of uv.
          version: "0.9.30"
```

### Cache des dépendances
    dans .yml doc (le nom est à choisir selon notre besoin ), peut être géré manuellement : 
```yaml
    jobs:
  install_job:
    env:
      # Configure a constant location for the uv cache
      UV_CACHE_DIR: /tmp/.uv-cache

    steps:
      # ... setup up Python and uv ...

      - name: Restore uv cache
        uses: actions/cache@v5
        with:
          path: /tmp/.uv-cache
          key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
          restore-keys: |
            uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
            uv-${{ runner.os }}

      # ... install packages, run tests, etc ...

      - name: Minimize uv cache
        run: uv cache prune --ci

        ou bien automatiqument, via astral-sh/setup-uv : 
            - name: Enable caching
            uses: astral-sh/setup-uv@v7
             with:
                enable-cache: true
```

### Exécution de commandes
    uv run (cela vérifie les maj de l'environement avant d'executer une commande)

## Mission 3 : Comprendre Semantic Release 
### Qu'est-ce que le versionnage sémantique (SemVer) ?
    le système de nommage des mises à jour (Y pour les modifs mineures et Z pour les version correctives) du code ou bien pour le lancement de l'appli (X) tout court.

### Format MAJOR.MINOR.PATCH. Quand bumper chaque niveau ?
    **MAJOR** : quand le nouveau code n'est pas compatible avec l'ancien, breaking change. On commit avec un footer BREAKING CHANGE ou bien le "!" dans la tête du commit. 
    **MINOR** : quand les MAJ du code sont encore compatibles avec le code existant. Souvent, il s'agit des features (feat:). 
    **PATCH** : une correction des bugs dans le code principal. On commit avec fix:, perf:, docs:
    De base, chaque modification est à rajouter au plus tôt, mais après avoir passé des tests. 

### Qu'est-ce que Conventional Commits ? 
    la convention sur la façon d'écrire des messages des commits 
### Format des messages
```
    <type>[étendue optionnelle]: <description>

    [corps optionnel]
    [pied optionnel]
```

### Types de commits (feat, fix, etc.)
    **feat** : l'intro d'une nouvelle fonctionnalité dans le code (correction type Y, mineure)
    **fix** : l'intro des corections des bugs dans le code
    **BREAKING CHANGE** (se trouve dans le pied du commit) : indique le changement majeur dans la compatibilité des APIs
### Impact sur le versionnage
    semantic release permets de rendre immediatement visible les modifications apportées dans le code, car chaque MAJ a sa place dans la version du code (1.2.3)
### Comment python-semantic-release fonctionne ?
    python-semantic-release maintient les vesrions du code à jour automatiquement, après chaque merge des commits (ça reste à faire selon le SR à ma main). chaque type de commite déclenche une version mise à jour, p.e. :
            **un fix**: déclenche une version patch (ex : 1.0.1)
            **un feat**: déclenche une version mineure (ex : 1.1.0)
            **un !** ou **un BREAKING CHANGE** déclenche une version majeure (ex : 2.0.0)


### Configuration dans pyproject.toml
```toml
    [tool.semantic_release]
    commit_parser = "conventional" 
    version_toml = ["pyproject.toml:project.version"]
    allow_zero_version = true // production des versions du zéro (0.1.0 au lieu de 1.0.0.)

    [tool.semantic_release.changelog.default_templates]
    changelog_file = "CHANGELOG.md" // les paramètres par default 
```

### Génération du CHANGELOG
    pour commencer, on peut utiliser le changelog_file configuré automatiquent avec 
    `[tool.semantic_release.changelog]`
    il reste néanmoins modifiable pour mieux s'alligner au projet 
### Création des releases GitHub
    tout commence par le personal acces token, qu'on peut garder dans les Secrets  dans les GitHub Actions. 
    la mécanique des releases : 
        dans les Actions, créer `.github/workflows/release.yml` avec :
```yaml
            name: Semantic Release

            on:
            push:
                btanches:
                - main

            jobs:
                release:
                    runs-on: ubuntu-latest

                    permissions:
                    contents: write
                    issues: write # optionnel
                    pull-request: write # optionnel 

                    steps:
                    - name: Checkout Code
                        uses: actions/checkout@v4
                        with: 
                            fetch-depth: 0 # on récup toute l'histprique du Git 
                            token: ${{ secrets.GH_TOKEN }}

                            - name: Install semantic-release
                                run: pip install python-semantic-release

                    - name: Configure Git
                        run: |
                            git config user.name "github-actions[bot]"
                            git config user.email "github-actions[bot]@users.noreply.github.com"

                     - name: Python Semantic Release
                        env:
                            GH_TOKEN: ${{ secrets.GH_TOKEN }}
                        run: semantic-release version # ici on met à jour le pyproject.toml et CHANGELOG.md + on crée un tag git (v1.2.4) + on crée un github release avec le CHANGELOG.md
```
