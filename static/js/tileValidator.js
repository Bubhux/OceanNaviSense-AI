// static/js/tileValidator.js
export class TileValidator {
    static isValidTile(projection, z, x, y) {
        if (projection === 'EPSG3857') {
            const max = Math.pow(2, z) - 1;
            return x >= 0 && x <= max && y >= 0 && y <= max;
        } else if (projection === 'EPSG4326') {
            return this.isValidEPSG4326Tile(z, x, y);
        }
        return false;
    }
}

// Export par défaut pour la compatibilité
export default TileValidator;