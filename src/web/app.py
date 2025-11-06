# src/web/app.py
import streamlit as st
from src.core.wmts_client import get_wmts_layers
from src.core.visualize import create_wmts_map, display_folium_map
from src.app.config import WMTS_URL, COPERNICUS_USERNAME, COPERNICUS_PASSWORD
from dotenv import set_key

st.set_page_config(page_title="Copernicus Marine WMTS Viewer", layout="wide")

st.title("🌊 Copernicus Marine WMTS Viewer")
st.markdown(
    "Visualisez les données Global Wave Forecast (3-hourly) de Copernicus Marine.")

# --- Authentification ---
st.sidebar.header("🔐 Authentification Copernicus Marine")

username = st.sidebar.text_input(
    "Nom d’utilisateur", value=COPERNICUS_USERNAME or "")
password = st.sidebar.text_input(
    "Mot de passe", value=COPERNICUS_PASSWORD or "", type="password")

# Option d'enregistrement
save_credentials = st.sidebar.checkbox(
    "💾 Enregistrer ces identifiants dans le fichier .env")

if save_credentials and username and password:
    set_key(".env", "COPERNICUS_USERNAME", username)
    set_key(".env", "COPERNICUS_PASSWORD", password)
    st.sidebar.success("Identifiants sauvegardés dans .env ✅")

# Connexion
if username and password:
    try:
        wmts, layers = get_wmts_layers(WMTS_URL, username, password)
        st.success(f"Connexion réussie. {len(layers)} couches disponibles.")

        selected_layer = st.selectbox(
            "🛰️ Sélectionnez une couche à afficher :", layers)

        if st.button("Afficher la carte"):
            m = create_wmts_map(WMTS_URL, selected_layer, username, password)
            display_folium_map(m)

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
else:
    st.info("Veuillez entrer vos identifiants Copernicus Marine dans la barre latérale.")
