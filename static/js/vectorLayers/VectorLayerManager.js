// static/js/vectorLayers/VectorLayerManager.js
/**
 * Gestionnaire principal des couches vectorielles
 * Version réorganisée avec architecture cohérente
 */
class VectorLayerManager extends BaseVectorLayer {

}

// Exposer globalement
if (typeof window !== 'undefined') {
    window.VectorLayerManager = VectorLayerManager;
}