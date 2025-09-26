<script context="module">
    export const ssr = false;
</script>

<script>
    import mapboxgl from 'mapbox-gl';
    import 'mapbox-gl/dist/mapbox-gl.css';
    import { onMount, onDestroy } from 'svelte';

    let map;
    let mapContainer;
    const initialState = { lng: 138.599503, lat: -34.921230, zoom: 11};

    onMount(() => {
        mapboxgl.accessToken = 'pk.eyJ1IjoiYW5kcndvbmciLCJhIjoiY21nMGVoOXFmMDJoeDJqb2s3dG9oZjl3aCJ9.ksR7Z1KCEONNFmVnKX5Uaw';
        map = new mapboxgl.Map({
            container: mapContainer,
            style: 'mapbox://styles/mapbox/navigation-night-v1',
            center: [initialState.lng, initialState.lat],
            zoom: initialState.zoom
        });
    });

    onDestroy(() => {
        if (map) map.remove();
    });

</script>

<div class="map" bind:this={mapContainer}></div>

<style>
    .map {
        position: absolute;
        width: 100%;
        height: 100%;
        inset: 0;
    }
</style>
