# src/web/main_panel.py
"""
Application principale Copernicus WMTS Viewer - Version Panel pure
"""

import panel as pn
from src.web.app_panel import final_app as app
import threading
from src.core.tile_server import run_tile_server


def start_tile_server():
    """Démarre le serveur de tuiles en arrière-plan"""
    try:
        run_tile_server()
    except Exception as e:
        print(f"❌ Serveur de tuiles: {e}")


"""
if __name__ == "__main__":
    print("🌊 Copernicus WMTS Viewer - Démarrage...")

    # Démarrer le serveur de tuiles dans un thread séparé
    tile_thread = threading.Thread(target=start_tile_server, daemon=True)
    tile_thread.start()

    # Lancer l'application Panel
    print("🌐 Lancement de l'interface Panel...")
    print("📱 L'application sera disponible sur http://localhost:5006")

    # CORRECTION : Utiliser soit 'show' soit 'port', pas les deux ensemble
    # Option 1: Avec ouverture automatique du navigateur
    app.show(port=5006)

    # Option 2: Sans ouverture automatique
    # app.show(port=5006, show=False)
"""


def main():
    """Fonction principale pour lancer l'application"""
    print("🌊 Copernicus WMTS Viewer - Démarrage...")

    # Démarrer le serveur de tuiles dans un thread séparé
    tile_thread = threading.Thread(target=start_tile_server, daemon=True)
    tile_thread.start()

    # Lancer l'application Panel
    print("🌐 Lancement de l'interface Panel...")
    print("📱 L'application sera disponible sur http://localhost:5006")

    # Lancer l'application Panel
    app.show(port=5006)


if __name__ == "__main__":
    main()
