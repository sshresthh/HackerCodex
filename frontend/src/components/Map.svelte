<script context="module">
	export const ssr = false;
</script>

<script lang="ts">
    import { env as publicEnv } from '$env/dynamic/public';
	import mapboxgl from 'mapbox-gl';
	import 'mapbox-gl/dist/mapbox-gl.css';
	import './Map.css';
	import { onMount, onDestroy } from 'svelte';

    let map: mapboxgl.Map;
    let mapContainer: HTMLDivElement;
	const initialState = { lng: 138.599503, lat: -34.92123, zoom: 11.5 };
	let lng = initialState.lng;
	let lat = initialState.lat;
	let zoom = initialState.zoom;
	let navOpen = false;
	let settingsOpen = false;
	let darkMode = false;
    const lightStyleUrl = 'mapbox://styles/andrwong/cmg0m3l32009201rh7v66cr21';
    const darkStyleUrl = 'mapbox://styles/andrwong/cmg0l6d2r001e01ps1i8mgeyh';
    let currentStyleUrl = lightStyleUrl;

    onMount(() => {
        mapboxgl.accessToken = publicEnv.PUBLIC_MAPBOX_TOKEN || '';
		map = new mapboxgl.Map({
			container: mapContainer,
            style: darkMode ? darkStyleUrl : lightStyleUrl,
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
        currentStyleUrl = darkMode ? darkStyleUrl : lightStyleUrl;
	});

    // Reactive statement to handle theme changes without redundant setStyle calls
    $: if (map) {
        const newStyle = darkMode ? darkStyleUrl : lightStyleUrl;
        if (newStyle !== currentStyleUrl) {
            map.setStyle(newStyle);
            currentStyleUrl = newStyle;
        }
    }

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

    function handleClickOutside(event: MouseEvent | KeyboardEvent) {
        const target = event.target as HTMLElement | null;
        if (
            settingsOpen &&
            target &&
            !target.closest('.settings-dropdown') &&
            !target.closest('.button')
        ) {
            settingsOpen = false;
        }
    }
</script>

<svelte:head>
	<title>Mapster</title>
	<script src="https://kit.fontawesome.com/2df6b0f25d.js" crossorigin="anonymous"></script>
</svelte:head>

<button onclick={handleReset} class="reset-button">Reset</button>

<div class="left-gutter">
	<label class="burger" for="burger">
		<input
			type="checkbox"
			id="burger"
			bind:checked={navOpen}
			onchange={() => {
				if (navOpen) settingsOpen = false;
			}}
		/>
		<span></span>
		<span></span>
		<span></span>
	</label>
	<div class="gutter-bottom">
		<div class="btn-cont">
			<button
				class="button"
				aria-label="Settings"
				onclick={() => {
					if (navOpen) navOpen = false;
					settingsOpen = !settingsOpen;
				}}
			>
				<svg
					class="settings-btn"
					xmlns="http://www.w3.org/2000/svg"
					height="24"
					viewBox="0 -960 960 960"
					width="24"
					fill="#1f2937"
				>
					<path
						d="m370-80-16-128q-13-5-24.5-12T307-235l-119 50L78-375l103-78q-1-7-1-13.5v-27q0-6.5 1-13.5L78-585l110-190 119 50q11-8 23-15t24-12l16-128h220l16 128q13 5 24.5 12t22.5 15l119-50 110 190-103 78q1 7 1 13.5v27q0 6.5-2 13.5l103 78-110 190-118-50q-11 8-23 15t-24 12L590-80H370Zm70-80h79l14-106q31-8 57.5-23.5T639-327l99 41 39-68-86-65q5-14 7-29.5t2-31.5q0-16-2-31.5t-7-29.5l86-65-39-68-99 42q-22-23-48.5-38.5T533-694l-13-106h-79l-14 106q-31 8-57.5 23.5T321-633l-99-41-39 68 86 64q-5 15-7 30t-2 32q0 16 2 31t7 30l-86 65 39 68 99-42q22 23 48.5 38.5T427-266l13 106Zm42-180q58 0 99-41t41-99q0-58-41-99t-99-41q-59 0-99.5 41T342-480q0 58 40.5 99t99.5 41Zm-2-140Z"
					/>
				</svg>
				<span class="tooltip">settings</span>
			</button>
		</div>
	</div>
</div>

<div class="map" bind:this={mapContainer} onclick={handleClickOutside} role="button" tabindex="0" onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && handleClickOutside(e)}></div>

<!-- Coordinate display moved to top-right for better UX -->
<div class="coordinate-display">
	<span class="coordinate-item">
		<span class="coordinate-label">Longitude:</span>
		<span class="coordinate-value">{lng.toFixed(4)}</span>
	</span>
	<span class="coordinate-separator">|</span>
	<span class="coordinate-item">
		<span class="coordinate-label">Latitude:</span>
		<span class="coordinate-value">{lat.toFixed(4)}</span>
	</span>
	<span class="coordinate-separator">|</span>
	<span class="coordinate-item">
		<span class="coordinate-label">Zoom:</span>
		<span class="coordinate-value">{zoom.toFixed(2)}</span>
	</span>
</div>

<!-- menu toggle handled by burger -->
{#if navOpen}
    <div class="scrim" onclick={() => (navOpen = false)} role="button" tabindex="0" onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && (navOpen = false)}></div>
{/if}

{#if settingsOpen}
	<div class="settings-dropdown">
		<div class="settings-header">
			<h3>Settings</h3>
		</div>
		<div class="settings-content">
			<div class="setting-item">
				<div class="setting-info">
					<span class="setting-label">Theme</span>
					<span class="setting-description">Switch between light and dark mode</span>
				</div>
				<label>
					<input class="toggle-checkbox" type="checkbox" bind:checked={darkMode} />
					<div class="toggle-slot">
						<div class="sun-icon-wrapper">
							<div class="iconify sun-icon" data-icon="feather-sun" data-inline="false"></div>
						</div>
						<div class="toggle-button"></div>
						<div class="moon-icon-wrapper">
							<div class="iconify moon-icon" data-icon="feather-moon" data-inline="false"></div>
						</div>
					</div>
				</label>
			</div>
		</div>
	</div>
{/if}

<nav class="sidenav {navOpen ? 'open' : ''}" aria-hidden={!navOpen}>
	<header class="sidenav-header">
		<h2>Mapster</h2>
	</header>
	<div class="sidenav-content">
		<button class="nav-item">TEST BUTTON</button>
		<hr />
	</div>
	<footer class="sidenav-footer">
		<span class="footer-spacer"></span>
		<span class="version">v1.0</span>
	</footer>
</nav>
