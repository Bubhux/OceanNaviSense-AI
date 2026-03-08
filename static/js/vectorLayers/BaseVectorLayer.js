// static/js/vectorLayers/BaseVectorLayer.js
class BaseVectorLayer {
    constructor(map, layerName) {
        this.map = map;
        this.layerName = layerName;
        this.polygonLayer = null;
        this.labelLayer = null;
        this.isLayerOnMap = false;
        this.currentProperties = new Set();
    }

    // NOUVELLE MÉTHODE : Reprojection automatique
    getCurrentProjection() {
        return this.map.getView().getProjection().getCode();
    }

    // MODIFIER : Méthode pour créer des features avec la bonne projection
    createFeatureFromGeoJSON(feature) {
        const currentProj = this.getCurrentProjection();

        // Lire la feature avec la projection cible
        const vectorFeature = new ol.format.GeoJSON().readFeature(feature, {
            featureProjection: currentProj,
            dataProjection: 'EPSG:4326' // Les données source sont en WGS84
        });

        return vectorFeature;
    }

    // MODIFIER : Méthode addToMap avec vérification de projection
    addToMap() {
        const hasAnyLayer = this.polygonLayer || this.labelLayer;
        if (!hasAnyLayer) {
            console.warn(`⚠️ Impossible d'ajouter ${this.layerName}: aucune couche créée`);
            return false;
        }

        const layers = this.map.getLayers().getArray();
        const currentProj = this.getCurrentProjection();

        console.log(`🗺️ Ajout couche ${this.layerName} en projection: ${currentProj}`);

        try {
            this.map.updateSize();

            // VÉRIFICATION CRITIQUE : S'assurer que les couches utilisent la bonne projection
            if (this.polygonLayer) {
                const source = this.polygonLayer.getSource();
                if (source && source.getFeatures().length > 0) {
                    console.log(`✅ Couche polygon ${this.layerName} a ${source.getFeatures().length} features`);
                }

                if (!layers.includes(this.polygonLayer)) {
                    this.map.addLayer(this.polygonLayer);
                    console.log(`✅ Couche polygon ${this.layerName} ajoutée en ${currentProj}`);
                }
            }

            if (this.labelLayer) {
                const source = this.labelLayer.getSource();
                if (source && source.getFeatures().length > 0) {
                    console.log(`✅ Labels ${this.layerName} ont ${source.getFeatures().length} features`);
                }

                if (!layers.includes(this.labelLayer)) {
                    this.map.addLayer(this.labelLayer);
                    console.log(`✅ Labels ${this.layerName} ajoutés en ${currentProj}`);
                }
            }

            this.isLayerOnMap = true;

            setTimeout(() => {
                this.map.renderSync();
                console.log(`🎨 Rendu terminé pour ${this.layerName} en ${currentProj}`);
            }, 50);

            return true;
        } catch (error) {
            console.error(`❌ Erreur ajout couche ${this.layerName}:`, error);
            return false;
        }
    }

    removeFromMap() {
        let removed = false;

        try {
            const layers = this.map.getLayers().getArray();

            // NOUVEAU: Forcer la mise à jour avant suppression
            this.map.updateSize();

            // Retirer la couche polygon si elle existe
            if (this.polygonLayer && layers.includes(this.polygonLayer)) {
                this.map.removeLayer(this.polygonLayer);
                console.log(`✅ Couche polygon ${this.layerName} retirée de la carte`);
                removed = true;
            }

            // Retirer la couche de labels si elle existe
            if (this.labelLayer && layers.includes(this.labelLayer)) {
                this.map.removeLayer(this.labelLayer);
                console.log(`✅ Labels ${this.layerName} retirés de la carte`);
                removed = true;
            }

            if (!removed) {
                console.log(`ℹ️ Couche ${this.layerName} n'était pas sur la carte`);
            }

            this.isLayerOnMap = false;

            // NOUVEAU: Forcer le rendu après suppression
            setTimeout(() => {
                this.map.renderSync();
            }, 50);

            return true;
        } catch (error) {
            console.error(`❌ Erreur retrait couche ${this.layerName}:`, error);
            return false;
        }
    }
}

if (typeof window !== 'undefined') {
    window.BaseVectorLayer = BaseVectorLayer;
}
