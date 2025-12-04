// static/js/map.js
import { TileValidator } from './tileValidator.js';
import { ScaleBar } from './scaleBar.js';
import { ZoomController } from './zoomController.js';
import { CoordinatesControl } from './coordinates.js';

export class MapManager {
    constructor() {
        this.map = null;
        this.zoomController = null;
        this.coordinatesControl = null;
        this.scaleBar = null;
        this.currentProjection = window.mapProjection || 'EPSG3857';
        this.tileSource = null;

        // NETTOYAGE FORCÉ POUR PREMIER DÉMARRAGE
        this.cleanFirstStart();

        // Toujours charger depuis localStorage (sera vide au premier démarrage)
        this.viewState = this.loadViewState() || {
            center: null,
            zoom: null,
            resolution: null,
            projection: null
        };

        console.log('💾 État initial:', this.viewState);

        // LIER les méthodes
        this.saveViewState = this.saveViewState.bind(this);
        this.updateZoomInfo = this.updateZoomInfo.bind(this);
    }

    // Nouvelle méthode pour nettoyer au premier démarrage
    cleanFirstStart() {
        const firstStart = sessionStorage.getItem('appFirstStart');
        if (firstStart === null) {
            console.log('🆕 Premier démarrage - nettoyage localStorage');
            localStorage.removeItem('mapViewState');
            sessionStorage.setItem('appFirstStart', 'done');
        }
    }

    // Détection de première visite
    detectFirstVisit() {
        try {
            const firstVisit = sessionStorage.getItem('firstVisit');
            if (firstVisit === null) {
                // Première visite dans cette session
                sessionStorage.setItem('firstVisit', 'false');
                // Vérifier si c'est la toute première visite (pas de localStorage)
                const hasSavedState = localStorage.getItem('mapViewState') !== null;
                return !hasSavedState;
            }
            return false;
        } catch (error) {
            console.warn('⚠️ Impossible de détecter première visite:', error);
            return true; // Par défaut, considérer comme première visite
        }
    }

    // === SAUVEGARDE EN TEMPS RÉEL SIMPLIFIÉE ===
    saveViewState() {
        if (this.map && this.map.getView()) {
            const view = this.map.getView();
            const newState = {
                center: view.getCenter() ? [...view.getCenter()] : null,
                zoom: view.getZoom(),
                resolution: view.getResolution(),
                projection: view.getProjection().getCode(),
                timestamp: Date.now()
            };

            try {
                localStorage.setItem('mapViewState', JSON.stringify(newState));

                // Log pour débogage
                //console.log('💾 État sauvegardé:', {
                //    center: newState.center,
                //    zoom: newState.zoom,
                //    projection: newState.projection
                //});

                this.viewState = newState;
            } catch (error) {
                console.warn('⚠️ Impossible de sauvegarder:', error);
            }
        }
    }

    loadViewState() {
        try {
            const saved = localStorage.getItem('mapViewState');
            if (saved) {
                const state = JSON.parse(saved);
                console.log('📥 État chargé depuis localStorage:', state);
                return state;
            }
        } catch (error) {
            console.warn('⚠️ Impossible de charger l\'état:', error);
        }
        return null;
    }

    // === METHODE POUR NETTOYER MANUELLEMENT ===
    clearStorage() {
        console.log('🧹 Nettoyage manuel du stockage');
        localStorage.removeItem('mapViewState');
        sessionStorage.removeItem('firstVisit');
        this.viewState = {
            center: null,
            zoom: null,
            resolution: null,
            projection: null
        };
        console.log('✅ Stockage nettoyé manuellement');
    }

    // === INITIALISATION DE LA CARTE ===
    initMap() {
        console.log('🔍 Initialisation Natural Earth avec projection:', this.currentProjection);
        console.log('📋 Statut visite:', this.isFirstVisit ? 'PREMIÈRE VISITE' : 'VISITE PRÉCÉDENTE');

        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }

        const config = this.getProjectionConfig();
        const { initialCenter, initialZoom } = this.calculateInitialView(config);

        console.log('🎯 Configuration vue initiale:', {
            center: initialCenter,
            zoom: initialZoom,
            projection: config.code
        });

        const tileGrid = new ol.tilegrid.TileGrid({
            extent: config.extent,
            origin: config.origin,
            resolutions: config.resolutions,
            tileSize: 256
        });

        const self = this;
        this.tileSource = new ol.source.TileImage({
            projection: config.code,
            tileGrid: tileGrid,
            tileUrlFunction: function (tileCoord) {
                return self.getTileUrl(tileCoord);
            },
            crossOrigin: 'anonymous'
        });

