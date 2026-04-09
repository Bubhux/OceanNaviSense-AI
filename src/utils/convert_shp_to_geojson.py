# utils/convert_shp_to_geojson.py
import geopandas as gpd
import json
import os
from pathlib import Path


def get_available_shapefiles():
    """Récupère tous les dossiers contenant des Shapefiles"""
    base_dir = Path(__file__).parent.parent.parent
    vector_dir = base_dir / "data/vector"

    shapefile_folders = []

    if not vector_dir.exists():
        print(f"❌ Dossier vector introuvable : {vector_dir}")
        return []

    # Parcourir tous les dossiers du répertoire vector
    for folder in vector_dir.iterdir():
        if folder.is_dir():
            # Vérifier si le dossier contient des fichiers .shp
            shp_files = list(folder.glob("*.shp"))
            if shp_files:
                shapefile_folders.append({
                    'name': folder.name,
                    'path': folder,
                    'shp_count': len(shp_files),
                    'main_shp': shp_files[0].name if shp_files else None
                })

    return shapefile_folders


def display_available_datasets(shapefile_folders):
    """Affiche la liste des datasets disponibles"""
    print("\n" + "="*60)
    print("📁 DATASETS SHAPEFILE DISPONIBLES")
    print("="*60)

    for i, folder_info in enumerate(shapefile_folders, 1):
        print(f"{i:2d}. {folder_info['name']}")
        print(f"    📊 {folder_info['shp_count']} fichier(s) .shp")
        print(f"    📁 {folder_info['main_shp']}")
        print()


def choose_dataset(shapefile_folders):
    """Permet à l'utilisateur de choisir un dataset"""
    if not shapefile_folders:
        print("❌ Aucun dataset Shapefile trouvé dans data/vector/")
        return None

    while True:
        try:
            choice = input(
                f"\n🎯 Choisissez un dataset (1-{len(shapefile_folders)}) ou 'q' pour quitter : ").strip()

            if choice.lower() == 'q':
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(shapefile_folders):
                selected_folder = shapefile_folders[choice_num - 1]
                print(f"✅ Dataset sélectionné : {selected_folder['name']}")
                return selected_folder
            else:
                print(
                    f"❌ Veuillez choisir un nombre entre 1 et {len(shapefile_folders)}")

        except ValueError:
            print("❌ Veuillez entrer un nombre valide")


def inspect_selected_dataset(folder_info):
    """Inspecte le dataset sélectionné"""
    print(f"\n🔍 INSPECTION DU DATASET: {folder_info['name']}")
    print("="*50)

    shp_files = list(folder_info['path'].glob("*.shp"))
    if not shp_files:
        print("❌ Aucun fichier .shp trouvé")
        return None

    shp_path = shp_files[0]

    try:
        gdf = gpd.read_file(shp_path)
        print(f"📁 Fichier : {shp_path.name}")
        print(f"📊 Nombre d'entités : {len(gdf)}")
        print(f"🎯 Système de coordonnées : {gdf.crs}")
        print(f"📝 Colonnes disponibles : {list(gdf.columns)}")

        # Afficher les types de géométrie
        print(f"🔶 Types de géométrie : {gdf.geometry.type.unique()}")

        # Afficher un échantillon des données
        if len(gdf) > 0:
            print(f"\n📋 Échantillon des données (2 premières entités):")
            for i in range(min(2, len(gdf))):
                print(f"\n  Entité {i}:")
                for col in gdf.columns:
                    if col != 'geometry' and gdf.iloc[i][col] is not None:
                        value = gdf.iloc[i][col]
                        # Tronquer les valeurs trop longues
                        if len(str(value)) > 50:
                            value = str(value)[:47] + "..."
                        print(f"    {col}: {value}")

        return gdf

    except Exception as e:
        print(f"❌ Erreur lors de l'inspection : {e}")
        import traceback
        traceback.print_exc()
        return None


