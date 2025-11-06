# src/core/tile_server.py
import http.server
import socketserver
import os
import urllib.parse
import threading
from pathlib import Path


class TileHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Définir le répertoire de base
        self.base_directory = os.getcwd()
        super().__init__(*args, directory=self.base_directory, **kwargs)

    def translate_path(self, path):
        """Traduit le chemin pour servir correctement les fichiers."""
        path = urllib.parse.unquote(path)

        # Chemin complet demandé
        full_path = os.path.normpath(os.path.join(
            self.base_directory, path.lstrip('/')))

        # Protection contre les accès en dehors du répertoire autorisé
        if not full_path.startswith(self.base_directory):
            return super().translate_path('/404')

        # Servir les fichiers GeoJSON vectoriels
        if path.startswith('/data/vector/'):
            if os.path.exists(full_path):
                print(f"✅ Fichier vectoriel servi: {path} -> {full_path}")
                return full_path
            else:
                print(
                    f"❌ Fichier vectoriel introuvable: {path} -> {full_path}")

        # Servir les fichiers statiques
        if path.startswith('/static/'):
            if os.path.exists(full_path):
                return full_path

        # Servir les templates
        if path.startswith('/templates/'):
            if os.path.exists(full_path):
                return full_path

        # Servir les tuiles
        if '/data/map/tiles/' in path:
            if os.path.exists(full_path):
                return full_path

        return super().translate_path(path)

    def guess_type(self, path):
        """Déterminer le type MIME correctement."""
        if path.endswith('.css'):
            return 'text/css'
        elif path.endswith('.js'):
            return 'application/javascript'
        elif path.endswith('.html'):
            return 'text/html'
        elif path.endswith('.png'):
            return 'image/png'
        elif path.endswith('.kml'):
            return 'application/vnd.google-earth.kml+xml'
        elif path.endswith('.geojson'):
            return 'application/geo+json'  # Type MIME pour GeoJSON
        return super().guess_type(path)

    def log_message(self, format, *args):
        """Réduire les logs pour éviter le spam."""
        # Seulement logger les erreurs et les requêtes importantes
        if args[1] != '200' or '/tiles/' in self.path or '/data/vector/' in self.path:
            super().log_message(format, *args)

    def end_headers(self):
        """Ajouter les headers CORS pour permettre l'accès depuis Panel"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers',
                         'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        super().end_headers()

    def do_OPTIONS(self):
        """Gérer les requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self.end_headers()


def find_all_shapefile_folders():
    """Trouve tous les dossiers contenant des Shapefiles dans data/vector/"""
    base_dir = Path(__file__).parent.parent.parent
    vector_dir = base_dir / "data/vector"

    shapefile_folders = []

    if not vector_dir.exists():
        print(f"❌ Répertoire vector introuvable : {vector_dir}")
        return []

    # Parcourir tous les dossiers du répertoire vector
    for folder in vector_dir.iterdir():
        if folder.is_dir():
            # Vérifier si le dossier contient des fichiers .shp
            shp_files = list(folder.glob("*.shp"))
            if shp_files:
                # Vérifier les fichiers associés nécessaires
                associated_files = {
                    'shp': len(list(folder.glob("*.shp"))),
                    'dbf': len(list(folder.glob("*.dbf"))),
                    'shx': len(list(folder.glob("*.shx"))),
                    'prj': len(list(folder.glob("*.prj"))),
                    'cpg': len(list(folder.glob("*.cpg"))),
                }

                shapefile_folders.append({
                    'name': folder.name,
                    'path': folder,
                    'shp_files': shp_files,
                    'main_shp': shp_files[0].name if shp_files else None,
                    'associated_files': associated_files,
                    'is_complete': all(associated_files[ext] > 0 for ext in ['shp', 'dbf', 'shx'])
                })

    return shapefile_folders


