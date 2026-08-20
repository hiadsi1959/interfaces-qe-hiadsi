# S. HIADSI — Quantum ESPRESSO interfaces website

Public website to present and download the **six Quantum ESPRESSO interfaces**
(including **QE–ALAMODE** for anharmonic phonons and κ<sub>L</sub>).

## Usage rules

| Allowed | Not allowed without collaboration |
|----------|-----------------------------------|
| Download, install, use | Modify the source code |
| Research & teaching | Redistribute a modified version |
| Cite S. HIADSI / LMESM | Remove author credits |

Details: [`TERMS_OF_USE.md`](TERMS_OF_USE.md)

## Preview locally (open access)

```bash
cd /home/hiadsi/site_web_hiadsi
chmod +x DEMARRER-SITE.sh
./DEMARRER-SITE.sh
```

Open **http://127.0.0.1:8090/**

## Contents

| Interface | Archive |
|-----------|---------|
| Interface-QE v1 | `telechargements/Interface-QE_v1.tar.gz` |
| QE Input Generator | `telechargements/generation_inputs-QE.tar.gz` |
| Pseudopotential Generator | `telechargements/generation_pseudos.tar.gz` |
| Supra-QE | `telechargements/supra-QE.tar.gz` |
| THERMO_PW v:20/08/2026 | `telechargements/thermo_pw_20260820.tar.gz` (~916 Ko, sans résultats de calcul) |
| QE–ALAMODE | `telechargements/QE-Alamode_interface.tar.gz` |

The `.tar.gz` files in `telechargements/` are **links** to `5-Interfaces-hiadsi`.

## Publish for everyone

### Option A — GitHub Pages (recommended, free)

Target account: [hiadsi1959](https://github.com/hiadsi1959)  
Repository: `interfaces-qe-hiadsi`  
Public URL: `https://hiadsi1959.github.io/interfaces-qe-hiadsi/`

1. Archives `.tar.gz` must be **copied** (not only linked) into `telechargements/`
2. Push the site to GitHub (`main` branch)
3. Enable **Settings → Pages** (`main` branch, `/` folder)

### Option B — Netlify / Vercel

Drag and drop the folder (with archives copied).

## Important

These interfaces **run calculations on the researcher’s PC** (with QE installed).
This site does not run calculations online.

## Download tracking (private)

Public download statistics were removed from the main page.

- **Private counters page**: [compteurs.html](compteurs.html)  
  Default access code: `hiadsi1959` (change via `statsAccessHash` in `js/config.js`).
- Counters still increment silently via [CountAPI](https://countapi.mileshilliard.com/).
- Adjust historical baselines in `js/config.js` → `baselineCounts`.
- **Who downloads**: required form (name + institution) before download.
- **E-mail (optional)**: set `notificationEmail` in `js/config.js` to receive a FormSubmit message for each download (includes the total).
- Locally (`./DEMARRER-SITE.sh`): log in `telechargements.jsonl` via `./LIRE-TELECHARGEMENTS.sh`.
