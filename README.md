# HIADSI — Site des interfaces Quantum ESPRESSO

Portail public pour présenter et télécharger les **5 interfaces** situées dans
`/home/hiadsi/5-Interfaces-hiadsi`.

## Règle d’usage

| Autorisé | Interdit sans collaboration |
|----------|-----------------------------|
| Télécharger, installer, utiliser | Modifier le code source |
| Recherche & enseignement | Redistribuer une version modifiée |
| Citer S. Hiadsi / LMESM | Retirer les mentions d’auteur |

Détail : [`CONDITIONS_UTILISATION.md`](CONDITIONS_UTILISATION.md)

## Prévisualiser en local (accès libre)

```bash
cd /home/hiadsi/site_web_hiadsi
chmod +x DEMARRER-SITE.sh
./DEMARRER-SITE.sh
```

Ouvrez **http://127.0.0.1:8090/**

## Contenu

| Interface | Archive |
|-----------|---------|
| Interface-QE v1 | `telechargements/Interface-QE_v1.tar.gz` |
| Génération Inputs QE | `telechargements/generation_inputs-QE.tar.gz` |
| Génération Pseudopotentiels | `telechargements/generation_pseudos.tar.gz` |
| Supra-QE | `telechargements/supra-QE.tar.gz` |
| THERMO_PW | `telechargements/thermo_pw.tar.gz` |

Les fichiers `.tar.gz` dans `telechargements/` sont des **liens** vers `5-Interfaces-hiadsi`.

## Publier pour que tout le monde y accède

### Option A — GitHub Pages (recommandé, gratuit)

Compte cible : [hiadsi1959](https://github.com/hiadsi1959)  
Dépôt prévu : `interfaces-qe-hiadsi`  
URL publique : `https://hiadsi1959.github.io/interfaces-qe-hiadsi/`

1. Les archives `.tar.gz` doivent être **copiées** (pas seulement liées) dans `telechargements/`
2. Poussez le site sur GitHub (branche `main`)
3. Activez **Settings → Pages** (branche `main`, dossier `/`)

### Option B — Netlify / Vercel

Glissez-déposez le dossier (avec les archives copiées).

## Important

Ces interfaces **calculent sur le PC du chercheur** (avec QE installé).
Ce site ne lance pas les calculs en ligne.

## Suivi des téléchargements

- **Compteurs publics** : section Stats du site (et sous chaque interface).
- **Qui télécharge** : formulaire obligatoire (nom + organisme) avant le téléchargement.
- Sur le site GitHub Pages : renseignez votre e-mail dans `js/config.js` (`notificationEmail`) pour recevoir un message à chaque téléchargement.
- En local (`./DEMARRER-SITE.sh`) : journal dans `telechargements.jsonl` via `./LIRE-TELECHARGEMENTS.sh`.