def find_all_geojson_files():
    """Trouve tous les fichiers GeoJSON dans data/vector/geojson/"""
    base_dir = Path(__file__).parent.parent.parent
    geojson_dir = base_dir / "data/vector/geojson"

    geojson_files = []

    if not geojson_dir.exists():
        print(f"❌ Répertoire GeoJSON introuvable : {geojson_dir}")
        return []

    for geojson_file in geojson_dir.glob("*.geojson"):
        file_size = geojson_file.stat().st_size
        geojson_files.append({
            'name': geojson_file.name,
            'path': geojson_file,
            'size': file_size,
            'size_mb': file_size / (1024 * 1024)
        })

    return geojson_files


def check_vector_data_health():
    """Vérifie la santé de tous les données vectorielles"""
    print("\n" + "="*60)
    print("🔍 DIAGNOSTIC COMPLET DES DONNÉES VECTORIELLES")
    print("="*60)

    # Vérifier les Shapefiles
    shapefile_folders = find_all_shapefile_folders()

    print(f"\n📁 SHAPEFILES TROUVÉS ({len(shapefile_folders)} dossiers):")
    print("-" * 50)

    for folder_info in shapefile_folders:
        status = "✅ COMPLET" if folder_info['is_complete'] else "⚠️ INCOMPLET"
        print(f"\n📂 {folder_info['name']} - {status}")
        print(f"   📊 Fichier principal: {folder_info['main_shp']}")

        # Afficher les fichiers associés
        for file_type, count in folder_info['associated_files'].items():
            status_icon = "✅" if count > 0 else "❌"
            print(f"   {status_icon} .{file_type}: {count} fichier(s)")

    # Vérifier les fichiers GeoJSON
    geojson_files = find_all_geojson_files()

    print(f"\n🗺️ FICHIERS GEOJSON ({len(geojson_files)} fichiers):")
    print("-" * 50)

    for geojson_info in geojson_files:
        print(f"📄 {geojson_info['name']} - {geojson_info['size_mb']:.2f} MB")

    # Vérifier la correspondance Shapefile -> GeoJSON
    print(f"\n🔗 CORRESPONDANCE SHAPEFILE -> GEOJSON:")
    print("-" * 50)

    shapefile_names = {folder['name'] for folder in shapefile_folders}
    geojson_names = {file['name'].replace(
        '.geojson', '') for file in geojson_files}

    # Shapefiles sans GeoJSON correspondant
    missing_geojson = shapefile_names - geojson_names
    if missing_geojson:
        print("❌ Shapefiles sans GeoJSON correspondant:")
        for name in sorted(missing_geojson):
            print(f"   - {name}")
    else:
        print("✅ Tous les Shapefiles ont un GeoJSON correspondant")

    # GeoJSON sans Shapefile correspondant
    extra_geojson = geojson_names - shapefile_names
    if extra_geojson:
        print("📝 GeoJSON sans Shapefile source (peut être normal):")
        for name in sorted(extra_geojson):
            print(f"   - {name}")

    return {
        'shapefile_folders': shapefile_folders,
        'geojson_files': geojson_files,
        'missing_geojson': missing_geojson
    }


