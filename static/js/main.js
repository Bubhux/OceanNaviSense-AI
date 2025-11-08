// static/js/main.js
// Imports OpenLayers directs
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import TileLayer from 'ol/layer/Tile.js';
import VectorLayer from 'ol/layer/Vector.js';
import XYZ from 'ol/source/XYZ.js';
import OSM from 'ol/source/OSM.js';
import VectorSource from 'ol/source/Vector.js';
import TileImage from 'ol/source/TileImage.js';
import TileGrid from 'ol/tilegrid/TileGrid.js';
import ScaleLine from 'ol/control/ScaleLine.js';
import ZoomToExtent from 'ol/control/ZoomToExtent.js';
import FullScreen from 'ol/control/FullScreen.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import Feature from 'ol/Feature.js';
import Point from 'ol/geom/Point.js';

import { Style, Fill, Stroke, Text, Circle } from 'ol/style.js';
import { fromLonLat, toLonLat, transformExtent } from 'ol/proj.js';
import { containsCoordinate, getCenter } from 'ol/extent.js';
import { defaults as defaultControls } from 'ol/control.js';

// Exposer globalement pour compatibilité
window.ol = {
    Map,
    View,
    layer: {
        Tile: TileLayer,
        Vector: VectorLayer
    },
    source: {
        XYZ,
        OSM,
        Vector: VectorSource,
        TileImage // ⚠️ AJOUTEZ CECI AUSSI
    },
    tilegrid: {
        TileGrid
    },
    control: {
        ScaleLine,
        ZoomToExtent,
        FullScreen,
        defaults: defaultControls
    },
    proj: {
        fromLonLat,
        toLonLat,
        transformExtent
    },
    extent: {
        containsCoordinate,
        getCenter
    },
    format: {
        GeoJSON
    },
    Feature,
    geom: {
        Point
    },
    style: {
        Style,
        Fill,
        Stroke,
        Text,
        Circle
    }
};

console.log('✅ OpenLayers chargé globalement');

// Maintenant importer vos autres fichiers
import './utils.js';
import './tileValidator.js';
import './map.js';
import './app.js';
import './vectorLayers/BaseVectorLayer.js';
import './vectorLayers/GeographyRegionsLayer.js';
import './vectorLayers/VectorLayerManager.js';
import './debug.js';

console.log('🚀 Application chargée avec Vite + OpenLayers local');