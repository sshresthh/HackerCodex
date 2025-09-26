<script context="module">
	export const ssr = false;
</script>

<script lang="ts">
    import { env } from '$env/dynamic/public';
	import mapboxgl from 'mapbox-gl';
	import 'mapbox-gl/dist/mapbox-gl.css';
	import './Map.css';
	import { onMount, onDestroy } from 'svelte';
    import CoordinateDisplay from './CoordinateDisplay.svelte';
    import Notification from './Notification.svelte';
    import FloatingUpload from './FloatingUpload.svelte';
    import FloatingList from './FloatingList.svelte';

    let map: mapboxgl.Map;
    let mapContainer: HTMLDivElement;
	const initialState = { lng: 138.599503, lat: -34.92123, zoom: 11.5 };
	let lng = initialState.lng;
	let lat = initialState.lat;
	let zoom = initialState.zoom;
    let darkMode = true;
    const lightStyleUrl = 'mapbox://styles/andrwong/cmg0m3l32009201rh7v66cr21';
    const darkStyleUrl = 'mapbox://styles/andrwong/cmg0l6d2r001e01ps1i8mgeyh';
    let currentStyleUrl = lightStyleUrl;
    let isUploading = false;
    let eventMarker: mapboxgl.Marker | null = null;
    let notice: { message: string; type: 'info' | 'error' | 'success' } = { message: '', type: 'info' };

    onMount(() => {
        mapboxgl.accessToken = env.PUBLIC_MAPBOX_TOKEN || '';
        
        // Disable Mapbox analytics to prevent CORS errors
        mapboxgl.setRTLTextPlugin('https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-rtl-text/v0.2.3/mapbox-gl-rtl-text.js', null, true);
        
		map = new mapboxgl.Map({
			container: mapContainer,
            style: darkStyleUrl,
			center: [initialState.lng, initialState.lat],
			zoom: initialState.zoom,
            // Disable analytics to prevent CORS errors
            attributionControl: false,
            // Suppress WebGL warnings
            preserveDrawingBuffer: true,
            antialias: false
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
        currentStyleUrl = darkStyleUrl;
	});

    // Always dark theme

	onDestroy(() => {
		if (map) map.remove();
	});

// Minimal UI only

    async function uploadPoster(file: File) : Promise<void> {
        if (!file || !map) return;
        try {
            isUploading = true;
            const form = new FormData();
            form.append('file', file);
            // Use relative path for production, absolute for development
            const apiUrl = env.PUBLIC_API_URL || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://127.0.0.1:8000' : '');
            const endpoint = apiUrl ? `${apiUrl}/api/process-poster` : '/api/process-poster';
            const res = await fetch(endpoint, {
                method: 'POST',
                body: form
            });
            if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
            const data = await res.json();

            const latNum = parseFloat(String(data?.Latitude ?? ''));
            const lngNum = parseFloat(String(data?.Longitude ?? ''));

            if (Number.isFinite(latNum) && Number.isFinite(lngNum)) {
                // Remove previous marker if any
                if (eventMarker) {
                    eventMarker.remove();
                }

                const popupHtml = `
                    <div class="popup">
                        <div class="popup-title">${data?.Title || 'Event'}</div>
                        <div class="popup-sub">${data?.Date || ''} ${data?.Time || ''}</div>
                        <div class="popup-loc">${data?.Location || ''}</div>
                        <div class="popup-desc">${(data?.Description || '').slice(0, 120)}</div>
                    </div>
                `;

                const popup = new mapboxgl.Popup({ offset: 18 }).setHTML(popupHtml);
                eventMarker = new mapboxgl.Marker({ color: '#2563eb' })
                    .setLngLat([lngNum, latNum])
                    .setPopup(popup)
                    .addTo(map);

                map.flyTo({ center: [lngNum, latNum], zoom: 14, essential: true });
                popup.addTo(map);
                notice = { message: 'Event pinned on the map.', type: 'success' };
                setTimeout(() => (notice = { message: '', type: 'info' }), 2500);
            } else {
                notice = { message: 'Could not determine coordinates. Check Google Geocoding API setup.', type: 'error' };
            }
        } catch (err) {
            console.error(err);
            notice = { message: 'Upload failed. Please try again.', type: 'error' };
        } finally {
            isUploading = false;
        }
    }
</script>

<svelte:head>
	<title>Mapster</title>
	<script src="https://kit.fontawesome.com/2df6b0f25d.js" crossorigin="anonymous"></script>
</svelte:head>

<Notification message={notice.message} type={notice.type} onClose={() => (notice = { message: '', type: 'info' })} />

<div class="map" bind:this={mapContainer}></div>

<CoordinateDisplay {lng} {lat} {zoom} />

<FloatingUpload on:file={(e) => uploadPoster(e.detail)} disabled={isUploading} />
<FloatingList on:open={() => (notice = { message: 'List coming soon.', type: 'info' })} />

