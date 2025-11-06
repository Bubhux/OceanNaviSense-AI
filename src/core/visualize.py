# src/core/visualize.py
import folium
import streamlit.components.v1 as components


def create_wmts_map(wmts_url, layer_name, username, password):
    """Crée une carte Folium intégrant une couche WMTS."""
    m = folium.Map(location=[0, 0], zoom_start=2)

    folium.raster_layers.WmsTileLayer(
        url=wmts_url,
        layers=layer_name,
        name=layer_name,
        fmt='image/png',
        transparent=True,
        version='1.3.0',
        attr="Copernicus Marine Service"
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


def display_folium_map(m):
    """Affiche une carte Folium dans Streamlit."""
    map_html = m._repr_html_()
    components.html(map_html, height=600)
