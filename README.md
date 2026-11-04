# Test Pseudos

Interface web (autonome) pour valider **tous** les pseudopotentiels UPF (Quantum ESPRESSO), quelle que soit leur source :

- pseudos **générés par les 4 générateurs** : `ld1`, `APE`, `ATOMPAW`, `ONCVPSP` — accessibles via les bibliothèques générateur de l'interface ;
- pseudos **téléchargés des bases de données et sites** (SSSP, PseudoDojo, SG15, GBRV, QE-loc pseudopotentials…) — importés via « Déposer le pseudo à testé » ou copiés dans `pseudos/` ;
- vos pseudos **locaux**.

Le générateur d'origine est détecté automatiquement dans le UPF. Chaîne de test appliquée à chaque pseudo, pilotée par **5 cases à cocher** dans l'onglet test_pseudos :

**1 · Niveau 1** `pw.x` SCF (stabilité numérique, coché par défaut) → **2 · Niveau 2** dérivées logarithmiques & ghosts (`ld1.x` iswitch=2, journaux ONCVPSP `.out` / APE `ape_run.log` / ATOMPAW, coché par défaut) → **3 · Niveau 3 (optionnel)** EOS sur cristal de référence, fit Birch-Murnaghan, comparaison `a0` / `B0` à l'expérimental (décoché par défaut) → **4 · Niveau 4 (optionnel)** delta-test qualité projecteurs, jauge ΔE à ecutrho fixé + audit des projecteurs (décoché par défaut) → **5 · corrections automatiques** en cas d'échec (coché par défaut) → les pseudos validés sont archivés dans `pseudos_testés_validés/` (onglet 📂, téléchargeables vers un disque quelconque).

## Guide d'utilisation

### 1. Démarrage

```bash
cd /home/hiadsi/test_pseudos
./DEMARRER.sh
```

Ouvre **http://127.0.0.1:5040/**
Arrêt :
```bash
./ARRETER.sh
```

### 2. Validation d'un pseudopotentiel (UPF)

1. Clique sur **⟳ Purger / Rafraîchir** pour vider les résultats et les fichiers de travail.
2. Dans l'onglet **test_pseudos**, importe les pseudos à tester : bibliothèque générateur (Local, ONCVPSP, ld1, ATOMPAW, APE), pseudos téléchargés des bases de données via **Déposer le pseudo à testé**, ou fichiers `*.UPF` placés dans `pseudos/`.
3. Sélectionne les fichiers à tester (ou clique sur **Tester tout le dossier**).
4. Lance la chaîne complète : **Niveau 1** (pw.x SCF) + **Niveau 2** (logders / ghosts) + **corrections automatiques** en cas d'échec. Deux cases optionnelles s'ajoutent : **Niveau 3 — EOS sur cristal** (test consultatif de transferabilité : équation d'état Birch-Murnaghan sur la structure de référence de l'élément, comparaison de `a0` et `B0` aux valeurs expérimentales) et **Niveau 4 — Delta-test qualité projecteurs** (jauge ΔE : écart d'énergie meV/atome à ecutrho fixé, audit des projecteurs `PP_BETA` du UPF).
5. À la fin, les pseudos validés peuvent être archivés (**📦 Archiver les validés**) puis consultés/téléchargés dans l'onglet **📂 pseudos_testés_validés**.

### 3. Options du test

| Option | Effet |
|---|---|
| **Inclure le niveau 2 (logders / ghosts)** — cochée par défaut ; le niveau 1 (pw.x SCF) est toujours exécuté | Active l'analyse des dérivées logarithmiques et détection des états fantômes (ghosts) via `ld1.x` (iswitch=2) pour les UPF *atomic* / `ld1`, ou lecture du journal du générateur pour ONCVPSP (`.out`), APE (`ape_run.log`), ATOMPAW (`atompaw_run.log` + `logderiv.*`). |
| **Corrections automatiques (5)** — cochée par défaut | Quand le niveau 1 échoue, l'outil cherche (jusqu'à `PSEUDO_TEST_AUTOCORRECT_MAX` essais) les paramètres QE qui rendent le pseudo utilisable : mélange ralenti + smearing élargi → cutoffs ×1,5 → boîte élargie. |
| **Niveau 3 — EOS sur cristal (optionnel, lent)** — décochée par défaut | Pour l'élément du pseudo : 6 points SCF (`pw.x`, `ibrav` 2/3 ou fin de diamant) sur `a0` expérimental ±4,5 %, ajustement Birch-Murnaghan 3e ordre (B0' fixé à 4), comparaison `a0` et `B0` à l'expérimental (seuils 3 % / 20 %). Consultatif : n'influe ni sur le verdict ni sur l'archivage. Éléments couverts : Si, Ge, C, Sn, Al, Cu, Ag, Au, Pb, Pt, W, Mo, Ta, V, Li, Na, K (table `engine/crystal_tests.CRYSTALS`). |
| **Niveau 4 — Delta-test qualité projecteurs (optionnel)** — décochée par défaut | Jauge delta : deux SCF `pw.x` de l'atome isolé, le 1er à `ecutwfc`/`ecutrho` retenus, le 2e à `ecutwfc` × 1,4 avec le **même `ecutrho`** ; écart **ΔE (meV/atome)**, seuils 0,5 / 3 meV/atome (SUCCESS / WARNING / FAILED). Publiquement : le Delta-test officiel SSSP/PseudoDojo compare à des références tout-électron (WIEN2k) non embarquées — ici la jauge quantifie la convergence de jauge interne à ecutrho fixé, le complément physique étant assuré par le Niveau 3 (EOS). S'ajoute l'audit des projecteurs : bloc `PP_BETA` réel vs `number_of_proj` du header, canaux s/p/d/f, énergies d'émission positives (candidats ghost). Consultatif : n'influe ni sur le verdict ni sur l'archivage. |

