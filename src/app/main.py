# src/app/main.py
from src.core.wmts_client import get_wmts_capabilities
from src.core.visualize import display_wmts_layer
from src.app.config import WMTS_URL, COPERNICUS_USERNAME, COPERNICUS_PASSWORD


def main():
    wmts = get_wmts_capabilities()
    # Exemple : première couche trouvée
    layer_name = list(wmts.contents.keys())[0]
    print(f"\n🛰️ Visualisation de la couche : {layer_name}")

    display_wmts_layer(WMTS_URL, layer_name,
                       COPERNICUS_USERNAME, COPERNICUS_PASSWORD)


if __name__ == "__main__":
    main()
