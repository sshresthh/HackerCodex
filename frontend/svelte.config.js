import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://svelte.dev/docs/kit/integrations
	// for more information about preprocessors
	preprocess: vitePreprocess(),

	kit: {
		adapter: adapter({
			pages: 'public', // Change output directory to 'public'
			fallback: 'index.html' // enable SPA mode
		}),
		prerender: {
			entries: ['*'] // prerender all routes
		}
	},
	compilerOptions: {
		generate: 'dom',
		dev: true
	}
};

export default config;
