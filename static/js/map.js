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
}

// Export pour utilisation dans d'autres modules
export default MapManager;