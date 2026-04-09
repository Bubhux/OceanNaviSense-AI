// static/js/vectorLayers.js
/**
 * Point d'entrée principal pour les couches vectorielles
 * Avec Vite, tout est déjà bundle, donc pas besoin de chargement dynamique
 */

let vectorManager = null;
let isVectorModulesLoaded = false;

function initializeVectorLayerManager() {
    console.log('🔍 Vérification de la disponibilité de la carte...');

    // Attendre que la carte ET le MapManager soient initialisés
    const checkMapReady = () => {
        if (window.mapManager && window.mapManager.map) {
            createVectorManager();
        } else {
            console.log('⏳ En attente de l\'initialisation de la carte...');
            setTimeout(checkMapReady, 100);
        }
    };

    checkMapReady();
}