def convert_shapefile_to_geojson(folder_info):
    """Convertit le Shapefile sélectionné en GeoJSON"""

    shp_files = list(folder_info['path'].glob("*.shp"))
    if not shp_files:
        print("❌ Aucun fichier .shp trouvé")
        return None

    shp_path = shp_files[0]

    # Créer le nom du fichier de sortie basé sur le nom du dossier
    output_filename = folder_info['name'].replace(
        'ne_10m_', '').replace('ne_50m_', '').replace('ne_110m_', '')
    output_filename = output_filename.replace(
        '_', ' ').title().replace(' ', '_')
    output_filename = output_filename.lower()

    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / "data/vector/geojson"
    output_path = output_dir / f"{output_filename}.geojson"

    # Créer le répertoire de sortie
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"\n🔄 CONVERSION EN COURS...")
        print(f"📥 Source : {shp_path.name}")
        print(f"📤 Destination : {output_path.name}")

        # Lire le Shapefile
        gdf = gpd.read_file(shp_path)

        # Nettoyer les données
        initial_count = len(gdf)
        gdf = gdf.dropna(subset=['geometry'])
        cleaned_count = len(gdf)

        if cleaned_count == 0:
            print("❌ Aucune géométrie valide après nettoyage !")
            return None

        print(f"🧹 Géométries nettoyées : {cleaned_count}/{initial_count}")

        # Conversion du système de coordonnées si nécessaire
        if gdf.crs and gdf.crs != 'EPSG:4326':
            print("🔄 Conversion vers EPSG:4326...")
            gdf = gdf.to_crs('EPSG:4326')

        # Simplification légère des géométries
        print("🔧 Simplification des géométries...")
        gdf['geometry'] = gdf['geometry'].simplify(
            0.0001, preserve_topology=True)

        # Sauvegarder en GeoJSON
        gdf.to_file(output_path, driver='GeoJSON')

        # Vérifications finales
        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"✅ Conversion réussie !")
        print(f"📁 Fichier : {output_path}")
        print(f"📊 Taille : {file_size:.2f} MB")
        print(f"📍 Entités : {len(gdf)}")
        print(f"🎯 CRS : {gdf.crs}")

        return output_path

    except Exception as e:
        print(f"❌ Erreur lors de la conversion : {e}")
        import traceback
        traceback.print_exc()
        return None


def test_geojson_output(output_path):
    """Teste le fichier GeoJSON généré"""
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"\n🧪 VERIFICATION DU FICHIER GEOJSON")
        print("="*40)
        print(f"📊 Nombre de features : {len(data['features'])}")

        if len(data['features']) > 0:
            first_feature = data['features'][0]
            print(
                f"📝 Propriétés disponibles : {list(first_feature['properties'].keys())}")
            print(f"🔷 Type de géométrie : {first_feature['geometry']['type']}")

            # Afficher les premières propriétés non-nulles
            print(f"\n📍 Propriétés de la première entité :")
            prop_count = 0
            for key, value in first_feature['properties'].items():
                if value is not None and value != '':
                    print(f"  {key}: {value}")
                    prop_count += 1
                    if prop_count >= 5:  # Limiter à 5 propriétés
                        remaining = len(
                            first_feature['properties']) - prop_count
                        if remaining > 0:
                            print(f"  ... et {remaining} autres propriétés")
                        break

    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")


def main():
    """Fonction principale avec interface interactive"""
    print("🌍 CONVERTISSEUR SHAPEFILE -> GEOJSON")
    print("="*50)

    # Récupérer tous les datasets disponibles
    shapefile_folders = get_available_shapefiles()

    if not shapefile_folders:
        print("❌ Aucun dataset Shapefile trouvé.")
        print("💡 Assurez-vous que vos fichiers sont dans data/vector/")
        return

    # Afficher les datasets disponibles
    display_available_datasets(shapefile_folders)

    # Laisser l'utilisateur choisir
    selected_dataset = choose_dataset(shapefile_folders)

    if not selected_dataset:
        print("👋 Au revoir !")
        return

    # Inspecter le dataset sélectionné
    gdf = inspect_selected_dataset(selected_dataset)

    if gdf is None:
        print("❌ Impossible d'inspecter le dataset")
        return

    # Demander confirmation pour la conversion
    confirm = input(
        f"\n❓ Voulez-vous convertir ce dataset en GeoJSON ? (o/n) : ").strip().lower()

    if confirm not in ['o', 'oui', 'y', 'yes']:
        print("❌ Conversion annulée")
        return

    # Convertir le dataset
    output_path = convert_shapefile_to_geojson(selected_dataset)

    if output_path:
        # Tester le résultat
        test_geojson_output(output_path)

        print(f"\n🎉 Conversion terminée avec succès !")
        print(f"📁 Fichier disponible : {output_path}")
    else:
        print(f"\n❌ La conversion a échoué")


def convert_specific_dataset(dataset_name):
    """Convertir un dataset spécifique sans interface interactive"""
    base_dir = Path(__file__).parent.parent.parent
    dataset_path = base_dir / "data/vector" / dataset_name

    if not dataset_path.exists():
        print(f"❌ Dataset introuvable : {dataset_path}")
        return None

    folder_info = {
        'name': dataset_name,
        'path': dataset_path,
        'shp_count': len(list(dataset_path.glob("*.shp"))),
        'main_shp': None
    }

    shp_files = list(dataset_path.glob("*.shp"))
    if shp_files:
        folder_info['main_shp'] = shp_files[0].name

    print(f"🔧 Conversion du dataset : {dataset_name}")
    output_path = convert_shapefile_to_geojson(folder_info)

    if output_path:
        test_geojson_output(output_path)

    return output_path


if __name__ == "__main__":
    # Mode interactif par défaut
    main()

    # Exemple pour convertir un dataset spécifique en ligne de commande
    # import sys
    # if len(sys.argv) > 1:
    #     dataset_name = sys.argv[1]
    #     convert_specific_dataset(dataset_name)
    # else:
    #     main()
