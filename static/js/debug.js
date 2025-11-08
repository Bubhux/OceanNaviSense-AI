// static/js/debug.js
window.debug = {
    // Debug général de la carte
    showDebugInfo: function () {
        if (!window.mapManager || !window.mapManager.map) {
            console.error('❌ Carte non disponible');
            return;
        }

        const map = window.mapManager.map;
        const view = map.getView();
        const currentZoom = view.getZoom();
        const frontendPercent = Math.round(((currentZoom - 3) / 7) * 100);

        console.log('=== 🐛 DEBUG GÉNÉRAL ===');
        console.log('- Zoom back-end actuel:', currentZoom);
        console.log('- Pourcentage front-end calculé:', frontendPercent + '%');
        console.log('- Centre de la vue:', view.getCenter());
        console.log('- Projection:', view.getProjection().getCode());
        console.log('- Résolution:', view.getResolution());
        console.log('- Étendue vue:', view.calculateExtent());

        // Conversion coordonnées pour lisibilité
        const center = view.getCenter();
        if (view.getProjection().getCode() === 'EPSG:3857') {
            const lonLat = ol.proj.toLonLat(center);
            console.log('- Centre (lon/lat):', lonLat.map(coord => coord.toFixed(4)));
        } else {
            console.log('- Centre (lat/lon):', center.map(coord => coord.toFixed(4)));
        }

        // État sauvegardé
        if (window.mapManager.viewState) {
            console.log('- État sauvegardé:', window.mapManager.viewState);
        }

        console.log('=== FIN DEBUG GÉNÉRAL ===');
    },
};

// === EXPOSITION GLOBALE POUR LES BOUTONS ===

// Commandes générales
window.showDebugInfo = function () { window.debug.showDebugInfo(); };

// Auto-initialisation des logs
setTimeout(() => {
    console.log('🔧 Debug utilitaire chargé! Commandes disponibles:');
    console.log('• showDebugInfo() - Debug général');
}, 2000);

// Surveillance automatique des changements de vue
if (typeof window !== 'undefined' && window.mapManager) {
    let lastViewState = null;

    setInterval(() => {
        if (window.mapManager && window.mapManager.map) {
            const view = window.mapManager.map.getView();
            const currentState = {
                center: view.getCenter(),
                zoom: view.getZoom()
            };

            if (lastViewState &&
                (Math.abs(lastViewState.center[0] - currentState.center[0]) > 1000 ||
                    Math.abs(lastViewState.center[1] - currentState.center[1]) > 1000 ||
                    Math.abs(lastViewState.zoom - currentState.zoom) > 0.1)) {
                console.log('🔄 Changement de vue détecté:', {
                    center: currentState.center,
                    zoom: currentState.zoom
                });
            }

            lastViewState = currentState;
        }
    }, 1000);
}