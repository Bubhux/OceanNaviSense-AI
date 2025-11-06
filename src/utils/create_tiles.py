# src/utils/create_tiles.py
import os
import sys
import math
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from osgeo import gdal
from tqdm import tqdm
import shutil
import time


# CRS par défaut
DEFAULT_CRS_LIST = [
    ("EPSG:3857", 1),
    ("EPSG:3857", 2),
    ("EPSG:3857", 3),
    ("EPSG:4326", 1),
    ("EPSG:4326", 2),
    ("EPSG:4326", 3),
]

# Augmentation du nombre de workers - adapté à votre processeur
MAX_WORKERS = 8


class ProgressTracker:
    """Classe pour gérer les barres de progression"""

    def __init__(self):
        self.bars = {}
        self.completed_tasks = 0
        self.total_tasks = 0

    def create_bar(self, task_id, description, total):
        """Crée une nouvelle barre de progression"""
        self.bars[task_id] = tqdm(
            total=total,
            desc=description,
            unit="step",
            leave=False
        )
        self.total_tasks += 1

    def update_bar(self, task_id, advance=1):
        """Met à jour une barre de progression"""
        if task_id in self.bars:
            self.bars[task_id].update(advance)

    def complete_bar(self, task_id):
        """Termine une barre de progression"""
        if task_id in self.bars:
            self.bars[task_id].close()
            self.completed_tasks += 1
            # Afficher le pourcentage global
            if self.total_tasks > 0:
                percent = (self.completed_tasks / self.total_tasks) * 100
                print(
                    f"📊 Progression globale: {self.completed_tasks}/{self.total_tasks} ({percent:.1f}%)")


# Instance globale du tracker de progression
progress_tracker = ProgressTracker()


def log(msg, verbose):
    if verbose:
        print(msg)


