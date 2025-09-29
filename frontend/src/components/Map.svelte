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
import FabMenu from './FabMenu.svelte';
import LoadingOverlay from './LoadingOverlay.svelte';
import EventSidebar from './EventSidebar.svelte';
import SearchPanel from './SearchPanel.svelte';

	let map: mapboxgl.Map;
    let mapContainer: HTMLDivElement;
	const initialState = { lng: 138.5991, lat: -34.9284, zoom:12.93 };
	let lng = initialState.lng;
	let lat = initialState.lat;
	let zoom = initialState.zoom;
    const darkStyleUrl = 'mapbox://styles/andrwong/cmg0l6d2r001e01ps1i8mgeyh';
    const lightStyleUrl = 'mapbox://styles/andrwong/cmg0m3l32009201rh7v66cr21';
    let theme: 'dark' | 'light' = 'light';
    let isUploading = false;
    let eventMarker: mapboxgl.Marker | null = null;
    let currentPopup: mapboxgl.Popup | null = null;
    let searchOpen = false;
    let notice: { message: string; type: 'info' | 'error' | 'success' } = { message: '', type: 'info' };
let originalXHR: typeof XMLHttpRequest;
let originalFetch: typeof fetch;
let originalSendBeacon: typeof navigator.sendBeacon | undefined;

	// GeoJSON source id
	const EVENTS_SOURCE_ID = 'events-source';
	const HEAT_LAYER_ID = 'events-heat';
