<script context="module">
	export const ssr = false;
</script>

<script>
	import mapboxgl from 'mapbox-gl';
	import 'mapbox-gl/dist/mapbox-gl.css';
	import { onMount, onDestroy } from 'svelte';

	let map;
	let mapContainer;
	const initialState = { lng: 138.599503, lat: -34.92123, zoom: 11 };
	let lng = initialState.lng;
	let lat = initialState.lat;
	let zoom = initialState.zoom;

	onMount(() => {
		mapboxgl.accessToken =
			'pk.eyJ1IjoiYW5kcndvbmciLCJhIjoiY21nMGVoOXFmMDJoeDJqb2s3dG9oZjl3aCJ9.ksR7Z1KCEONNFmVnKX5Uaw';
		map = new mapboxgl.Map({
			container: mapContainer,
			style: 'mapbox://styles/mapbox/navigation-night-v1',
			center: [initialState.lng, initialState.lat],
			zoom: initialState.zoom
		});

		// Keep displayed coordinates/zoom in sync with the map
		const update = () => {
			const center = map.getCenter();
			lng = center.lng;
			lat = center.lat;
			zoom = map.getZoom();
		};
		map.on('load', update);
		map.on('move', update);
	});

	onDestroy(() => {
		if (map) map.remove();
	});

	function handleReset() {
		map.flyTo({
			center: [initialState.lng, initialState.lat],
			zoom: initialState.zoom,
			essential: true
		});
	}
</script>

<div class="map" bind:this={mapContainer}></div>

<div class="sidebar">
	Longitude: {lng.toFixed(4)} | Latitude: {lat.toFixed(4)} | Zoom:
	{zoom.toFixed(2)}
</div>

<button onclick={handleReset} class="reset-button">Reset</button>

<style>
	.map {
		position: absolute;
		width: 100%;
		height: 100%;
		inset: 0;
	}
	.sidebar {
		background-color: rgb(35 55 75 / 90%);
		color: #fff;
		padding: 6px 12px;
		font-family: monospace;
		z-index: 1;
		position: absolute;
		top: 0;
		left: 0;
		margin: 12px;
		border-radius: 4px;
	}

	.reset-button {
		position: absolute;
		top: 50px;
		z-index: 1;
		left: 12px;
		padding: 4px 10px;
		border-radius: 10px;
		cursor: pointer;
	}
</style>