        const view = new ol.View({
            projection: config.code,
            center: initialCenter,
            zoom: initialZoom,
            extent: config.extent,
            resolutions: config.resolutions,
            minZoom: config.minZoom,
            maxZoom: config.maxZoom,
            constrainOnlyCenter: false,
            smoothExtentConstraint: true,
            enableRotation: config.enableRotation !== false,
            multiWorld: false
        });

        this.map = new ol.Map({
            target: 'map',
            layers: [
                new ol.layer.Tile({
                    source: this.tileSource,
                    extent: config.extent
                })
            ],
            view: view,
            controls: []
        });

        setTimeout(() => {
            this.map.updateSize();
            this.map.renderSync();

            // CORRECTION : Appliquer showWholeWorld() seulement pour la première visite
            if (this.isFirstVisit) {
                console.log('🌍 Première visite - application vue mondiale');
                this.showWholeWorld();
            }

            // MISE À JOUR INITIALE DU PANEL D'INFO
            this.updateZoomInfo();
            this.saveViewState(); // Sauvegarder l'état initial
        }, 100);

        this.map.addControl(new ol.control.ScaleLine());
        this.setupEventListeners();
        this.initControls();

        console.log('✅✅✅ Carte initialisée avec projection:', this.currentProjection);
        return this.map;
    }

    calculateInitialView(config) {
        let initialCenter, initialZoom;

        // Si ce n'est pas la première visite ET qu'un état valide existe
        if (!this.isFirstVisit && this.viewState.center && this.viewState.zoom !== null &&
            this.isValidCenter(this.viewState.center, config)) {

            if (this.viewState.projection === config.code) {
                initialCenter = this.viewState.center;
                initialZoom = this.viewState.zoom;
                console.log('🎯 Utilisation état sauvegardé:', { center: initialCenter, zoom: initialZoom });
            } else {
                console.log('🔄 Conversion nécessaire entre projections');
                if (this.viewState.projection === 'EPSG:4326' && config.code === 'EPSG:3857') {
                    initialCenter = ol.proj.fromLonLat(this.viewState.center);
                    initialZoom = this.viewState.zoom;
                } else if (this.viewState.projection === 'EPSG:3857' && config.code === 'EPSG:4326') {
                    initialCenter = ol.proj.toLonLat(this.viewState.center);
                    initialZoom = this.viewState.zoom;
                } else {
                    // Fallback vers vue par défaut
                    const defaultView = this.getDefaultView();
                    initialCenter = defaultView.center;
                    initialZoom = defaultView.zoom;
                }
                console.log('🎯 Utilisation état converti:', { center: initialCenter, zoom: initialZoom });
            }
        } else {
            // Utiliser la vue par défaut (sera remplacé par showWholeWorld si première visite)
            const defaultView = this.getDefaultView();
            initialCenter = defaultView.center;
            initialZoom = defaultView.zoom;
            console.log('🎯 Utilisation position par défaut:', {
                center: initialCenter,
                zoom: initialZoom
            });
        }

        return { initialCenter, initialZoom };
    }

    // Vérifier si le centre est valide pour la projection
    isValidCenter(center, config) {
        if (!center || center.length !== 2) return false;

        const [x, y] = center;
        const [minX, minY, maxX, maxY] = config.extent;

        return x >= minX && x <= maxX && y >= minY && y <= maxY;
    }

    // Vue par défaut (utilisée temporairement avant showWholeWorld)
    getDefaultView() {
        if (this.currentProjection === 'EPSG3857') {
            return {
                center: ol.proj.fromLonLat([0, 0]),
                zoom: 1
            };
        } else {
            return {
                center: [0, 0],
                zoom: 1
            };
        }
    }

    // === CONFIGURATION DES ÉVÉNEMENTS ===
    setupEventListeners() {
        const view = this.map.getView();

        // CORRECTION : Mettre à jour le panneau d'info ET sauvegarder
        const updateAndSave = () => {
            this.updateZoomInfo();
            this.saveViewState();
        };

        // Événements principaux - mettre à jour le panneau ET sauvegarder
        view.on('change:resolution', updateAndSave);
        view.on('change:center', updateAndSave);
        view.on('change:rotation', updateAndSave);

        // Événements de fin d'interaction
        this.map.on('moveend', updateAndSave);

        // Redimensionnement
        window.addEventListener('resize', () => {
            setTimeout(() => {
                if (this.map) {
                    this.map.updateSize();
                    const currentZoom = this.map.getView().getZoom();
                    if (this.zoomController) {
                        this.zoomController.updateZoomControl(currentZoom);
                    }
                    if (this.scaleBar) {
                        this.scaleBar.updateScaleBar();
                    }
                    updateAndSave(); // Mettre à jour le panneau ET sauvegarder
                }
            }, 100);
        });

        // Événement de chargement complet de la carte
        this.map.on('loadend', () => {
            this.updateZoomInfo();
        });
    }

    initControls() {
        this.zoomController = new ZoomController(this.map);

        setTimeout(() => {
            console.log('🗺️ Initialisation du contrôle des coordonnées...');
            try {
                this.coordinatesControl = new CoordinatesControl(this.map);
                console.log('✅ CoordinatesControl initialisé avec succès');
            } catch (error) {
                console.error('❌ Erreur initialisation CoordinatesControl:', error);
            }
        }, 100);

        this.scaleBar = new ScaleBar();
        this.scaleBar.init(this.map);
    }

    changeProjection(newProjection) {
        console.log(`🔄 Changement de projection vers: ${newProjection}`);

        // Sauvegarder l'état actuel AVANT le changement
        this.saveViewState();

        this.currentProjection = newProjection;

        if (this.map) {
            const config = this.getProjectionConfig();
            const currentView = this.map.getView();

            // Convertir le centre si nécessaire
            let newCenter = currentView.getCenter();
            if (currentView.getProjection().getCode() === 'EPSG:3857' && config.code === 'EPSG:4326') {
                newCenter = ol.proj.toLonLat(newCenter);
            } else if (currentView.getProjection().getCode() === 'EPSG:4326' && config.code === 'EPSG:3857') {
                newCenter = ol.proj.fromLonLat(newCenter);
            }

            const newView = new ol.View({
                projection: config.code,
                center: newCenter,
                zoom: currentView.getZoom(),
                extent: config.extent,
                resolutions: config.resolutions,
                minZoom: config.minZoom,
                maxZoom: config.maxZoom,
                constrainOnlyCenter: false,
                smoothExtentConstraint: true,
                enableRotation: config.enableRotation,
                multiWorld: false
            });

            this.map.setView(newView);

            setTimeout(() => {
                this.map.updateSize();
                this.map.renderSync();
                // Mettre à jour le panneau ET sauvegarder après le changement
                this.updateZoomInfo();
                this.saveViewState();
                console.log('✅ Projection changée avec succès');
            }, 100);
        }
    }

    getProjectionConfig() {
        const projections = {
            'EPSG3857': {
                code: 'EPSG:3857',
                extent: [-20037508.34, -20037508.34, 20037508.34, 20037508.34],
                origin: [-20037508.34, 20037508.34],
                resolutions: [
                    156543.03392804097, 78271.51696402048, 39135.75848201024,
                    19567.87924100512, 9783.93962050256, 4891.96981025128,
                    2445.98490512564, 1222.99245256282, 611.49622628141,
                    305.748113140705, 152.8740565703525, 76.43702828517625
                ],
                minZoom: 0,
                maxZoom: 10,
                enableRotation: true
            },
            'EPSG4326': {
                code: 'EPSG:4326',
                extent: [-180, -90, 180, 90],
                origin: [-180, 90],
                resolutions: [
                    1.40625,
                    0.703125,
                    0.3515625,
                    0.17578125,
                    0.087890625,
                    0.0439453125,
                    0.02197265625,
                    0.010986328125,
                    0.0054931640625,
                    0.00274658203125,
                    0.001373291015625
                ],
                minZoom: 0,
                maxZoom: 10,
                enableRotation: false
            }
        };

        return projections[this.currentProjection];
    }

    getTileUrl(tileCoord) {
        const z = tileCoord[0];
        const x = tileCoord[1];
        const y = tileCoord[2];

        const isValid = TileValidator.isValidTile(this.currentProjection, z, x, y);

        if (!isValid) {
            if (this.currentProjection === 'EPSG4326') {
                console.warn(`🚫 Tuile EPSG4326 invalide ignorée: ${z}/${x}/${y}`);
            }
            return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
        }

        let y_corrected;

        if (this.currentProjection === 'EPSG3857') {
            y_corrected = (Math.pow(2, z) - 1) - y;
        } else {
            const limits = TileValidator.getEPSG4326Limits(z);
            y_corrected = limits.maxY - y;
        }

        const url = `http://localhost:8000/data/map/tiles/${this.currentProjection}/${z}/${x}/${y_corrected}.png`;
        return url;
    }
}

// Export pour utilisation dans d'autres modules
export default MapManager;