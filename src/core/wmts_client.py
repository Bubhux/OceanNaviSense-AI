# src/core/wmts_client.py
from owslib.wmts import WebMapTileService
from requests.auth import HTTPBasicAuth
import requests


def get_wmts_layers(url, username, password):
    """Retourne les couches disponibles du service WMTS."""
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    if response.status_code != 200:
        raise Exception(
            f"Erreur de connexion ({response.status_code}) : {response.text[:300]}")

    wmts = WebMapTileService(url, username=username, password=password)
    layers = list(wmts.contents.keys())
    return wmts, layers
