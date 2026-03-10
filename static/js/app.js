// static/js/app.js
import { MapManager } from './map.js';

// Déclarer les propriétés étendues de Window
/**
 * @typedef {Object} CustomWindow
 * @property {any} mapManager
 * @property {any} map
 * @property {any} vectorLayerManager
 * @property {boolean} urlLayersLoaded
 * @property {Function} zoomIn
 * @property {Function} zoomOut
 * @property {Function} setZoom
 * @property {Function} showWholeWorld
 * @property {Function} centerOnLatitude
 * @property {Function} centerOnNorthPole
 * @property {Function} centerOnSouthPole
 * @property {Function} reloadVectorLayers
 * @property {Function} setVectorLayerManager
 * @property {Function} getAppStatus
 * @property {Function} loadVectorLayersFromURL
 * @property {Function} areVectorModulesLoaded
 */

/** @type {Window & CustomWindow} */
const customWindow = window;

let mapManager;
let vectorLayerManager = null;
let isMapInitialized = false;
let appStarted = false;
customWindow.urlLayersLoaded = false;

function initMap() {
    if (appStarted) {
        console.log('⚠️ Application déjà démarrée');
        return;
    }
    appStarted = true;

    console.log('🗺️ Initialisation de la carte...');

    try {
        mapManager = new MapManager()
        const map = mapManager.initMap();

        // Marquer comme initialisé
        isMapInitialized = true;
        console.log('✅ Carte initialisée avec succès');

        // Stocker les références globales
        customWindow.mapManager = mapManager;
        customWindow.map = map;

        console.log('✅ Références globales stockées');

        // Initialiser les contrôles
        setTimeout(function () {
            if (mapManager.zoomController) {
                mapManager.zoomController.updateZoomControl(3);
            }
        }, 200);

        // Exposer les méthodes globales
        customWindow.zoomIn = function () { mapManager.zoomIn(); };
        customWindow.zoomOut = function () { mapManager.zoomOut(); };
        customWindow.setZoom = function (level) { mapManager.setZoom(level); };
        customWindow.showWholeWorld = function () { mapManager.showWholeWorld(); };
        customWindow.centerOnLatitude = function (latitude) { mapManager.centerOnLatitude(latitude); };
        customWindow.centerOnNorthPole = function () { mapManager.centerOnNorthPole(); };
        customWindow.centerOnSouthPole = function () { mapManager.centerOnSouthPole(); };

        // Déclencher l'initialisation du VectorLayerManager si les modules sont chargés
        if (customWindow.areVectorModulesLoaded && customWindow.areVectorModulesLoaded()) {
            console.log('🚀 Modules vectoriels déjà chargés, initialisation...');
        } else {
            console.log('⏳ En attente du chargement des modules vectoriels...');
        }

        // Charger les couches depuis les paramètres d'URL
        setTimeout(() => {
            loadVectorLayersFromURL();
        }, 1000);

    } catch (error) {
        console.error('❌ Erreur lors de l\'initialisation de la carte:', error);
        appStarted = false;
    }
}