### 4. Résultats du test

Chaque résultat affiche :
- **Format UPF** : version, blocs requis, type NC/US/PAW, projecteurs, cohérence XC et empreinte SHA-256.
- **Niveau 1 · pw.x SCF** : convergence, énergie totale, durée, corrections appliquées en cas d'échec.
  Le SCF tourne avec la fonctionnelle du pseudo (`input_dft` déduit du UPF, omis si non reconnue).
- **Niveau 2 · ld1 / logders / ghosts** : analyse des dérivées logarithmiques et détection des états fantômes (ghosts).
- **Niveau 3 · EOS cristal** : a0 équivalent, B0 (GPa), résidu max du fit (meV/atome) et écarts % à l'expérimental.
- **Niveau 4 · Delta-test** : jauge ΔE (meV/atome, ecutwfc vs réf. ×1,4 à même ecutrho), seuils appliqués et audit des projecteurs (PP_BETA vs header, canaux, énergies positives).
- **Corrections automatiques (5)** : tentatives de régénération des paramètres QE (mixing, cutoffs, cell) et résultats.
- **Ghosts** : états fantômes détectés et leur statut, avec le canal concerné (`l=0`, `l=2`, `l=3`, etc.).
- **Pseudo corrigé (sans ghost) prêt pour QE** : avec les nouveaux paramètres et les livrables (`scf_atome_isole.in`, `oncvpsp_corrige.dat`).

### 5. Suppression d'un pseudo

Si le niveau 2 détecte des **ghosts** et que le pseudo est corrigé, le résultat affiche :
- **Ghosts · ÉLIMINÉS** : les états fantômes ont été corrigés (canal `l`, facteur de `rc` appliqué).
- **Pseudo corrigé (sans ghost) prêt pour QE** : le pseudo régénéré est sauvegardé dans `ready/` :
  ```
  ready/<pseudo>_sans_ghost/
    <pseudo>.UPF          # pseudo corrigé
    scf_atome_isole.in    # input pw.x validé
    oncvpsp_corrige.dat   # fichier de correction (ONCVPSP)
  ```

