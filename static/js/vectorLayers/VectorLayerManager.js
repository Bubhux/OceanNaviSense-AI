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
}

// Exposer globalement
if (typeof window !== 'undefined') {
    window.VectorLayerManager = VectorLayerManager;
}