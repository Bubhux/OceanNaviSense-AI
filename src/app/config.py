# src/app/config.py
import os
from dotenv import load_dotenv

# Charger les variables d’environnement du fichier .env
load_dotenv()

WMTS_URL = "https://wmts.marine.copernicus.eu/teroWmts/GLOBAL_ANALYSISFORECAST_WAV_001_027/cmems_mod_glo_wav_anfc_0.083deg_PT3H-i_202411?request=GetCapabilities&service=WMS"

COPERNICUS_USERNAME = os.getenv("COPERNICUS_USERNAME")
COPERNICUS_PASSWORD = os.getenv("COPERNICUS_PASSWORD")