L'identité du correcteur est : **Auteur : Said Hiadsi** — `said.hiadsi@univ-usto.dz` (cliqué pour contacter).

### 6. Variables d'environnement

| Variable | Défaut | Rôle |
|---|---|---|
| `PW_BIN` / `LD1_BIN` | `./bin/pw.x`, `./bin/ld1.x` (fallback QE) | Binaires embarqués dans le dossier `bin/` du projet — **l'interface est autonome** ; sinon fallback sur `$QE_BIN_DIR` |
| `ONCVPSP_BIN` | `./bin/oncvpsp.x` | Binaire ONCVPSP pour l'élimination des ghosts |
| `ATOMPAW_BIN` | `./bin/atompaw` | Binaire ATOMPAW pour le niveau 2 natif |
| `QE_BIN_DIR` | `$HOME/q-e-qe-7.5/bin` | Binaires QE de secours si `bin/` est incomplet |
| `ONCVPSP_OUT_ROOT` | `$HOME/generation_pseudos/pseudos-oncvpsp` | Racine de recherche des journaux ONCVPSP (`.out`) |
| `PSEUDOS_DIR` | `./pseudos` | Dossier local de pseudopotentiels `.UPF` |
| `TEST_PSEUDOS_PORT` | `5040` | Port d'écoute du serveur API |
| `PSEUDO_TEST_TIMEOUT` | non défini : `420` s (NC) · `600` s (US/PAW) | Borne `pw.x` (tout l'onglet) |
| `PSEUDO_TEST_ECUTWFC` | `60` Ry | Cutoff d'onde du test atome isolé |
| `PSEUDO_TEST_CELL` | `16` bohr | Arête de la boîte cubique du test |
| `PSEUDO_TEST_AUTOCORRECT` | `1` | Désactive la correction automatique si `0` |
| `PSEUDO_TEST_AUTOCORRECT_MAX` | `3` | Nombre max de tentatives de correction |
| `PSEUDO_TEST_GHOST_FIX_MAX` | `4` | Nombre max d'essais de suppression de ghosts ONCVPSP |
| `PSEUDO_TEST_DELTA_WARN` | `0,5` meV/atome | Niveau 4 · delta-test : au-dessus de ce ΔE → WARNING (décimales acceptées aussi avec une virgule) |
| `PSEUDO_TEST_DELTA_FAIL` | `3` meV/atome | Niveau 4 · delta-test : au-dessus de ce ΔE → FAILED ; doit rester > `PSEUDO_TEST_DELTA_WARN` sinons défauts conservés |
| `PSEUDO_READY_DIR` | `./ready` | Dossier où sont écrits les pseudos corrigés |

## Démarrage du serveur

```bash
cd /home/hiadsi/test_pseudos
./DEMARRER.sh
```

Ouvre **http://127.0.0.1:5040/**
Arrêt :
```bash
./ARRETER.sh
```

## Structure du projet

```
test_pseudos/
  bin/                     # binaires embarqués : pw.x, ld1.x, oncvpsp.x, atompaw, ape
  engine/test_pseudos.py   # moteur de validation (4 niveaux + corrections)
  engine/crystal_tests.py  # niveau 3 : EOS Birch-Murnaghan sur cristal de référence
                           # niveau 4 : delta-test qualité projecteurs (jauge ΔE)
  engine/ghost_fix.py      # suppression des ghosts ONCVPSP
  engine/ld1_ghost.py      # test de ghost par ld1.x
  engine/gen_ghost.py      # test de ghost générique
  backend/server.py        # API Flask (sans état persistant)
  interface/               # UI : 4 onglets (Accueil · test_pseudos · 📂 pseudos_testés_validés · Guide)
  interface/index.compact.html  # Interface compactée nouvelle - 04-11-2026
  interface/index.inline.html   # Interface inline compactée nouvelle
  docs/                    # guide PDF
  pseudos/                 # UPF à tester (local)
  uploads/                 # UPF déposés via « Déposer le pseudo à testé »
  ready/                   # pseudos corrigés (livrables)
  pseudos_testés_validés/  # archive des pseudos validés (onglet 📂, téléchargement)
```

## Guide methodologique (PDF)

Le contenu du guide (`docs/Guide_Methodologique_Validation_Pseudopotentiels.pdf`)
est intégré à la page d'accueil. Le PDF est aussi servi en `/api/guide.pdf`.

## Correction automatique

Quand le SCF du niveau 1 échoue, le moteur cherche **la cause** puis relance le
calcul avec des paramètres corrigés (mélange ralenti + smearing élargi → cutoffs
×1,5 → boîte élargie), dans une limite de `PSEUDO_TEST_AUTOCORRECT_MAX` essais.
Si une tentative converge, ses paramètres sont renvoyés et un dossier prêt à
l'emploi est écrit dans `ready/` :

```
ready/<pseudo>/
  <pseudo>.UPF          # le pseudo
  scf_atome_isole.in    # input pw.x validé, lancement direct
```

> Le moteur ne réécrit pas le UPF d'origine : il détermine et fournit les
> **paramètres QE qui rendent le pseudo utilisable**. La seule exception est
> l'élimination des ghosts ONCVPSP (ci-dessous), qui régénère un UPF.

## Élimination des ghosts (ONCVPSP)

Quand le rapport de génération signale `WARNING - GHOST(+/-)`, le moteur
régénère le pseudopotentiel :

1. il retrouve l'input de génération `oncv_<El>.dat` (à côté du `.out`) ;
2. il relève les canaux `l` en ghost ;
3. il élargit progressivement `rc` (×1,15 → ×1,75) et réduit `qcut` (×0,90)
de ces canaux — le remède standard anti-ghost ;
4. il relance `oncvpsp.x` et revérifie l'absence de ghost ;
5. il extrait le UPF corrigé et le **valide au niveau 1** avant de le proposer.

Le pseudo corrigé est livré dans `ready/<pseudo>_sans_ghost/` avec
`scf_atome_isole.in`, le UPF régénéré et l'input `oncvpsp_corrige.dat`.

Prérequis : `oncvpsp.x` accessible (`ONCVPSP_BIN`, par défaut `./bin/oncvpsp.x`, sinon
`~/.local/bin/oncvpsp.x` ou `$PATH`) et l'input `.dat` conservé à côté du `.out`. Réglages :
`ONCVPSP_TIMEOUT` (600 s), `PSEUDO_TEST_GHOST_FIX_MAX` (4 essais).

Le timeout est réellement appliqué : `pw.x` et sa descendance sont tués à
l'échéance (aucun processus fantôme, pas de blocage de l'interface).

