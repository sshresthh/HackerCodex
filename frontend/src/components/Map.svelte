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

    onMount(() => {
        if (!mapContainer) return;

        mapboxgl.accessToken = env.PUBLIC_MAPBOX_TOKEN || '';

        // Completely disable Mapbox analytics and telemetry to prevent CORS errors
        if ('setTelemetryEnabled' in mapboxgl && typeof (mapboxgl as any).setTelemetryEnabled === 'function') {
            (mapboxgl as any).setTelemetryEnabled(false);
        }
        
        // Disable events completely
        if ('setEventManager' in mapboxgl) {
            (mapboxgl as any).setEventManager(null);
        }

        // Block all network requests to Mapbox analytics
        const blockAnalytics = (url: string) => {
            return url.includes('events.mapbox.com') ||
                   url.includes('analytics.mapbox.com') ||
                   url.includes('api.mapbox.com/events');
        };

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
                if (blockAnalytics(url)) {
                    throw new Error('Blocked analytics request');
                }
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
                // Block all analytics requests
                transformRequest: (url, resourceType) => {
                    if (blockAnalytics(url)) {
                        return { url: '', headers: {} };
                    }
                    return { url };
                }
            });
        }

        if (map) {
            // Disable telemetry after map creation
            map.on('load', () => {
                if ('setTelemetryEnabled' in mapboxgl) {
                    (mapboxgl as any).setTelemetryEnabled(false);
                }
                // Disable events on the map instance
                if (map && 'setEventManager' in map) {
                    (map as any).setEventManager(null);
                }
            });

            // Keep displayed coordinates/zoom in sync with the map
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
		// Restore original functions
		if (originalXHR) {
			window.XMLHttpRequest = originalXHR;
		}
		if (originalFetch) {
			window.fetch = originalFetch;
		}
	});

    async function uploadPoster(file: File) : Promise<void> {
        if (!file || !map) return;
        try {
            isUploading = true;
            const form = new FormData();
            form.append('file', file);
            // Use relative path for production, absolute for development
            const apiUrl = env.PUBLIC_API_URL || (
                typeof window !== 'undefined' && ['localhost', '0.0.0.0'].includes(window.location.hostname)
                    ? 'http://0.0.0.0:8000'
                    : ''
            );
            const endpoint = apiUrl ? `${apiUrl}/api/process-poster` : '/api/process-poster';
            const res = await fetch(endpoint, {
                method: 'POST',
                body: form
            });
            if (!res.ok) {
                const detail = await res.text();
                throw new Error(`Upload failed: ${res.status} ${detail}`);
            }
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

                if (map) {
                    map.flyTo({ center: [lngNum, latNum], zoom: 14, essential: true });
                    popup.addTo(map);
                }
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
</svelte:head>

<Notification message={notice.message} type={notice.type} onClose={() => (notice = { message: '', type: 'info' })} />

<div class="map" bind:this={mapContainer}></div>

<CoordinateDisplay {lng} {lat} {zoom} />

<FloatingUpload on:file={(e) => uploadPoster(e.detail)} disabled={isUploading} />
<FloatingList on:open={() => (notice = { message: 'List coming soon.', type: 'info' })} />

