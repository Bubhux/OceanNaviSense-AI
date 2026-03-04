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

    static isValidEPSG4326Tile(z, x, y) {
        // STRUCTURE RÉELLE CONFIRMÉE PAR LES TESTS
        switch (z) {
            case 0:
                return x === 0 && y === 0; // Seul X=0 a des fichiers, X=1 vide
            case 1:
                return (x === 0 || x === 1) && y === 0; // X=0-1 existent, X=2 vide
            case 2:
                return x >= 0 && x <= 3 && y >= 0 && y <= 1; // X=0-3 existent, X=4 vide
            case 3:
                return x >= 0 && x <= 7 && y >= 0 && y <= 3; // X=0-7 existent, X=8 vide
            case 4:
                return x >= 0 && x <= 15 && y >= 0 && y <= 7; // X=0-15 existent, X=16 vide
            case 5:
                return x >= 0 && x <= 31 && y >= 0 && y <= 15; // X=0-31 existent, X=32 vide
            case 6:
                return x >= 0 && x <= 63 && y >= 0 && y <= 31; // X=0-63 existent, X=64 vide
            case 7:
                return x >= 0 && x <= 127 && y >= 0 && y <= 63; // X=0-127 existent, X=128 vide
            case 8:
                return x >= 0 && x <= 255 && y >= 0 && y <= 127; // X=0-255 existent, X=256 vide
            case 9:
                return x >= 0 && x <= 511 && y >= 0 && y <= 255; // X=0-511 existent, X=512 vide
            case 10:
                return x >= 0 && x <= 1023 && y >= 0 && y <= 511; // X=0-1023 existent, X=1024 vide
            default:
                return false;
        }
    }

    static getMaxZoom(projection) {
        if (projection === 'EPSG3857') return 10;
        if (projection === 'EPSG4326') return 10;
        return 0;
    }

    static getEPSG4326Limits(zoomLevel) {
        // STRUCTURE RÉELLE CONFIRMÉE PAR LES TESTS
        const limits = {
            0: { maxX: 0, maxY: 0 },    // Seul X=0 a des fichiers, X=1 vide
            1: { maxX: 1, maxY: 0 },    // X=0-1 existent, X=2 vide
            2: { maxX: 3, maxY: 1 },    // X=0-3 existent, X=4 vide
            3: { maxX: 7, maxY: 3 },    // X=0-7 existent, X=8 vide
            4: { maxX: 15, maxY: 7 },   // X=0-15 existent, X=16 vide
            5: { maxX: 31, maxY: 15 },  // X=0-31 existent, X=32 vide
            6: { maxX: 63, maxY: 31 },  // X=0-63 existent, X=64 vide
            7: { maxX: 127, maxY: 63 }, // X=0-127 existent, X=128 vide
            8: { maxX: 255, maxY: 127 }, // X=0-255 existent, X=256 vide
            9: { maxX: 511, maxY: 255 }, // X=0-511 existent, X=512 vide
            10: { maxX: 1023, maxY: 511 } // X=0-1023 existent, X=1024 vide
        };

        return limits[zoomLevel] || { maxX: 0, maxY: 0 };
    }

    // Méthode pour debug
    static debugStructure() {
        console.log("📊 Structure EPSG4326 validée:");
        console.log("N0: X=0 seulement");
        console.log("N1: X=0-1");
        console.log("N2: X=0-3, Y=0-1");
        console.log("N3: X=0-7, Y=0-3");
        console.log("N4: X=0-15, Y=0-7");
    }
}

// Export par défaut pour la compatibilité
export default TileValidator;