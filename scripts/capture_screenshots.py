#!/usr/bin/env python3
"""
scripts/capture_screenshots.py

Automatise la capture d'écran des différentes pages du Dashboard Streamlit
à l'aide de Playwright pour la documentation et le README.md.

Prérequis :
- Stack Docker démarrée (dashboard accessible sur http://localhost:8501)
- Données initialisées (grc load + scans SARIF ingérés)
- Playwright installé : `pip install playwright && playwright install chromium`
"""

import sys
import time
import urllib.request
from pathlib import Path

# Fix Windows console encoding for Unicode/emojis
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

DASHBOARD_URL = "http://localhost:8501"
VIEWPORT_WIDTH = 1440
VIEWPORT_HEIGHT = 900
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"

# Pages à capturer : (Libellé dans le menu Streamlit, Nom du fichier image)
PAGES_TO_CAPTURE = [
    ("Vue d'ensemble", "overview.png"),
    ("Heatmap des Risques", "heatmap.png"),
    ("SoA (ISO 27001)", "soa_matrix_preview.png"),
    ("Conformité Globale", "compliance.png"),
]


def check_dashboard_health(url: str, timeout: int = 5) -> bool:
    """Vérifie si le dashboard Streamlit répond correctement."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.getcode() == 200
    except Exception:
        return False


def wait_for_streamlit_ready(page, timeout_ms: int = 15000):
    """Attend que Streamlit ait terminé son exécution et rendu les composants."""
    # Attente que l'indicateur d'exécution Streamlit disparaisse
    try:
        page.wait_for_selector('[data-testid="stStatusWidget"]', state="detached", timeout=timeout_ms)
    except PlaywrightTimeoutError:
        pass
    # Petite temporisation de stabilisation pour les graphiques et CSS
    time.sleep(2.0)


def main():
    print(f"🔍 Vérification de la disponibilité du Dashboard sur {DASHBOARD_URL}...")
    if not check_dashboard_health(DASHBOARD_URL):
        print(
            f"\n❌ ERREUR : Le dashboard Streamlit ne répond pas sur {DASHBOARD_URL}.\n"
            "Veuillez démarrer la stack au préalable :\n"
            "  1. docker-compose up -d\n"
            "  2. docker-compose exec api python -m app.cli load\n"
            "  3. docker-compose exec api python -m app.cli ingest --source sarif --file grc/scans/projet1_trivy.sarif\n"
            "  4. docker-compose exec api python -m app.cli ingest --source sarif --file grc/scans/projet3_ad_audit.sarif\n",
            file=sys.stderr,
        )
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Dossier de destination : {OUTPUT_DIR}")

    with sync_playwright() as p:
        print("🚀 Lancement du navigateur Chromium (headless, 1440x900)...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT})
        page = context.new_page()

        print(f"🌐 Navigation vers {DASHBOARD_URL}...")
        page.goto(DASHBOARD_URL, wait_until="networkidle")
        wait_for_streamlit_ready(page)

        for menu_label, filename in PAGES_TO_CAPTURE:
            print(f"📸 Capture de la page '{menu_label}' -> {filename}...")

            # Clic sur l'option radio correspondante dans la barre latérale
            nav_option = page.locator('div[data-testid="stRadio"] label', has_text=menu_label)
            if nav_option.count() > 0:
                nav_option.first.click()
            else:
                # Fallback par texte exact dans la sidebar
                page.locator(f'text="{menu_label}"').first.click()

            wait_for_streamlit_ready(page)

            out_path = OUTPUT_DIR / filename
            page.screenshot(path=str(out_path), full_page=False)
            print(f"   ✅ Enregistré : {out_path} ({out_path.stat().st_size} octets)")

        browser.close()

    print("\n🎉 Toutes les captures ont été générées avec succès dans docs/images/ !")


if __name__ == "__main__":
    main()
