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

    const darkStyleUrl = 'mapbox://styles/andrwong/cmg0l6d2r001e01ps1i8mgeyh';
    let isUploading = false;
    let eventMarker: mapboxgl.Marker | null = null;
    let notice: { message: string; type: 'info' | 'error' | 'success' } = { message: '', type: 'info' };
    let originalXHR: typeof XMLHttpRequest;
    let originalFetch: typeof fetch;

    // Dummy events for testing FloatingList + pins
    const dummyEvents = [
        {
            title: "Adelaide Music Festival",
            date: "Sept 30",
            location: "Rymill Park",
            category: "Music",
            lat: -34.921,
            lng: 138.606
        },
        {
            title: "Food & Wine Expo",
            date: "Oct 5",
            location: "Adelaide Convention Centre",
            category: "Food & Drink",
            lat: -34.9205,
            lng: 138.595
        },
        {
            title: "Outdoor Movie Night",
            date: "Oct 10",
            location: "Botanic Gardens",
            category: "Entertainment",
            lat: -34.915,
            lng: 138.610
        },
        {
            title: "Cultural Parade",
            date: "Oct 15",
            location: "King William Street",
            category: "Culture",
            lat: -34.928,
            lng: 138.599
        }
    ];

    // add markers for dummy events
    function addDummyMarkers() {
        dummyEvents.forEach((e) => {
            if (!Number.isFinite(e.lat) || !Number.isFinite(e.lng)) return;

            const popupHtml = `
                <div class="popup">
                    <div class="popup-title">${e.title}</div>
                    <div class="popup-sub">${e.date || ""}</div>
                    <div class="popup-loc">${e.location}</div>
                    <div class="popup-desc">${e.category}</div>
                </div>
            `;

            new mapboxgl.Marker({ color: '#f43f5e' })
                .setLngLat([e.lng, e.lat])
                .setPopup(new mapboxgl.Popup({ offset: 18 }).setHTML(popupHtml))
                .addTo(map);
        });
    }

    onMount(() => {
        if (!mapContainer) return;

        mapboxgl.accessToken = env.PUBLIC_MAPBOX_TOKEN || '';

        // Disable telemetry
        if ('setTelemetryEnabled' in mapboxgl && typeof (mapboxgl as any).setTelemetryEnabled === 'function') {
            (mapboxgl as any).setTelemetryEnabled(false);
        }
        if ('setEventManager' in mapboxgl) {
            (mapboxgl as any).setEventManager(null);
        }

        // block analytics
        const blockAnalytics = (url: string) =>
            url.includes('events.mapbox.com') ||
            url.includes('analytics.mapbox.com') ||
            url.includes('api.mapbox.com/events');

        // Override fetch
        originalFetch = window.fetch;
        window.fetch = function(input, init) {
            const url = typeof input === 'string' ? input : input.toString();
            if (blockAnalytics(url)) {
                return Promise.reject(new Error('Blocked analytics request'));
            }
            return originalFetch.call(this, input, init);
        };

        // Override XMLHttpRequest
        originalXHR = window.XMLHttpRequest;
        window.XMLHttpRequest = class extends originalXHR {
            open(method: string, url: string, async?: boolean, user?: string | null, password?: string | null) {
                if (blockAnalytics(url)) throw new Error('Blocked analytics request');
                return super.open(method, url, async ?? true, user, password);
            }
        };

        if (mapContainer) {
            map = new mapboxgl.Map({
                container: mapContainer,
                style: darkStyleUrl,
                center: [initialState.lng, initialState.lat],
                zoom: initialState.zoom,
                attributionControl: false,
                preserveDrawingBuffer: true,
                antialias: false,
                transformRequest: (url) => {
                    if (blockAnalytics(url)) return { url: '', headers: {} };
                    return { url };
                }
            });
        }

        if (map) {
            map.on('load', () => {
                if ('setTelemetryEnabled' in mapboxgl) {
                    (mapboxgl as any).setTelemetryEnabled(false);
                }
                if ('setEventManager' in map) {
                    (map as any).setEventManager(null);
                }

                // Add dummy event markers
                addDummyMarkers();

                notice = { message: `${dummyEvents.length} dummy events loaded.`, type: 'success' };
                setTimeout(() => (notice = { message: '', type: 'info' }), 3000);
            });

            const update = () => {
                if (!map) return;
                const center = map.getCenter();
                lng = center.lng;
                lat = center.lat;
                zoom = map.getZoom();
            };
            map.on('load', update);
            map.on('move', update);
        }
    });

	onDestroy(() => {
		if (map) map.remove();
		if (originalXHR) window.XMLHttpRequest = originalXHR;
		if (originalFetch) window.fetch = originalFetch;
	});

    async function uploadPoster(file: File) : Promise<void> {
        // keep your existing uploadPoster logic if needed
    }
</script>

<svelte:head>
	<title>Mapster</title>
</svelte:head>

<Notification message={notice.message} type={notice.type} onClose={() => (notice = { message: '', type: 'info' })} />

<div class="map" bind:this={mapContainer}></div>

<CoordinateDisplay {lng} {lat} {zoom} />

<FloatingUpload on:file={(e) => uploadPoster(e.detail)} disabled={isUploading} />

<!-- pass dummy events to FloatingList -->
<FloatingList events={dummyEvents} on:select={(e) => {
    const { lat, lng } = e.detail;
    if (map) {
        map.flyTo({ center: [lng, lat], zoom: 14, essential: true });
    }
}} />
