<script context="module">
	export const ssr = false;
</script>

<svelte:head>
    <script src="https://kit.fontawesome.com/2df6b0f25d.js" crossorigin="anonymous"></script>
</svelte:head>

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
	let navOpen = false;
	let settingsOpen = false;
	let darkMode = false;

	onMount(() => {
		mapboxgl.accessToken =
			'pk.eyJ1IjoiYW5kcndvbmciLCJhIjoiY21nMGVoOXFmMDJoeDJqb2s3dG9oZjl3aCJ9.ksR7Z1KCEONNFmVnKX5Uaw';
		map = new mapboxgl.Map({
			container: mapContainer,
			style: darkMode ? 'mapbox://styles/andrwong/cmg0l6d2r001e01ps1i8mgeyh' : 'mapbox://styles/andrwong/cmg0m3l32009201rh7v66cr21',
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

	// Reactive statement to handle theme changes
	$: if (map && map.isStyleLoaded()) {
		const newStyle = darkMode 
			? 'mapbox://styles/andrwong/cmg0l6d2r001e01ps1i8mgeyh' 
			: 'mapbox://styles/andrwong/cmg0m3l32009201rh7v66cr21';
		
		// Only change style if it's different from current
		if (map.getStyle().name !== (darkMode ? 'Mapbox Dark' : 'andrwong/cmg0l6d2r001e01ps1i8mgeyh')) {
			map.setStyle(newStyle);
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

	function handleClickOutside(event) {
		if (settingsOpen && !event.target.closest('.settings-dropdown') && !event.target.closest('.button')) {
			settingsOpen = false;
		}
	}
</script>

<div class="left-gutter">
	<label class="burger" for="burger">
		<input type="checkbox" id="burger" bind:checked={navOpen}>
		<span></span>
		<span></span>
		<span></span>
	</label>
	<div class="gutter-bottom">
		<div class="btn-cont">
			<button class="button" aria-label="Settings" onclick={() => settingsOpen = !settingsOpen}>
				<svg
					class="settings-btn"
					xmlns="http://www.w3.org/2000/svg"
					height="24"
					viewBox="0 -960 960 960"
					width="24"
					fill="#1f2937"
				>
					<path d="m370-80-16-128q-13-5-24.5-12T307-235l-119 50L78-375l103-78q-1-7-1-13.5v-27q0-6.5 1-13.5L78-585l110-190 119 50q11-8 23-15t24-12l16-128h220l16 128q13 5 24.5 12t22.5 15l119-50 110 190-103 78q1 7 1 13.5v27q0 6.5-2 13.5l103 78-110 190-118-50q-11 8-23 15t-24 12L590-80H370Zm70-80h79l14-106q31-8 57.5-23.5T639-327l99 41 39-68-86-65q5-14 7-29.5t2-31.5q0-16-2-31.5t-7-29.5l86-65-39-68-99 42q-22-23-48.5-38.5T533-694l-13-106h-79l-14 106q-31 8-57.5 23.5T321-633l-99-41-39 68 86 64q-5 15-7 30t-2 32q0 16 2 31t7 30l-86 65 39 68 99-42q22 23 48.5 38.5T427-266l13 106Zm42-180q58 0 99-41t41-99q0-58-41-99t-99-41q-59 0-99.5 41T342-480q0 58 40.5 99t99.5 41Zm-2-140Z" />
				</svg>
				<span class="tooltip">settings</span>
			</button>
		</div>
	</div>
</div>

<div class="map" bind:this={mapContainer} onclick={handleClickOutside}></div>

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
	<div class="scrim" onclick={() => (navOpen = false)}></div>
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
					<input class="toggle-checkbox" type="checkbox" bind:checked={darkMode}>
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
		<h2>FuseMap</h2>
	</header>
	<div class="sidenav-content">
		<button class="nav-item" onclick={handleReset}>Reset view</button>
		<hr />
		<div class="nav-section">
			<div class="nav-title">Layers</div>
			<label class="nav-item disabled">Coming soon</label>
		</div>
	</div>
    <footer class="sidenav-footer">
        <span class="footer-spacer"></span>
        <span class="version">v0.1</span>
    </footer>
</nav>

<style>
	.map {
		position: absolute;
		width: 100%;
		height: 100%;
		inset: 0;
		left: 60px; /* reserve space for left gutter */
		overflow: hidden;
	}

	/* Reset button positioned left of coordinate display */
	.reset-button {
		position: absolute;
		top: 12px;
		right: 280px; /* position left of coordinate display */
		background: rgba(255, 255, 255, 0.95);
		backdrop-filter: blur(8px);
		border: 1px solid rgba(0, 0, 0, 0.1);
		border-radius: 8px;
		padding: 8px 12px;
		font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
		font-size: 13px;
		color: #374151;
		cursor: pointer;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		z-index: 1;
		transition: all 0.2s ease;
	}

	.reset-button:hover {
		background: rgba(255, 255, 255, 1);
		transform: translateY(-1px);
		box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
	}

	/* Modern coordinate display in top-right */
	.coordinate-display {
		position: absolute;
		top: 12px;
		right: 12px;
		background: rgba(255, 255, 255, 0.95);
		backdrop-filter: blur(8px);
		padding: 8px 16px;
		border-radius: 8px;
		font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
		font-size: 13px;
		color: #374151;
		border: 1px solid rgba(0, 0, 0, 0.1);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		z-index: 1;
		display: flex;
		align-items: center;
		gap: 8px;
		max-width: calc(100vw - 80px);
		overflow: visible;
		white-space: nowrap;
	}

	.coordinate-item {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.coordinate-label {
		color: #6b7280;
		font-weight: 500;
	}

	.coordinate-value {
		color: #111827;
		font-weight: 600;
	}

	.coordinate-separator {
		color: #d1d5db;
		margin: 0 4px;
	}

	.left-gutter {
		position: absolute;
		top: 0;
		left: 0;
		width: 60px;
		height: 100%;
		background: #ffffff;
		z-index: 4;
		border-right: 1px solid #e5e7eb;
		box-shadow: 0 0 16px rgba(0, 0, 0, 0.06);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: flex-start;
		padding-top: 16px;
		padding-bottom: 20px; /* increased padding to prevent cutoff */
		gap: 0;
	}

	.burger {
		position: relative;
		width: 40px;
		height: 30px;
		background: transparent;
		cursor: pointer;
		display: block;
	}

	.burger input {
		display: none;
	}

	.burger span {
		display: block;
		position: absolute;
		height: 4px;
		width: 100%;
		background: black;
		border-radius: 9px;
		opacity: 1;
		left: 0;
		transform: rotate(0deg);
		transition: .25s ease-in-out;
	}

	.burger span:nth-of-type(1) {
		top: 0px;
		transform-origin: left center;
	}

	.burger span:nth-of-type(2) {
		top: 50%;
		transform: translateY(-50%);
		transform-origin: left center;
	}

	.burger span:nth-of-type(3) {
		top: 100%;
		transform-origin: left center;
		transform: translateY(-100%);
	}

	.burger input:checked ~ span:nth-of-type(1) {
		transform: rotate(45deg);
		top: 0px;
		left: 5px;
	}

	.burger input:checked ~ span:nth-of-type(2) {
		width: 0%;
		opacity: 0;
	}

	.burger input:checked ~ span:nth-of-type(3) {
		transform: rotate(-45deg);
		top: 28px;
		left: 5px;
	}

	.scrim {
		position: absolute;
		inset: 0;
		background: rgba(0, 0, 0, 0.25);
		z-index: 2;
		overflow: hidden;
	}

	/* Global overflow prevention - only apply to map interface */
	:global(html, body) {
		overflow: hidden;
		height: 100vh;
		margin: 0;
		padding: 0;
	}

	/* Settings button container */
	.gutter-bottom {
		margin-top: auto;
		width: 100%;
		display: flex;
		justify-content: center;
		padding-bottom: 22px;
	}

	/* Modern settings button */
	.btn-cont {
		display: flex;
		justify-content: center;
		align-items: center;
		width: 44px;
		height: 44px;
		background: #ffffff;
		border: 1px solid #e5e7eb;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
		transition: all 0.2s ease;
	}

	.btn-cont:hover {
		background: #f9fafb;
		border-color: #d1d5db;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
		transform: translateY(-1px);
	}

	.button {
		background: none;
		border: none;
		cursor: pointer;
		padding: 8px;
		border-radius: 8px;
		position: relative;
		transition: background-color 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.button:hover .tooltip {
		visibility: visible;
		opacity: 1;
	}

	.settings-btn {
		display: block;
		transition: transform 0.3s ease;
		width: 20px;
		height: 20px;
	}

	.settings-btn:hover {
		transform: rotate(90deg);
	}

	.tooltip {
		visibility: hidden;
		width: 100px;
		background-color: #1f2937;
		color: #ffffff;
		text-align: center;
		border-radius: 6px;
		padding: 6px 8px;
		position: absolute;
		z-index: 10;
		bottom: 125%;
		left: 50%;
		margin-left: -50px;
		opacity: 0;
		transition: opacity 0.3s ease;
		font-size: 12px;
		font-weight: 500;
	}

	.tooltip::after {
		content: '';
		position: absolute;
		top: 100%;
		left: 50%;
		margin-left: -5px;
		border-width: 5px;
		border-style: solid;
		border-color: #1f2937 transparent transparent transparent;
	}

	.sidenav {
		position: absolute;
		top: 0;
		left: 60px;
		height: 100%;
		width: 300px;
		background: #ffffff;
		border-right: 1px solid #e5e7eb;
		box-shadow: 0 0 24px rgba(0, 0, 0, 0.12);
		z-index: 3;
		transform: translateX(-100%);
		transition: transform 200ms ease-out;
		display: flex;
		flex-direction: column;
		overflow: visible;
	}
	.sidenav.open {
		transform: translateX(0);
	}
	.sidenav-header {
		padding: 20px 20px 12px 20px;
		font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
		font-weight: 600;
		font-size: 18px;
		color: #111827;
		border-bottom: 1px solid #f3f4f6;
		background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
	}
	.sidenav-content {
		padding: 16px 20px;
		overflow: hidden;
		flex: 1 1 auto;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.sidenav-footer {
		position: relative;
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 16px 20px;
		border-top: 1px solid #f3f4f6;
		color: #6b7280;
		font-size: 13px;
		min-height: 48px;
		background: #f9fafb;
	}

	.footer-spacer {
		flex: 1 1 auto;
	}

	.version {
		color: #9ca3af;
		font-weight: 500;
	}

	.nav-section {
		margin: 16px 0 8px 0;
	}

	.nav-title {
		font-size: 11px;
		color: #9ca3af;
		margin: 0 0 8px 4px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		font-weight: 600;
	}

	.nav-item {
		padding: 10px 16px;
		border-radius: 8px;
		border: 1px solid #e5e7eb;
		background: #ffffff;
		cursor: pointer;
		margin: 4px 0;
		transition: all 0.2s ease;
		font-size: 14px;
		font-weight: 500;
		color: #374151;
		display: block;
		width: 100%;
		text-align: left;
	}

	.nav-item:hover {
		background: #f3f4f6;
		border-color: #d1d5db;
		transform: translateX(2px);
	}

	.nav-item.disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.nav-item.disabled:hover {
		background: #ffffff;
		border-color: #e5e7eb;
		transform: none;
	}

	/* Settings dropdown styles */
	.settings-dropdown {
		position: absolute;
		bottom: 60px; /* position above the settings button */
		left: 70px; /* position to the right of the left gutter */
		width: 280px;
		background: #ffffff;
		border-radius: 12px;
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
		z-index: 10;
		overflow: hidden;
		border: 1px solid rgba(0, 0, 0, 0.08);
		animation: slideUp 0.2s ease-out;
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
	}

	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateY(8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.settings-header {
		display: flex;
		align-items: center;
		justify-content: flex-start;
		padding: 16px 20px 12px 20px;
		border-bottom: 1px solid #f3f4f6;
		background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
	}

	.settings-header h3 {
		margin: 0;
		font-size: 16px;
		font-weight: 600;
		color: #111827;
		font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
	}

	.settings-content {
		padding: 16px 20px 20px 20px;
	}

	.setting-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
	}

	.setting-info {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.setting-label {
		font-size: 15px;
		font-weight: 500;
		color: #111827;
	}

	.setting-description {
		font-size: 13px;
		color: #6b7280;
		line-height: 1.4;
	}

	/* New theme toggle styles */
	.toggle-checkbox {
		position: absolute;
		opacity: 0;
		cursor: pointer;
		height: 0;
		width: 0;
	}

	.toggle-slot {
		font-size: 10px;
		position: relative;
		height: 3.5em;
		width: 7em;
		border: 2px solid;
        border-color: #9ca3af;
		border-radius: 10em;
		background-color: white;
		transition: background-color 250ms;
	}

	.toggle-checkbox:checked ~ .toggle-slot {
		background-color: #374151;
	}

	.toggle-button {
		transform: translate(0.3em, 0.25em);
		position: absolute;
		height: 3em;
		width: 3em;
		border-radius: 50%;
		background-color: #ffeccf;
		box-shadow: inset 0px 0px 0px 0.75em #ffbb52;
		transition: background-color 250ms, border-color 250ms, transform 500ms cubic-bezier(.26,2,.46,.71);
	}

	.toggle-checkbox:checked ~ .toggle-slot .toggle-button {
		background-color: #485367;
		box-shadow: inset 0px 0px 0px 0.75em white;
		transform: translate(3.65em, 0.25em);
	}

	.sun-icon {
		position: absolute;
		height: 6em;
		width: 6em;
		color: #ffbb52;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.2em;
	}

	.sun-icon-wrapper {
		position: absolute;
		height: 6em;
		width: 6em;
		opacity: 1;
		transform: translate(2em, 2em) rotate(15deg);
		transform-origin: 50% 50%;
		transition: opacity 150ms, transform 500ms cubic-bezier(.26,2,.46,.71);
	}

	.toggle-checkbox:checked ~ .toggle-slot .sun-icon-wrapper {
		opacity: 0;
		transform: translate(3em, 2em) rotate(0deg);
	}

	.moon-icon {
		position: absolute;
		height: 6em;
		width: 6em;
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.2em;
	}

	.moon-icon-wrapper {
		position: absolute;
		height: 6em;
		width: 6em;
		opacity: 0;
		transform: translate(11em, 2em) rotate(0deg);
		transform-origin: 50% 50%;
		transition: opacity 150ms, transform 500ms cubic-bezier(.26,2.5,.46,.71);
	}

	.toggle-checkbox:checked ~ .toggle-slot .moon-icon-wrapper {
		opacity: 1;
		transform: translate(2em, 2em) rotate(-15deg);
	}
</style>
