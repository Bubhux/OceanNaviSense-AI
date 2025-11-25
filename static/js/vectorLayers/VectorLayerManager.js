// static/js/vectorLayers/VectorLayerManager.js
/**
 * Gestionnaire principal des couches vectorielles
 * Version réorganisée avec architecture cohérente
 */
class VectorLayerManager extends BaseVectorLayer {
    constructor(map) {
        super(map, 'vector_manager');
        this.layers = new Map();
        this.currentLayers = new Set();
        this.regionTypes = new Set();
        this.marineProperties = new Set();
        this.graticuleProperties = new Set();
        this.labelTypes = new Set();
        this.graticuleDensity = 'auto';
        this.isReady = false;

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
                    regionTypesArray,
                    marineArray,
                    graticuleArray,
                    this.graticuleDensity,
                    labelTypesArray
                );
                console.log('✅ Couches vectorielles rafraîchies pour nouvelle projection');
            }, 100);
        }
    }

    // === GESTION DES COUCHES ===
    updateVectorLayers(layers, regionTypes) {
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
        const newRegionTypes = new Set(regionTypes || []);
        const newMarineProperties = new Set(marineProperties || []);
        const newGraticuleProperties = new Set(graticuleProperties || []);

        console.log('🎯 Couches à afficher:', Array.from(newLayers));

        this.removeAllLayers();

        // Ajouter les nouvelles couches
        for (const layerName of newLayers) {
            this.addVectorLayer(layerName, newRegionTypes, newMarineProperties, newGraticuleProperties);
        }

        this.currentLayers = newLayers;

        console.log(`✅ Couches vectorielles mises à jour en ${currentProj}`);
        console.log('📊 État final:', {
            currentLayers: Array.from(this.currentLayers),
        });
    }
}

// Exposer globalement
if (typeof window !== 'undefined') {
    window.VectorLayerManager = VectorLayerManager;
}