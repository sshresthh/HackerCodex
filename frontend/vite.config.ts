import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		proxy: {
			'/api': 'http://localhost:8000'
		}
	},
	build: {
		sourcemap: false, // Disable source maps to prevent 404 errors
		rollupOptions: {
			output: {
				// Suppress WebGL warnings in production
				intro: `
                    // Suppress WebGL warnings
                    const originalConsoleWarn = console.warn;
                    console.warn = function(...args) {
                        if (args[0] && typeof args[0] === 'string') {
                            if (args[0].includes('WEBGL_debug_renderer_info') || 
                                args[0].includes('texSubImage') ||
                                args[0].includes('Alpha-premult') ||
                                args[0].includes('y-flip')) {
                                return;
                            }
                        }
                        originalConsoleWarn.apply(console, args);
                    };
                `
			}
		}
	}
});
