#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script complet et automatisé de validation de pseudopotentiels (.UPF) pour Quantum ESPRESSO.

Objectif : test à deux niveaux
  - Niveau 1 : stabilité numérique SCF (pw.x) sur atome isolé
  - Niveau 2 : analyse des dérivées logarithmiques / ghost states par générateur
        ONCVPSP   -> .out de génération (généralement à côté du .UPF ou dans
                    ONCVPSP_OUT_ROOT)
        ld1       -> ld1.x (iswitch=2) sur les UPFs DAL CORSO / atomic
        ape       -> ape_run.log (section Ghost state analysis)
        atompaw   -> atompaw_run.log (+ logderiv.*)
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration des outils par générateur
# ---------------------------------------------------------------------------
_PW_X = os.environ.get("PW_BIN", "pw.x")
# Nom du fichier journal que le générateur a produit (recherché dans le
# répertoire de travail).
_LD1_LOG = "ld1_run.log"
_ATOMPAW_LOG = "atompaw_run.log"
_LOGDERIV_GLOB = "logderiv.*"
_LD1_X = os.environ.get("LD1_BIN", "ld1.x")
_LD1_LOG = "ld1_run.log"
_GHOST_PATTERN = re.compile(r"GHOST", re.I)

# Valeurs de base pour le calcul SCF niveau 1.
_DEFAULT_PW_TIMEOUT = float(os.environ.get("PSEUDO_TEST_TIMEOUT", "600"))

# Paramètres par défaut du calcul SCF.
_PW_DEFAULTS = {
    "ecutwfc": 200.0,        # ecutwfc pour un atome isolé
    "ecutrho": 800.0,        # ecutrho
    "mixing_beta": 0.3,
    "electron_maxstep": 150,
    "conv_thr": 1.0e-5,
    "celldm": 25.0,          # bohr pour atome isolé
}

# Détection du générateur à partir du header UPF.
_GENERATOR_RE = {
    "oncvpsp": re.compile(r"ONCVPSP|OPTIMIZED\s*NORM-CONSERVING", re.I),
    "ld1": re.compile(r"DAL\s*CORSO|GENERATED\s+USING\s+\"ATOMIC\"|ATOMIC\s+PSEUDOPOTENTIAL\s+ENGINE", re.I),
    "ape": re.compile(r"ATOMIC\s+PSEUDOPOTENTIAL\s+ENGINE|APE", re.I),
    "atompaw": re.compile(r"ATOMPAW|PseudoDojo", re.I),
}


def _ensure_work_dir(work_dir):
    """Crée un répertoire de travail accessible en écriture (repli /tmp si besoin)."""
    path = Path(work_dir)
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_probe"
        probe.write_text("ok")
        probe.unlink()
        return path
    except OSError:
        return Path(tempfile.mkdtemp(prefix="pseudo_test_"))


def _read_output(path):
    """Lit un fichier de sortie et retourne (contenu, ok)."""
    p = Path(path)
    if not p.is_file():
        return None, False
    try:
        return p.read_text(errors="ignore"), True
    except OSError:
        return None, False


def _write_output(path, content):
    """Écrit un fichier de sortie (données brutes)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# Détection du générateur
# ---------------------------------------------------------------------------


def _attr(text, name, default=None):
    """Recherche d'une attribut dans un texte."""
    import re
    m = re.search(rf"\\b{name}=\"([^\\"]*)\"", text, flags=re.I)
    return m.group(1).strip() if m else defaultnérateur d'origine d'un pseudo UPF."""
    u = text.upper()
    if "ONCVPSP" in u or "N-C" in u:
        return "oncvpsp"
    if "ATOMPAW" in u:
        return "atompaw"
    if "ATOMIC PSEUDOPOTENTIAL ENGINE" in u or ("APE" in u and "PSEUDOPOTENTIAL" in u):
        return "ape"
    if "DAL CORSO" in u or "GENERATED USING \"ATOMIC\"" in u:
        return "ld1"
    return "other"
def parse_upf_meta(upf_path):
    """Extrait les m'etadonn'ees principales du fichier UPF."""
    upf_path = Path(upf_path)
    text = upf_path.read_text(errors="ignore")
    gen = detect_generator(text)
    element = _attr(text, "element") or extract_element_name(upf_path.name)
    z_valence = None
    zv = _attr(text, "z_valence")
    if zv:
        try:
            z_valence = float(zv.replace("D", "E").replace("d", "e"))
        except ValueError:
            pass
    # If generator is None, try to infer from path/filename
    if gen is None:
        gen = infer_generator_from_path(upf_path)
    # Detect pseudo type from UPF header
    text_upper = text.upper()
    if "PAW" in text_upper and ("ATOMIC_PSEUDOPOTENTIAL" in text_upper or "paw" in text_upper):
        pseudo_type = "PAW"
    elif "US" in text_upper or "ULTRASOFT" in text_upper:
        pseudo_type = "US"
    elif "NC" in text_upper or "NORM-CONSERVING" in text_upper:
        pseudo_type = "NC"
    else:
        pseudo_type = "NC"  # default
    
    return {
        "element": element.strip(),
        "generator": gen,
        "dft": (_attr(text, "functional") or "PBE").upper(),
        "z_valence": z_valence,
        "pseudo_type": pseudo_type,
        "l_max": 2,
        "rel": 1,
    }