## Interface

- **⟳ Purger / Rafraîchir** : vide résultats et fichiers de travail, puis recharge l'état. Les livrables de `ready/` sont conservés (pour les supprimer : `POST /api/purge {"what":"all","ready":true}`).
- **🗑 Purger la liste** : vide la liste de pseudos affichée en bas de page.
- **📦 Archiver les validés** : copie les pseudos testés/corrigés de `ready/` vers l'archive `pseudos_testés_validés/` sans jamais écraser un contenu différent.
- **Onglet 📂 pseudos_testés_validés** : liste l'archive (chemin, nombre, taille) et permet de **télécharger chaque UPF** (`/api/archive/file/<nom>`) vers un disque quelconque.
- **Onglet Guide** : méthodologie de production DFT au-delà de la chaîne de test (convergence E_cut, équation d'état, transferabilité, électronique/phonons).
- Le bouton d'état API (en haut à droite) est vert en ligne, rouge hors ligne, avec « ↻ Réessayer » pour retenter ; reconnexion automatique toutes les 15 s.
- Un rafraîchissement de page retrouve le dernier job et ses résultats (`GET /api/jobs`).

## CLI

```bash
python3 engine/test_pseudos.py ./pseudos pw.x ld1.x /chemin/pseudos-oncvpsp
```

