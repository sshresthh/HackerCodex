<script context="module">
	export const ssr = false;
</script>

<script lang="ts">
	import { env } from '$env/dynamic/public';
	import mapboxgl from 'mapbox-gl';
	import 'mapbox-gl/dist/mapbox-gl.css';
	import './Map.css';
	import { onMount, onDestroy } from 'svelte';
	import { getSupabaseClient } from '$lib/supabaseClient';
	import CoordinateDisplay from './CoordinateDisplay.svelte';
	import Notification from './Notification.svelte';
	import FloatingUpload from './FloatingUpload.svelte';
	import FloatingList from './FloatingList.svelte';

	let map: mapboxgl.Map;
    let mapContainer: HTMLDivElement;
	const initialState = { lng: 138.5991, lat: -34.9284, zoom:12.93 };
	let lng = initialState.lng;
	let lat = initialState.lat;
	let zoom = initialState.zoom;
    const darkStyleUrl = 'mapbox://styles/andrwong/cmg0l6d2r001e01ps1i8mgeyh';
    let isUploading = false;
    let eventMarker: mapboxgl.Marker | null = null;
    let notice: { message: string; type: 'info' | 'error' | 'success' } = { message: '', type: 'info' };
let originalXHR: typeof XMLHttpRequest;
let originalFetch: typeof fetch;
let originalSendBeacon: typeof navigator.sendBeacon | undefined;

	// GeoJSON source id
	const EVENTS_SOURCE_ID = 'events-source';
	const HEAT_LAYER_ID = 'events-heat';
	const CIRCLE_LAYER_ID = 'events-circle';

	function toFeatureCollection(rows: any[]): GeoJSON.FeatureCollection {
		const features = rows
			.filter((r) => Number.isFinite(r?.lng) && Number.isFinite(r?.lat))
			.map((r) => ({
				type: 'Feature',
				geometry: { type: 'Point', coordinates: [r.lng, r.lat] },
				properties: {
					title: r.title || 'Event',
					location: r.location || '',
					time: r.time || '',
					category: r.category || '',
					id: r.id,
					weight: 1
				}
			}));
		return { type: 'FeatureCollection', features } as GeoJSON.FeatureCollection;
	}

const supabase = getSupabaseClient();
const apiBase = env.PUBLIC_API_URL || '';
let supabaseWarningShown = false;
let lastFetchId = 0;

async function fetchEventsForBounds(): Promise<void> {
	if (!map) return;
	if (!supabase) {
		if (!supabaseWarningShown) {
			supabaseWarningShown = true;
			notice = { message: 'Supabase not configured. Heatmap data unavailable.', type: 'error' };
			setTimeout(() => (notice = { message: '', type: 'info' }), 3000);
			console.warn('Supabase client unavailable. Cannot load events.');
		}
		return;
	}
	const fetchId = ++lastFetchId;
	const b = map.getBounds();
	const swLng = b.getWest();
	const neLng = b.getEast();
	const swLat = b.getSouth();
	const neLat = b.getNorth();
	try {
		const { data, error } = await supabase
			.from('events')
			.select('id,title,location,time,category,lat,lng')
			.gte('lng', swLng)
			.lte('lng', neLng)
			.gte('lat', swLat)
			.lte('lat', neLat)
			.limit(1000);
		if (fetchId !== lastFetchId) return; // stale response
		if (error) throw error;
		const fc = toFeatureCollection(data || []);
		const src = map.getSource(EVENTS_SOURCE_ID) as mapboxgl.GeoJSONSource | undefined;
		if (src) src.setData(fc as any);
	} catch (err) {
		console.error('Failed to load events from Supabase', err);
		notice = { message: 'Could not load events. Check Supabase configuration.', type: 'error' };
		setTimeout(() => (notice = { message: '', type: 'info' }), 3000);
	}
}

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
		return (
			url.includes('events.mapbox.com') ||
			url.includes('analytics.mapbox.com') ||
			url.includes('api.mapbox.com/events')
		);
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

				// Add empty GeoJSON source and layers for heatmap + circles
				if (!map.getSource(EVENTS_SOURCE_ID)) {
					map.addSource(EVENTS_SOURCE_ID, {
						type: 'geojson',
						data: { type: 'FeatureCollection', features: [] }
					});
				}
				if (!map.getLayer(HEAT_LAYER_ID)) {
					map.addLayer({
						id: HEAT_LAYER_ID,
						type: 'heatmap',
						source: EVENTS_SOURCE_ID,
						maxzoom: 16,
						paint: {
							// emphasise density with a neon palette
							'heatmap-weight': ['interpolate', ['linear'], ['get', 'weight'], 0, 0.1, 1, 1],
							'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 0.4, 10, 1.2, 16, 2.0],
							// Minimalist single-hue gradient (transparent → subtle cyan)
							'heatmap-color': [
								'interpolate', ['linear'], ['heatmap-density'],
								0.0, 'rgba(0,0,0,0)',
								0.2, 'rgba(34,211,238,0.15)',
								0.4, 'rgba(34,211,238,0.4)',
								0.7, 'rgba(34,211,238,0.75)',
								1.0, '#22d3ee'
							],
							// Softer radius for cleaner look
							'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 6, 10, 22, 16, 48],
							'heatmap-opacity': ['interpolate', ['linear'], ['zoom'], 8, 0.6, 16, 0.85]
						}
					});
				}
				if (!map.getLayer(CIRCLE_LAYER_ID)) {
					map.addLayer({
						id: CIRCLE_LAYER_ID,
						type: 'circle',
						source: EVENTS_SOURCE_ID,
						minzoom: 11,
						paint: {
							'circle-radius': ['interpolate', ['linear'], ['zoom'], 11, 2, 16, 5],
							'circle-color': '#22d3ee',
							'circle-opacity': 0.8,
							'circle-stroke-width': 0,
							'circle-stroke-color': 'transparent'
						}
					});
				}

				// Load initial events
				fetchEventsForBounds();
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
			map.on('moveend', fetchEventsForBounds);
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
            const apiUrl = env.PUBLIC_API_URL || '';
            const endpoint = `${apiUrl ? apiUrl : ''}/api/process-poster`;
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

