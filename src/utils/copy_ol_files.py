# copy_ol_files.py
import shutil
import os
from pathlib import Path


def copy_ol_files():
    node_modules_path = Path("node_modules/ol")
    static_path = Path("static/js/ol")

    # Fichiers nécessaires étendus
    required_files = [
        "Map.js", "View.js",
        "layer/Tile.js", "layer/Vector.js",
        "source/TileImage.js", "source/XYZ.js", "source/OSM.js", "source/Vector.js",
        "tilegrid/TileGrid.js",
        "control/ScaleLine.js", "control/ZoomToExtent.js", "control/FullScreen.js",
        "proj.js", "extent.js",
        "format/GeoJSON.js",
        "Feature.js",
        "geom/Point.js",
        "style/Style.js", "style/Fill.js", "style/Stroke.js", "style/Text.js"
    ]

    # CSS
    css_source = node_modules_path / "ol.css"
    css_dest = Path("static/css/ol.css")

    static_path.mkdir(parents=True, exist_ok=True)
    Path("static/css").mkdir(parents=True, exist_ok=True)

    if css_source.exists():
        shutil.copy2(css_source, css_dest)
        print(f"✅ CSS copié: {css_dest}")

    for file_path in required_files:
        source_file = node_modules_path / file_path
        dest_file = static_path / file_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        if source_file.exists():
            shutil.copy2(source_file, dest_file)
            print(f"✅ Fichier copié: {file_path}")
        else:
            print(f"❌ Fichier non trouvé: {source_file}")


if __name__ == "__main__":
    copy_ol_files()
