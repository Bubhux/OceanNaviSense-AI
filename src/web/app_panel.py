# src/web/app_panel.py
import panel as pn
import param
import os
import warnings
from src.core.wmts_client import get_wmts_layers
from src.app.config import WMTS_URL, COPERNICUS_USERNAME, COPERNICUS_PASSWORD

# Supprimer tous les warnings
warnings.filterwarnings('ignore')

pn.extension(design='material')

# Désactiver les vérifications de compatibilité de layout
pn.config.layout_compatibility = 'error'


# MAPPING entre noms affichés et noms techniques
LAYER_MAPPING = {
    'Régions géographiques': 'geography_regions'
}


class CopernicusViewer(param.Parameterized):
    projection = param.Selector(default='EPSG3857', objects=[
                                'EPSG3857', 'EPSG4326'])
    layer_name = param.Selector()
    use_local_background = param.Boolean(default=True)
    zoom_level = param.Integer(default=1, bounds=(0, 10))

    # Noms affichés (lisibles)
    vector_layers = param.ListSelector(
        default=[],
        objects=[
            'Régions géographiques'
        ]
    )

    def __init__(self, **params):
        super().__init__(**params)
        self.wmts = None
        self.layers = []

        if COPERNICUS_USERNAME and COPERNICUS_PASSWORD:
            self.connect_to_wmts()

    def connect_to_wmts(self):
        try:
            self.wmts, self.layers = get_wmts_layers(
                WMTS_URL, COPERNICUS_USERNAME, COPERNICUS_PASSWORD
            )
            self.param.layer_name.objects = self.layers
            if self.layers:
                self.layer_name = self.layers[0]
        except Exception as e:
            print(f"Erreur connexion WMTS: {e}")

    @param.depends('use_local_background', 'projection', 'vector_layers', 'graticule_density')
    def view_map(self):
        if not self.use_local_background:
            return pn.pane.Markdown(
                "### 🌍 Activez 'Natural Earth' comme fond de carte",
                style={'text-align': 'center', 'padding': '100px'}
            )

        map_url = "http://localhost:8000/templates/index.html"

        # Convertir les noms affichés en noms techniques pour l'URL
        technical_layers = [LAYER_MAPPING[layer]
                            for layer in self.vector_layers]

        params = {
            'projection': self.projection,
            'vector_layers': ','.join(technical_layers) if technical_layers else '',
            'graticule_density': self.graticule_density
        }

        query_string = '&'.join([f"{k}={v}" for k, v in params.items() if v])
        map_url_with_params = f"{map_url}?{query_string}" if query_string else map_url

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                    position: fixed;
                }}
                .map-frame {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    border: none;
                    z-index: 1;
                }}
            </style>
        </head>
        <body>
            <iframe 
                src="{map_url_with_params}" 
                class="map-frame"
                sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                allow="geolocation *"
                allowfullscreen>
            </iframe>
            {self.update_projection().object}
        </body>
        </html>
        """

        return pn.pane.HTML(
            html_content,
            sizing_mode='stretch_both'
        )

    @param.depends('projection', 'vector_layers', 'graticule_density')
    def update_projection(self):
        print(f"🔄 Changement de projection vers: {self.projection}")

        technical_layers = [LAYER_MAPPING[layer]
                            for layer in self.vector_layers]

        js_code = f"""
        <script>
            (function() {{
                function applyChanges() {{
                    if (window.mapManager && window.vectorLayerManager) {{
                        console.log('💾 Sauvegarde forcée avant modifications...');
                        if (window.mapManager.saveViewState) {{
                            window.mapManager.saveViewState();
                        }}

                        const stateBefore = {{
                            center: window.mapManager.map.getView().getCenter(),
                            zoom: window.mapManager.map.getView().getZoom(),
                            projection: window.mapManager.map.getView().getProjection().getCode()
                        }};
                        console.log('📊 État AVANT modifications:', stateBefore);
                    }} else {{
                        setTimeout(applyChanges, 500);
                    }}
                }}

                setTimeout(applyChanges, 300);
            }})();
        </script>
        """
        return pn.pane.HTML(js_code, width=0, height=0, margin=0, sizing_mode='fixed')


# Application Panel
viewer = CopernicusViewer()

# Création des CheckBoxGroup MIS À JOUR
vector_layers_checkbox = pn.widgets.CheckBoxGroup(
    name='Couches Natural Earth',
    value=viewer.vector_layers,
    options=[
        'Régions géographiques'
    ],
    inline=False
)
vector_layers_checkbox.link(viewer, value='vector_layers')

sidebar_content = pn.Column(
    pn.pane.Markdown("### 🗺️ Configuration Carte", margin=(5, 5, 0, 5)),
    pn.pane.Markdown("**Projection:**", margin=(5, 5, 0, 5)),
    viewer.param.projection,
    pn.pane.Markdown("**Couche Copernicus:**", margin=(10, 5, 0, 5)),
    viewer.param.layer_name,

    pn.pane.Markdown("### 🏞️ Couches Vectorielles", margin=(15, 5, 0, 5)),
    pn.pane.Markdown("**Couches Natural Earth:**", margin=(5, 5, 0, 5)),
    vector_layers_checkbox,

    pn.pane.Markdown("### 📊 Informations", margin=(15, 5, 0, 5)),
    pn.pane.Markdown(
        f"**Utilisateur:** {COPERNICUS_USERNAME or 'Non configuré'}",
        margin=(0, 5, 0, 5)
    ),
    pn.pane.Markdown(
        "**Serveur tuiles:** ✅ Démarré",
        margin=(0, 5, 0, 5)
    ),
    pn.pane.Markdown(
        "**Statut carte:** ✅ Disponible",
        margin=(0, 5, 5, 5)
    ),

    width=380,
    height=700,
    margin=5,
    sizing_mode='fixed',
    css_classes=['custom-sidebar']
)

sidebar_card = pn.Card(
    sidebar_content,
    title="🎛️ Panneau de contrôle",
    collapsible=True,
    collapsed=True,
    width=400,
    height=900,
    styles={
        'position': 'absolute',
        'left': '5px',
        'top': '5px',
        'z-index': '1000',
        'max-height': '80vh',
        'background': 'rgba(255, 255, 255, 0.4)',
        'border-radius': '8px',
        'box-shadow': '0 2px 8px rgba(0, 0, 0, 0.1)',
        'border': '1px solid rgba(255, 255, 255, 0.3)',
        'backdrop-filter': 'blur(0px)',
        'padding': '4px'
    },
    sizing_mode='fixed'
)

# Contenu principal
main_content = pn.Column(
    viewer.view_map,
    sizing_mode='stretch_both',
    margin=0
)

# Layout final
final_app = pn.Column(
    set_browser_title(),
    main_content,
    sidebar_card,
    sizing_mode='stretch_both',
    css_classes=['app-container']
)

# Servable
final_app.servable()