const PIN_LAYER_ID = 'events-pin';
const HIGHLIGHT_SOURCE_ID = 'highlight-source';
const HIGHLIGHT_LAYER_ID = 'highlight-circles';

	type LayerMode = 'normal' | 'heat' | 'pins';
    let layerMode: LayerMode = 'pins';

	function setLayerVisibility(mode: LayerMode) {
    if (!map) return;
    const heatVis = mode === 'heat' ? 'visible' : 'none';
    const pinVis = mode === 'pins' ? 'visible' : 'none';
    if (map.getLayer(HEAT_LAYER_ID)) map.setLayoutProperty(HEAT_LAYER_ID, 'visibility', heatVis);
    if (map.getLayer(PIN_LAYER_ID)) map.setLayoutProperty(PIN_LAYER_ID, 'visibility', pinVis);
}

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
					date: r.date || '',
					description: r.description || '',
					url: r.link || '',
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
	const b = map!.getBounds() as mapboxgl.LngLatBounds;
	const swLng = b.getWest()!;
	const neLng = b.getEast()!;
	const swLat = b.getSouth()!;
	const neLat = b.getNorth()!;
	try {
		const { data, error } = await supabase
			.from('events')
			.select('id,title,location,date,time,category,lat,lng,description,link')
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

    function drawPinToCanvas(size: number, themeNow: 'dark' | 'light', baseColor?: string) {
        const canvas = document.createElement('canvas');
        const pr = 2;
        canvas.width = size * pr;
        canvas.height = size * pr;
        const ctx = canvas.getContext('2d');
        if (!ctx) return { canvas, imageData: null as ImageData | null };
        ctx.scale(pr, pr);
        const w = size, h = size; // square canvas, pin centered
        const cx = w / 2;
        const cy = h * 0.38;
        const r = h * 0.22;
        const tipY = h * 0.78;

        const primary = baseColor || (themeNow === 'dark' ? '#67e8f9' : '#2563eb'); // high-contrast to background
        const top = themeNow === 'dark' ? '#e0f2fe' : '#c7d2fe';
        const bottom = themeNow === 'dark' ? '#0b1220' : '#1f2937';

        // minimalist circle pin
        ctx.beginPath();
        ctx.arc(cx, cy, r * 0.7, 0, Math.PI * 2);
        ctx.fillStyle = primary;
        ctx.fill();
        // subtle white outline for visibility
        ctx.lineWidth = 2;
        ctx.strokeStyle = themeNow === 'dark' ? '#0f172a' : '#ffffff';
        ctx.stroke();

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        return { canvas, imageData };
    }

    function addEventPinImage() {
        if (!map) return;
        const id = 'event-pin';
        if (map.hasImage(id)) map.removeImage(id);
        const { imageData } = drawPinToCanvas(64, theme);
        if (imageData) map.addImage(id, imageData, { pixelRatio: 2 });
    }

    function getPosterPinDataURL() {
        // Larger, same scheme, to emphasize uploaded poster pin
        const { canvas } = drawPinToCanvas(88, theme);
        return canvas.toDataURL('image/png');
    }

    onMount(() => {
        if (!mapContainer) return;

        mapboxgl.accessToken = env.PUBLIC_MAPBOX_TOKEN || '';

        // Completely disable Mapbox analytics and telemetry to prevent CORS errors
        if ('setTelemetryEnabled' in mapboxgl && typeof (mapboxgl as any).setTelemetryEnabled === 'function') {
            (mapboxgl as any).setTelemetryEnabled(false);
        }
        
        // (events remain enabled to allow popups on pin click)

        // Block all network requests to Mapbox analytics
	const blockAnalytics = (url: string) => {
		return (
			url.includes('events.mapbox.com') ||
			url.includes('analytics.mapbox.com') ||
			url.includes('api.mapbox.com/events')
		);
	};

        // Override fetch
        originalFetch = window.fetch.bind(window) as typeof fetch;
        window.fetch = (input: RequestInfo | URL, init?: RequestInit) => {
            const url = typeof input === 'string' ? input : input.toString();
            if (blockAnalytics(url)) {
                return Promise.reject(new Error('Blocked analytics request'));
            }
            return originalFetch(input as any, init as any);
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
        
        // Override navigator.sendBeacon
        originalSendBeacon = navigator.sendBeacon;
        navigator.sendBeacon = function(url: string | URL, data?: BodyInit): boolean {
            if (blockAnalytics(typeof url === 'string' ? url : url.toString())) {
                return false;
            }
            return originalSendBeacon ? (originalSendBeacon as any).call(navigator, url, data) : false;
        } as any;

        if (mapContainer) {
map = new mapboxgl.Map({
                container: mapContainer,
                style: theme === 'dark' ? darkStyleUrl : lightStyleUrl,
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
                // (events remain enabled to allow popups on pin click)

// Add empty GeoJSON source and layers for heatmap + circles + highlight
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
							// Aurora gradient tuned for the dark basemap
							'heatmap-weight': ['interpolate', ['linear'], ['get', 'weight'], 0, 0.15, 1, 1],
'heatmap-color': [
								'interpolate', ['linear'], ['heatmap-density'],
								0.00, 'rgba(0,0,0,0)',
								0.15, 'rgba(0,255,220,0.18)',   /* neon aqua */
								0.35, 'rgba(34,211,238,0.55)',   /* cyan */
								0.60, 'rgba(168,85,247,0.80)',    /* violet */
								0.85, 'rgba(244,63,94,0.90)',     /* neon pink/red */
								1.00, '#f43f5e'
							],
							// Stronger neon glow
							'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 8, 10, 28, 16, 56],
							'heatmap-opacity': ['interpolate', ['linear'], ['zoom'], 8, 0.7, 16, 0.95],
							'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 0.5, 10, 1.3, 16, 2.2]
						}
					});
				}
                // Pin symbol layer
                addEventPinImage();
                if (!map.getLayer(PIN_LAYER_ID)) {
                    map.addLayer({
                        id: PIN_LAYER_ID,
                        type: 'symbol',
                        source: EVENTS_SOURCE_ID,
                        minzoom: 11,
                        layout: {
                            'icon-image': 'event-pin',
'icon-size': ['interpolate', ['linear'], ['zoom'], 11, 0.35, 14, 0.45, 17, 0.55],
                            'icon-allow-overlap': true,
                            'icon-anchor': 'bottom'
                        }
                    });
                }

				// Load initial events and set initial visibility
				fetchEventsForBounds();
                setLayerVisibility(layerMode);

                // Pin click popup
                map.on('click', PIN_LAYER_ID, (ev) => {
                    const f = ev.features?.[0];
                    if (!f) return;
                    const p = f.properties as any;
                    const title = p.title || 'Event';
                    const loc = p.location || '';
                    const dateStr = p.date || '';
                    const time = p.time || '';
                    const url = p.url || '';
                    const desc = p.description || '';
                    const linkHtml = url ? `<a href="${url}" target="_blank" rel="noopener" class="popup-link">Visit website →</a>` : '';
                    const popupHtml = `
                        <div class="popup">
                          <div class="popup-title">${title}</div>
                          <div class="popup-sub">${dateStr} ${time}</div>
                          <div class="popup-loc">${loc}</div>
                          ${desc ? `<div class="popup-desc">${desc}</div>` : ''}
                          ${linkHtml}
                        </div>`;
                    if (currentPopup) currentPopup.remove();
                    currentPopup = new mapboxgl.Popup({ offset: 18 })
                      .setLngLat((f.geometry as any).coordinates)
                      .setHTML(popupHtml)
                      .addTo(map);
                });

                // Change cursor to pointer on hover
                map.on('mouseenter', PIN_LAYER_ID, () => map.getCanvas().style.cursor = 'pointer');
                map.on('mouseleave', PIN_LAYER_ID, () => map.getCanvas().style.cursor = '');

                // Highlight source/layer for search/chat results
                if (!map.getSource(HIGHLIGHT_SOURCE_ID)) {
                    map.addSource(HIGHLIGHT_SOURCE_ID, { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
                }
                if (!map.getLayer(HIGHLIGHT_LAYER_ID)) {
                    map.addLayer({
                        id: HIGHLIGHT_LAYER_ID,
                        type: 'circle',
                        source: HIGHLIGHT_SOURCE_ID,
                        paint: {
                            'circle-radius': ['interpolate', ['linear'], ['zoom'], 11, 4, 14, 8, 17, 12],
                            'circle-color': '#ffffff',
                            'circle-opacity': 0.95,
                            'circle-stroke-width': 2,
                            'circle-stroke-color': '#38bdf8'
                        }
                    });
                }
            });

            // Re-create layers when style changes (e.g., theme toggle)
            map.on('style.load', () => {
                // Add sources
                if (!map.getSource(EVENTS_SOURCE_ID)) {
                    map.addSource(EVENTS_SOURCE_ID, { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
                }
                // Heat layer (theme-specific)
                if (!map.getLayer(HEAT_LAYER_ID)) {
                    map.addLayer({
                        id: HEAT_LAYER_ID,
                        type: 'heatmap',
                        source: EVENTS_SOURCE_ID,
                        maxzoom: 16,
                        paint: theme === 'dark' ? {
                            'heatmap-weight': ['interpolate', ['linear'], ['get', 'weight'], 0, 0.2, 1, 1],
                            'heatmap-color': [
                                'interpolate', ['linear'], ['heatmap-density'],
                                0.00, 'rgba(0,0,0,0)',
                                0.15, 'rgba(0,255,220,0.18)',
                                0.35, 'rgba(34,211,238,0.55)',
                                0.60, 'rgba(168,85,247,0.80)',
                                0.85, 'rgba(244,63,94,0.90)',
                                1.00, '#f43f5e'
                            ],
                            'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 8, 10, 28, 16, 56],
                            'heatmap-opacity': ['interpolate', ['linear'], ['zoom'], 8, 0.7, 16, 0.95],
                            'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 0.5, 10, 1.3, 16, 2.2]
                        } : {
                            // Light theme
                            'heatmap-weight': ['interpolate', ['linear'], ['get', 'weight'], 0, 0.2, 1, 1],
                            'heatmap-color': [
                                'interpolate', ['linear'], ['heatmap-density'],
                                0.00, 'rgba(0,0,0,0)',
                                0.2, 'rgba(14,165,233,0.25)',
                                0.4, 'rgba(2,132,199,0.5)',
                                0.7, 'rgba(59,130,246,0.85)',
                                1.0, '#0ea5e9'
                            ],
                            'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 6, 10, 24, 16, 48],
                            'heatmap-opacity': ['interpolate', ['linear'], ['zoom'], 8, 0.6, 16, 0.9]
                        }
                    });
                }
                // Pin symbol layer (re-add after style change)
                addEventPinImage();
                if (!map.getLayer(PIN_LAYER_ID)) {
                    map.addLayer({
                        id: PIN_LAYER_ID,
                        type: 'symbol',
                        source: EVENTS_SOURCE_ID,
                        minzoom: 11,
                        layout: {
                            'icon-image': 'event-pin',
'icon-size': ['interpolate', ['linear'], ['zoom'], 11, 0.35, 14, 0.45, 17, 0.55],
                            'icon-allow-overlap': true,
                            'icon-anchor': 'bottom'
                        }
                    });
                }
                // Highlight source/layer
                if (!map.getSource(HIGHLIGHT_SOURCE_ID)) {
                    map.addSource(HIGHLIGHT_SOURCE_ID, { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
                }
                if (!map.getLayer(HIGHLIGHT_LAYER_ID)) {
                    map.addLayer({
                        id: HIGHLIGHT_LAYER_ID,
                        type: 'circle',
                        source: HIGHLIGHT_SOURCE_ID,
                        paint: theme === 'dark' ? {
                            'circle-radius': ['interpolate', ['linear'], ['zoom'], 11, 4, 14, 8, 17, 12],
                            'circle-color': '#ffffff',
                            'circle-opacity': 0.95,
                            'circle-stroke-width': 2,
                            'circle-stroke-color': '#38bdf8'
                        } : {
                            'circle-radius': ['interpolate', ['linear'], ['zoom'], 11, 4, 14, 8, 17, 12],
                            'circle-color': '#0ea5e9',
                            'circle-opacity': 0.9,
                            'circle-stroke-width': 2,
                            'circle-stroke-color': '#0369a1'
                        }
                    });
                }

                setLayerVisibility(layerMode);
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
            const apiUrlRaw = env.PUBLIC_API_URL || '';
            const apiUrl = apiUrlRaw && !/^https?:\/\//i.test(apiUrlRaw) ? `https://${apiUrlRaw}` : apiUrlRaw;
            const endpoint = `${apiUrl ? apiUrl.replace(/\/$/, '') : ''}/api/process-poster`;
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

                const link = data?.URL ? `<a href="${data.URL}" target="_blank" rel="noopener" class="popup-link">Open link</a>` : '';
                const popupHtml = `
                    <div class="popup">
                        <div class="popup-title">${data?.Title || 'Event'}</div>
                        <div class="popup-sub">${data?.Date || ''} ${data?.Time || ''}</div>
                        <div class="popup-loc">${data?.Location || ''}</div>
                        <div class="popup-desc">${(data?.Description || '').slice(0, 120)}</div>
                        ${link}
                    </div>
                `;

                const popup = new mapboxgl.Popup({ offset: 18 }).setHTML(popupHtml);
                const el = document.createElement('img');
                el.src = getPosterPinDataURL();
                el.style.width = '64px';
                el.style.height = '64px';
                el.style.transform = 'translateY(6px)';
                eventMarker = new mapboxgl.Marker({ element: el, anchor: 'bottom' })
                    .setLngLat([lngNum, latNum])
                    .setPopup(popup)
                    .addTo(map);

                if (map) {
                    map.flyTo({ center: [lngNum, latNum], zoom: 15, essential: true });

                    // Refresh layers so the new event stored in Supabase appears in heatmap/pins for future sessions
                    fetchEventsForBounds();
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

function focusOnItems(items: any[]) {
    if (!map || !items || !items.length) return;
    const feats = items
      .filter((r) => Number.isFinite(r?.lng) && Number.isFinite(r?.lat))
      .map((r) => ({
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [r.lng, r.lat] },
        properties: { title: r.title || 'Event' }
      }));
    const fc = { type: 'FeatureCollection', features: feats } as any;
    const src = map.getSource(HIGHLIGHT_SOURCE_ID) as mapboxgl.GeoJSONSource | undefined;
    if (src) src.setData(fc);

    if (feats.length === 1) {
      const [lng, lat] = (feats[0].geometry as any).coordinates;
      map.flyTo({ center: [lng, lat], zoom: Math.max(map.getZoom(), 14), essential: true });

      // Show popup after fly completes to avoid flicker
      const ev = items[0];
      if (ev) {
        const showPopup = () => {
          const title = ev.title || 'Event';
          const loc = ev.location || '';
          const dateStr = ev.date || '';
          const time = ev.time || '';
          const desc = ev.description || '';
          const url = ev.link || '';
          const linkHtml = url ? `<a href="${url}" target="_blank" rel="noopener" class="popup-link">Visit website →</a>` : '';
          const popupHtml = `
            <div class="popup">
              <div class="popup-title">${title}</div>
              <div class="popup-sub">${dateStr} ${time}</div>
              <div class="popup-loc">${loc}</div>
              ${desc ? `<div class="popup-desc">${desc}</div>` : ''}
              ${linkHtml}
            </div>`;
          if (currentPopup) currentPopup.remove();
          currentPopup = new mapboxgl.Popup({ offset: 18 })
            .setLngLat([lng, lat])
            .setHTML(popupHtml)
            .addTo(map);
        };
        if (map.isMoving()) {
          map.once('moveend', showPopup);
        } else {
          showPopup();
        }
      }

    } else if (feats.length > 1) {
      const bounds = new mapboxgl.LngLatBounds();
      feats.forEach((f: any) => bounds.extend(f.geometry.coordinates as [number, number]));
      map.fitBounds(bounds, { padding: 80, duration: 800, essential: true });
    }
  }

function handleThemeChange(e: CustomEvent<string>) {
    const next = (e.detail as 'dark' | 'light');
    theme = next;
    if (map) {
        map.setStyle(theme === 'dark' ? darkStyleUrl : lightStyleUrl);
    }
}

function handleLayerChange(e: CustomEvent<string>) {
    layerMode = e.detail as LayerMode;
    setLayerVisibility(layerMode);
}
</script>

<svelte:head>
	<title>Mapster</title>
</svelte:head>

<Notification message={notice.message} type={notice.type} onClose={() => (notice = { message: '', type: 'info' })} />
<LoadingOverlay visible={isUploading} message="Processing poster… extracting details" />

<div class="map" bind:this={mapContainer}></div>

<CoordinateDisplay {lng} {lat} {zoom} />

<FabMenu
  disabledUpload={isUploading}
  initialLayer={layerMode}
  theme={theme}
  on:file={(e) => uploadPoster(e.detail)}
  on:layerChange={(e) => handleLayerChange(new CustomEvent('change', { detail: e.detail }))}
  on:themeChange={(e) => handleThemeChange(new CustomEvent('theme', { detail: e.detail }))}
/>


<EventSidebar on:focus={(e) => focusOnItems([e.detail])} />

<!-- Floating search button (mobile-friendly) -->
<button class="search-btn" aria-label="Search events" on:click={() => (searchOpen = true)}>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M10 4a6 6 0 104.472 10.05l4.239 4.239 1.414-1.414-4.239-4.239A6 6 0 0010 4zm0 2a4 4 0 110 8 4 4 0 010-8z"/></svg>
</button>

<SearchPanel visible={searchOpen} on:focus={(e)=>focusOnItems([e.detail])} on:close={()=>searchOpen=false} />

<style>
.search-btn {
  position: fixed;
  top: 14px;
  left: 14px;
  width: 44px;
  height: 44px;
  border-radius: 9999px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(17,24,39,0.88);
  color: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}

.search-btn:hover { background: rgba(17,24,39,0.92); }
.search-btn:active { transform: scale(0.95); }

@media (max-width: 640px) {
  .search-btn { top: 10px; left: 10px; width: 40px; height: 40px; }
}
</style>