def run_tile_server(port=8000):
    """Démarre le serveur de tuiles HTTP avec gestion de port alternatif."""

    # Vérifier que les répertoires statiques existent
    static_dirs = ['static/css', 'static/js', 'templates']
    for static_dir in static_dirs:
        if not os.path.exists(static_dir):
            print(f"⚠️ Répertoire manquant: {static_dir}")

    # Diagnostic complet des données vectorielles
    vector_health = check_vector_data_health()

    # Vérifier les répertoires vectoriels de base
    vector_dirs_to_check = [
        "data/vector",
        "data/vector/geojson"
    ]

    print(f"\n📁 STRUCTURE DES RÉPERTOIRES VECTORIELS:")
    print("-" * 40)
    for vector_dir in vector_dirs_to_check:
        if os.path.exists(vector_dir):
            files = os.listdir(vector_dir)
            print(f"📁 {vector_dir} ({len(files)} éléments)")
            # Afficher les sous-dossiers et fichiers
            for item in sorted(files)[:10]:  # Limiter à 10 éléments
                item_path = os.path.join(vector_dir, item)
                if os.path.isdir(item_path):
                    print(f"   📂 {item}/")
                else:
                    print(f"   📄 {item}")
            if len(files) > 10:
                print(f"   ... et {len(files) - 10} autres éléments")
        else:
            print(f"❌ {vector_dir} - RÉPERTOIRE MANQUANT")

    # Essayer différents ports
    ports_to_try = [port, 8001, 8002, 8003]
    httpd = None

    for current_port in ports_to_try:
        try:
            print(f"\n🔄 Tentative de démarrage sur le port {current_port}...")
            httpd = socketserver.TCPServer(
                ("", current_port), TileHTTPRequestHandler)
            final_port = current_port
            break
        except OSError as e:
            if current_port == ports_to_try[-1]:  # Dernier port essayé
                print(
                    f"❌ Impossible de démarrer le serveur sur les ports {ports_to_try}")
                print(f"💡 Fermez les applications utilisant ces ports ou redémarrez")
                return None
            continue

    print(f"\n✅ Serveur de tuiles démarré sur http://localhost:{final_port}")
    print("📁 Répertoire de travail:", os.getcwd())

    # Vérifier que les tuiles existent
    tiles_paths = [
        "./data/map/tiles/EPSG3857/0/0/0.png",
        "./data/map/tiles/EPSG4326/0/0/0.png"
    ]

    print(f"\n🔍 VÉRIFICATION DES TUILES:")
    print("-" * 40)
    for path in tiles_paths:
        if os.path.exists(path):
            file_size = os.path.getsize(path) / 1024
            print(f"✅ {path} - {file_size:.1f} KB")
        else:
            print(f"⚠️ Tuiles manquantes: {path}")

    # Résumé des URLs disponibles
    print(f"\n🌐 URLs IMPORTANTES:")
    print("-" * 40)
    print(f"   🗺️  Carte: http://localhost:{final_port}/templates/index.html")
    print(f"   🎨 CSS: http://localhost:{final_port}/static/css/main.css")
    print(f"   ⚙️  JS: http://localhost:{final_port}/static/js/app.js")

    # URLs pour les GeoJSON
    print(f"\n   📊 DONNÉES VECTORIELLES GEOJSON:")
    for geojson_info in vector_health['geojson_files']:
        url_path = f"/data/vector/geojson/{geojson_info['name']}"
        print(
            f"      - {geojson_info['name']}: http://localhost:{final_port}{url_path}")

    # URLs pour les tuiles
    print(f"\n   🧩 TUILES:")
    print(
        f"      - EPSG3857: http://localhost:{final_port}/data/map/tiles/EPSG3857/{{z}}/{{x}}/{{y}}.png")
    print(
        f"      - EPSG4326: http://localhost:{final_port}/data/map/tiles/EPSG4326/{{z}}/{{x}}/{{y}}.png")

    # Recommandations
    if vector_health['missing_geojson']:
        print(f"\n💡 RECOMMANDATIONS:")
        print("-" * 40)
        print("Certains Shapefiles n'ont pas de GeoJSON correspondant.")
        print("Utilisez le convertisseur pour les générer:")
        print("   python utils/convert_shp_to_geojson.py")

    print(f"\n📊 STATUT GÉNÉRAL:")
    print("-" * 40)
    print(f"   ✅ Shapefiles: {len(vector_health['shapefile_folders'])}")
    print(f"   ✅ GeoJSON: {len(vector_health['geojson_files'])}")
    print(
        f"   ⚠️  Conversions manquantes: {len(vector_health['missing_geojson'])}")

    print("\n🎯 Prêt à servir les tuiles Natural Earth et données vectorielles...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur de tuiles")

    return final_port


if __name__ == "__main__":
    run_tile_server()