def find_gdal2tiles():
    """Trouve le chemin de gdal2tiles.py"""
    possible_paths = [
        os.path.join(sys.prefix, "Scripts", "gdal2tiles.py"),
        os.path.join(sys.prefix, "Scripts", "gdal2tiles.exe"),
        "gdal2tiles.py",
        "gdal2tiles.exe"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # Dernier recours: essayer d'appeler directement
    try:
        result = subprocess.run(['gdal2tiles.py', '--version'],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return 'gdal2tiles.py'
    except:
        pass

    try:
        result = subprocess.run(['gdal2tiles.exe', '--version'],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return 'gdal2tiles.exe'
    except:
        pass

    return None


def check_gdal2tiles():
    """Vérifie que gdal2tiles.py est disponible"""
    gdal2tiles_path = find_gdal2tiles()
    if gdal2tiles_path:
        print(f"✅ gdal2tiles trouvé: {gdal2tiles_path}")
        return gdal2tiles_path
    else:
        print("❌ gdal2tiles.py non trouvé")
        return None


def get_gdal2tiles_version(gdal2tiles_path):
    """Détermine la version de gdal2tiles pour adapter les options"""
    try:
        result = subprocess.run([gdal2tiles_path, '--version'],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            output = result.stdout.lower()
            if 'gdal2tiles' in output:
                return 'modern'
    except:
        pass

    # Par défaut, supposer une version ancienne
    return 'legacy'


def reproject(input_tif, output_tif, crs, verbose=False):
    """Reprojette le fichier source si nécessaire"""
    task_id = f"reproject_{crs}"
    progress_tracker.create_bar(task_id, f"🔄 Reprojection {crs}", 100)

    log(f"[Reprojection] {input_tif} → {output_tif} ({crs})", verbose)

    # Vérifier la projection actuelle
    ds = gdal.Open(input_tif)
    if ds:
        current_proj = ds.GetProjection()
        ds = None

        # Si déjà dans la bonne projection, copier simplement
        if crs in current_proj:
            log(f"[Info] Fichier déjà en {crs}, copie simple", verbose)
            shutil.copy2(input_tif, output_tif)
            progress_tracker.update_bar(task_id, 100)
            progress_tracker.complete_bar(task_id)
            return

    # Simulation de progression pour la reprojection
    for i in range(10):
        time.sleep(0.05)  # Réduit le délai pour plus de rapidité
        progress_tracker.update_bar(task_id, 10)

    # Reprojection nécessaire
    ds = gdal.Warp(output_tif, input_tif, dstSRS=crs,
                   format="GTiff", multithread=True,
                   resampleAlg='cubic', creationOptions=['COMPRESS=DEFLATE'],
                   # Augmentation des threads GDAL
                   warpOptions=['NUM_THREADS=4'])
    if ds is None:
        progress_tracker.complete_bar(task_id)
        raise RuntimeError(f"Erreur lors de la reprojection vers {crs}")
    ds = None

    progress_tracker.update_bar(task_id, 90)  # Dernière mise à jour
    progress_tracker.complete_bar(task_id)
    log(f"[Reprojection OK] {output_tif}", verbose)


def generate_tiles_gdal2tiles(gdal2tiles_path, version, input_tif, output_dir, crs, min_zoom, max_zoom, resume=False, verbose=False):
    """Génère les tuiles en utilisant gdal2tiles.py"""

    # Déterminer le type de projection pour gdal2tiles
    if crs == "EPSG:3857":
        profile = "mercator"
    elif crs == "EPSG:4326":
        profile = "geodetic"
    else:
        raise ValueError(f"CRS non supporté: {crs}")

    task_id = f"tiles_{crs}"
    total_steps = (max_zoom - min_zoom + 1) * 10  # Estimation des étapes
    progress_tracker.create_bar(task_id, f"🗺️  Génération {crs}", total_steps)

    log(f"[Tiles] Début génération - CRS={crs}, profile={profile}, zoom {min_zoom}-{max_zoom}", verbose)

    # Construire la commande gdal2tiles selon la version
    cmd = [gdal2tiles_path]

    if version == 'modern':
        # Options pour les versions modernes
        cmd.extend([
            '-p', profile,
            '-z', f'{min_zoom}-{max_zoom}',
            '-w', 'none',  # Pas de génération de page web
            '--xyz',       # Format XYZ
            '--processes', '2',  # Utilisation de plusieurs processus
        ])

        if resume:
            cmd.append('-r')
        if verbose:
            cmd.append('-v')

    else:
        # Options pour les versions anciennes
        cmd.extend([
            '-p', profile,
            '-z', f'{min_zoom}-{max_zoom}',
            '-w', 'none',
        ])

        if verbose:
            cmd.append('-v')

    # Fichier source et répertoire de destination
    cmd.extend([input_tif, output_dir])

    # Exécuter la commande
    log(f"[Commande] {' '.join(cmd)}", verbose)

    try:
        # Utiliser subprocess.Popen pour lire la sortie en temps réel
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Lire la sortie en temps réel pour mettre à jour la progression
        lines_processed = 0
        while True:
            output_line = process.stdout.readline()
            if output_line == '' and process.poll() is not None:
                break
            if output_line:
                lines_processed += 1
                # Mettre à jour la progression plus fréquemment
                if lines_processed % 3 == 0:  # Mettre à jour toutes les 3 lignes
                    progress_tracker.update_bar(task_id, 1)

                if verbose:
                    print(f"[gdal2tiles] {output_line.strip()}")

        # Attendre la fin du processus
        return_code = process.wait()

        if return_code == 0:
            progress_tracker.update_bar(
                task_id, total_steps - lines_processed)  # Compléter la barre
            progress_tracker.complete_bar(task_id)

            log(f"[Tiles OK] Tuiles générées dans {output_dir}", verbose)

            # Compter le nombre de tuiles générées
            tile_count = count_tiles_in_directory(output_dir)
            return tile_count
        else:
            progress_tracker.complete_bar(task_id)
            error_msg = f"Erreur gdal2tiles (code {return_code})"
            log(f"❌ {error_msg}", verbose)
            raise RuntimeError(error_msg)

    except subprocess.TimeoutExpired:
        progress_tracker.complete_bar(task_id)
        error_msg = "Timeout lors de l'exécution de gdal2tiles"
        log(f"❌ {error_msg}", verbose)
        raise RuntimeError(error_msg)
    except Exception as e:
        progress_tracker.complete_bar(task_id)
        log(f"❌ Exception lors de l'exécution de gdal2tiles: {e}", verbose)
        raise


def count_tiles_in_directory(directory):
    """Compte le nombre de fichiers PNG dans un répertoire"""
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.png'):
                count += 1
    return count


def get_total_size(path):
    total_size = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size


def process_crs(gdal2tiles_path, version, input_file, output_dir, crs, scale, min_zoom, max_zoom, resume, verbose):
    """Traite un CRS spécifique"""
    scale_suffix = f"@{scale}x" if scale > 1 else ""
    crs_name = crs.replace(":", "")
    crs_dir = os.path.join(output_dir, f"{crs_name}{scale_suffix}")

    # Si resume et le répertoire existe déjà, vérifier s'il est complet
    if resume and os.path.exists(crs_dir):
        log(f"[Resume] Utilisation du répertoire existant: {crs_dir}", verbose)
    else:
        os.makedirs(crs_dir, exist_ok=True)

    # Reprojection si nécessaire
    reprojected_tif = os.path.join(crs_dir, "reprojected.tif")
    reproject(input_file, reprojected_tif, crs, verbose)

    # Génération des tuiles avec gdal2tiles
    tile_count = generate_tiles_gdal2tiles(
        gdal2tiles_path, version, reprojected_tif, crs_dir, crs, min_zoom, max_zoom, resume, verbose)

    total_size = get_total_size(crs_dir)

    log(f"[Process CRS] {crs} terminé → {crs_dir} ({tile_count} tuiles, {total_size / (1024*1024):.1f} Mo)", verbose)
    return crs, tile_count, total_size


def parse_args():
    parser = argparse.ArgumentParser(
        description="Création de tuiles XYZ avec gdal2tiles")
    parser.add_argument("input_file", help="Fichier GeoTIFF d'entrée")
    parser.add_argument("output_dir", help="Répertoire de sortie")
    parser.add_argument("--min-zoom", type=int, default=0, help="Zoom minimum")
    parser.add_argument("--max-zoom", type=int, default=5, help="Zoom maximum")
    parser.add_argument("--crs", nargs="+",
                        help="Liste CRS@scale ex: EPSG:3857@1 EPSG:4326@2")
    parser.add_argument("--resume", action="store_true",
                        help="Reprendre les tuiles existantes")
    parser.add_argument("--verbose", action="store_true",
                        help="Afficher les logs détaillés")
    return parser.parse_args()


def build_crs_list(crs_args):
    if not crs_args:
        return DEFAULT_CRS_LIST
    result = []
    for arg in crs_args:
        if "@" in arg:
            crs, scale = arg.split("@")
            scale = scale.rstrip("xX")
            try:
                result.append((crs, int(scale)))
            except ValueError:
                raise ValueError(
                    f"Format invalide pour scale : '{scale}' dans '{arg}'")
        else:
            result.append((arg, 1))
    return result


def estimate_total_size(min_zoom, max_zoom, avg_tile_size_kb, num_crs):
    """Estime la taille totale en Ko selon le zoom et le nombre de CRS"""
    total_tiles = sum((2 ** z) ** 2 for z in range(min_zoom, max_zoom + 1))
    total_size_kb = total_tiles * avg_tile_size_kb * num_crs
    return total_tiles, total_size_kb


def get_free_space(path):
    """Retourne l'espace libre du disque (en octets)"""
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except:
            path = os.getcwd()

    try:
        stat = shutil.disk_usage(path)
        return stat.free
    except Exception as e:
        print(f"⚠️ Impossible de vérifier l'espace disque: {e}")
        return 100 * 1024 * 1024 * 1024  # 100 GB


def remove_reprojected_files():
    """Supprime les fichiers reprojetés temporaires"""
    paths = []
    for root, dirs, files in os.walk("data/map/tiles"):
        for file in files:
            if file == "reprojected.tif":
                paths.append(os.path.join(root, file))

    removed_count = 0
    for path in paths:
        if os.path.exists(path):
            try:
                os.remove(path)
                removed_count += 1
            except Exception as e:
                print(f"[Erreur suppression] {path} → {e}")

    if removed_count > 0:
        print(
            f"[Suppression OK] {removed_count} fichiers temporaires supprimés")


def main():
    """Fonction principale avec barre de progression globale"""
    # Vérifier que gdal2tiles est disponible
    gdal2tiles_path = check_gdal2tiles()
    if not gdal2tiles_path:
        print("❌ gdal2tiles non trouvé. Arrêt.")
        sys.exit(1)

    # Déterminer la version
    version = get_gdal2tiles_version(gdal2tiles_path)
    print(f"🔧 Version détectée: {version}")

    args = parse_args()
    crs_list = build_crs_list(args.crs)

    # S'assurer que le répertoire de sortie existe
    os.makedirs(args.output_dir, exist_ok=True)

    # === Estimation avant génération ===
    print("\n🔍 Estimation avant génération des tuiles...\n")

    num_crs = len(crs_list)
    avg_tile_size_kb = 12
    total_tiles, total_size_kb = estimate_total_size(
        args.min_zoom, args.max_zoom, avg_tile_size_kb, num_crs)

    total_size_gb = total_size_kb / (1024 * 1024)
    free_space_gb = get_free_space(args.output_dir) / (1024 * 1024 * 1024)

    print(
        f"🗺️  Nombre estimé de tuiles : {total_tiles:,} (pour {num_crs} CRS)")
    print(f"💾 Taille estimée : {total_size_gb:.2f} Go")
    print(f"📂 Espace disque disponible : {free_space_gb:.2f} Go")
    print(f"📁 Répertoire de sortie : {os.path.abspath(args.output_dir)}")
    print(f"🔧 Méthode : gdal2tiles.py ({version})")
    print(f"🚀 Workers parallèles : {MAX_WORKERS}")

    if free_space_gb < total_size_gb * 1.1:
        print("⚠️  Espace disque potentiellement insuffisant !")

    confirm = input(
        "\nSouhaitez-vous continuer la génération ? (O/N) : ").strip().lower()
    if confirm not in ["o", "oui", "y", "yes"]:
        print("❌ Génération annulée par l'utilisateur.")
        sys.exit(0)

    print("\n✅ Lancement de la génération des tuiles avec gdal2tiles...\n")

    # Barre de progression globale
    global_progress = tqdm(total=len(crs_list) * 2,
                           desc="🌍 Progression globale", unit="task")

    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(process_crs, gdal2tiles_path, version, args.input_file, args.output_dir, crs, scale,
                            args.min_zoom, args.max_zoom, args.resume, args.verbose)
            for crs, scale in crs_list
        ]

        for future in as_completed(futures):
            try:
                results.append(future.result())
                global_progress.update(1)
            except Exception as e:
                print(f"[Erreur] {e}")
                global_progress.update(1)

    global_progress.close()

    # === Rapport final ===
    print("\n" + "="*50)
    print("📊 RAPPORT FINAL")
    print("="*50)

    total_tiles_global = 0
    total_size_global = 0
    for crs, tile_count, total_size in results:
        print(
            f"   {crs:<12} → {tile_count:>8} tuiles, {total_size / (1024*1024):.2f} Mo")
        total_tiles_global += tile_count
        total_size_global += total_size

    print(
        f"\n   TOTAL GÉNÉRAL : {total_tiles_global:,} tuiles, {total_size_global / (1024*1024):.2f} Mo")
    print("="*50)

    # Suppression des fichiers temporaires
    print("\n🗑️ Suppression des fichiers reprojected.tif...")
    remove_reprojected_files()
    print("✅ Suppression terminée.")

    print("\n🎉 Génération terminée avec succès!")
    print("📂 Les tuiles sont prêtes dans:", os.path.abspath(args.output_dir))


if __name__ == "__main__":
    main()
