<script lang="ts">
    export let lng: number;
    export let lat: number;
    export let zoom: number;
</script>

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


