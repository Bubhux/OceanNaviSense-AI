// static/js/vectorLayers/VectorLayerManager.js
/**
 * Gestionnaire principal des couches vectorielles
 * Version réorganisée avec architecture cohérente
 */
class VectorLayerManager extends BaseVectorLayer {
    constructor(map) {
        super(map, 'vector_manager');
        this.layers = new Map();

        console.log('🗺️ Initialisation du VectorLayerManager');
        this.init();
    }

    // === INITIALISATION ===
    async init() {
        try {
            await this.initializeLayers();
            await this.loadAllData();
            this.isReady = true;
            console.log('✅ VectorLayerManager prêt');

            if (window.onVectorLayersReady) {
                window.onVectorLayersReady();
            }
        } catch (error) {
            console.error('❌ Erreur initialisation VectorLayerManager:', error);
        }
    }

    initializeLayers() {
        // Initialiser toutes les couches enfants
        this.layers.set('geography_regions', new GeographyRegionsLayer(this.map));

        console.log(`📋 ${this.layers.size} couches vectorielles initialisées`);
    }

    async loadAllData() {
        console.log('📥 Chargement de toutes les données vectorielles...');

        const loadPromises = [];
        for (const [layerName, layer] of this.layers) {
            loadPromises.push(
                layer.loadData().catch(error => {
                    console.error(`❌ Erreur chargement ${layerName}:`, error);
                    return false;
                })
            );
        }

        await Promise.all(loadPromises);
        console.log('✅ Toutes les données vectorielles chargées');
    }

    refreshLayersForProjection() {
        console.log('🔄 VectorLayerManager: Rafraîchissement des couches pour nouvelle projection');

        if (this.currentLayers.size > 0) {
            const layersArray = Array.from(this.currentLayers);

            // Supprimer et recréer toutes les couches
            this.removeAllLayers();

            setTimeout(() => {
                this.updateVectorLayers(
                    layersArray,
                );
                console.log('✅ Couches vectorielles rafraîchies pour nouvelle projection');
            }, 100);
        }
    }

    // === GESTION DES COUCHES ===
    updateVectorLayers(layers) {
        const currentProj = this.map.getView().getProjection().getCode();
        console.log(`🔄 VectorLayerManager: Mise à jour en projection ${currentProj}`);
        console.log('📋 Paramètres reçus:', {
            layers: layers,
        });

        this.graticuleDensity = graticuleDensity;
        this.labelTypes = new Set(labelTypes || []);

        // Mettre à jour la densité des graticules
        const graticulesLayer = this.layers.get('graticules_all');
        if (graticulesLayer) {
            graticulesLayer.setDensity(graticuleDensity);
        }

        const newLayers = new Set(layers || []);

        console.log('🎯 Couches à afficher:', Array.from(newLayers));

        this.removeAllLayers();

        // Ajouter les nouvelles couches
        for (const layerName of newLayers) {
            this.addVectorLayer(layerName);
        }

        this.currentLayers = newLayers;

        console.log(`✅ Couches vectorielles mises à jour en ${currentProj}`);
        console.log('📊 État final:', {
            currentLayers: Array.from(this.currentLayers),
        });
    }

    addVectorLayer(layerName, regionTypes, marineProperties, graticuleProperties) {
        console.log(`➕ VectorLayerManager: Ajout couche vectorielle: ${layerName}`);

        const layer = this.layers.get(layerName);
        if (!layer) {
            console.error(`❌ Couche ${layerName} non trouvée dans:`, Array.from(this.layers.keys()));
            return;
        }

        console.log(`🔍 Couche ${layerName} trouvée, données chargées:`, !!layer.rawGeoJSON);

        // CRÉER LA COUCHE AVEC LES PROPRIÉTÉS SPÉCIFIQUES
        switch (layerName) {
            case 'geography_regions':
                console.log(`🎯 Création geography_regions avec types:`, regionTypes);
                layer.createLayer(regionTypes);
                break;
            default:
                console.warn(`⚠️ Couche ${layerName} non gérée dans le switch`);
        }

        layer.addToMap();
        console.log(`✅ Couche ${layerName} ajoutée à la carte`);
    }

    removeVectorLayer(layerName) {
        console.log(`➖ VectorLayerManager: Suppression couche vectorielle: ${layerName}`);

        const layer = this.layers.get(layerName);
        if (layer) {
            layer.removeFromMap();
            console.log(`✅ Couche ${layerName} supprimée`);
        }
    }

    removeAllLayers() {
        console.log('🗑️ Suppression de toutes les couches vectorielles');
        for (const [layerName, layer] of this.layers) {
            layer.removeFromMap();
        }
    }

    // === MÉTHODES DE GESTION (SURNOMMES) ===
    activateManager() {
        console.log('🎛️ VectorLayerManager activé');
        // Le manager est toujours "actif", il gère juste les sous-couches
    }

    deactivateManager() {
        console.log('🔴 VectorLayerManager désactivé - suppression de toutes les couches');
        for (const layerName of this.currentLayers) {
            this.removeVectorLayer(layerName);
        }
        this.currentLayers.clear();
    }

    isManagerActive() {
        return this.currentLayers.size > 0;
    }

    // === MÉTHODES UTILITAIRES ===
    getLayer(layerName) {
        return this.layers.get(layerName);
    }

    isLayerVisible(layerName) {
        const layer = this.layers.get(layerName);
        return layer ? layer.isVisible() : false;
    }

    setLayerVisibility(layerName, visible) {
        if (visible) {
            this.currentLayers.add(layerName);
        } else {
            this.currentLayers.delete(layerName);
        }
    }

    getStatus() {
        return {
            isReady: this.isReady,
            activeLayers: Array.from(this.currentLayers),
        };
    }

    // === MÉTHODES HÉRITÉES (IMPLÉMENTATIONS VIDES) ===
    async loadData() {
        console.log('📥 VectorLayerManager: Chargement des données des sous-couches...');
        await this.loadAllData();
        return true;
    }

    createLayer(properties = new Set()) {
        console.log('🏗️ VectorLayerManager: Gestion des sous-couches activée');
    }

    createPolygonStyle(feature, resolution) {
        return null;
    }

    createLabelStyle(feature, resolution) {
        return null;
    }

    classifyFeatureImportance(feature) {
        return 'medium';
    }
}

// Exposer globalement
if (typeof window !== 'undefined') {
    window.VectorLayerManager = VectorLayerManager;
}