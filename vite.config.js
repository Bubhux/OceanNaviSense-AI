// vite.config.js
import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
    build: {
        rollupOptions: {
            input: resolve(__dirname, 'static/js/main.js'),
            output: {
                dir: resolve(__dirname, 'static/dist'),
                entryFileNames: 'main.js',
                format: 'es',
                globals: {
                    'ol': 'ol'
                }
            },
            external: ['ol']
        },
        outDir: resolve(__dirname, 'static/dist'),
        sourcemap: true
    },
    server: {
        port: 3000
    },
    resolve: {
        alias: {
            '@': resolve(__dirname, 'static/js'),
            'ol': resolve(__dirname, 'node_modules/ol')
        }
    },
    optimizeDeps: {
        include: ['ol']
    }
})