function loadVectorLayersFromURL() {
    if (customWindow.urlLayersLoaded) {
        console.log('✅ Couches URL déjà chargées, ignoré');
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const vectorLayers = urlParams.get('vector_layers');
    const regionTypes = urlParams.get('region_types');
    const marineProps = urlParams.get('marine_props');
    const graticuleProps = urlParams.get('graticule_props');
    const graticuleDensity = urlParams.get('graticule_density') || 'auto';
    const labelTypes = urlParams.get('label_types');

    if (vectorLayers && customWindow.vectorLayerManager) {
        const layersArray = vectorLayers.split(',').filter(l => l);
        const regionTypesArray = regionTypes ? regionTypes.split(',').filter(t => t) : [];
        const marinePropsArray = marineProps ? marineProps.split(',').filter(m => m) : [];
        const graticulePropsArray = graticuleProps ? graticuleProps.split(',').filter(g => g) : [];
        const labelTypesArray = labelTypes ? labelTypes.split(',').filter(l => l) : [];

        console.log('📥 Chargement couches depuis URL:', {
            layers: layersArray,
            regionTypes: regionTypesArray,
            marineProps: marinePropsArray,
            graticuleProps: graticulePropsArray,
            graticuleDensity: graticuleDensity,
            labelTypes: labelTypesArray
        });

        customWindow.urlLayersLoaded = true;

        const tryUpdate = () => {
            if (customWindow.vectorLayerManager && customWindow.vectorLayerManager.isReady) {
                console.log('✅ Gestionnaire vectoriel prêt, mise à jour des couches');
                customWindow.vectorLayerManager.updateVectorLayers(
                    layersArray,           // layers
                    regionTypesArray,      // regionTypes
                    marinePropsArray,      // marineProperties  
                    graticulePropsArray,   // graticuleProperties
                    graticuleDensity,      // graticuleDensity
                    labelTypesArray        // labelTypes
                );
                vectorLayerManager = customWindow.vectorLayerManager;
            } else if (customWindow.vectorLayerManager) {
                console.log('⏳ En attente du chargement des données...');
                setTimeout(tryUpdate, 500);
            } else {
                console.log('❌ VectorLayerManager non disponible');
            }
        };

        tryUpdate();
    } else if (vectorLayers) {
        console.log('⏳ VectorLayerManager pas encore disponible, report du chargement...');
        setTimeout(loadVectorLayersFromURL, 1000);
    }
}

function setupSessionCleanup() {
    // Nettoyer lors de la fermeture de l'onglet/navigateur
    window.addEventListener('beforeunload', function () {
        try {
            sessionStorage.removeItem('mapSessionActive');
            console.log('🧹 Session nettoyée');
        } catch (error) {
            console.warn('⚠️ Impossible de nettoyer la session:', error);
        }
    });
}

// Fonction pour forcer le rechargement
customWindow.reloadVectorLayers = function () {
    const manager = customWindow.vectorLayerManager || vectorLayerManager;
    if (manager && manager.currentLayers) {
        console.log('🔄 Rechargement forcé des couches vectorielles');
        manager.updateVectorLayers(
            Array.from(manager.currentLayers),
            Array.from(manager.regionTypes || []),
            Array.from(manager.marineProperties || []),
            Array.from(manager.graticuleProperties || [])
        );
    } else {
        console.log('❌ Impossible de recharger - VectorLayerManager non disponible');
    }
};

// Fonction pour définir le VectorLayerManager
customWindow.setVectorLayerManager = function (manager) {
    vectorLayerManager = manager;
    customWindow.vectorLayerManager = manager;
    console.log('✅ VectorLayerManager défini et synchronisé');

    if (!customWindow.urlLayersLoaded) {
        setTimeout(loadVectorLayersFromURL, 500);
    }
};

// DÉMARRAGE
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Démarrage de l\'application...');
    setupSessionCleanup();

    if (typeof MapManager === 'undefined') {
        console.error('❌ MapManager non chargé - vérifiez les imports de scripts');
        setTimeout(() => {
            if (typeof MapManager !== 'undefined') {
                initMap();
            } else {
                console.error('❌ MapManager toujours non disponible');
            }
        }, 1000);
        return;
    }

    setTimeout(initMap, 100);
});

// Exposer pour le debug
customWindow.getAppStatus = function () {
    const manager = customWindow.vectorLayerManager || vectorLayerManager;
    return {
        mapManager: !!mapManager,
        vectorLayerManager: !!manager,
        isMapInitialized: isMapInitialized,
        map: mapManager ? mapManager.map : null,
        vectorLayers: manager ? Array.from(manager.vectorLayers.keys()) : [],
        vectorModulesLoaded: customWindow.areVectorModulesLoaded ? customWindow.areVectorModulesLoaded() : false,
        urlLayersLoaded: customWindow.urlLayersLoaded
    };
};
