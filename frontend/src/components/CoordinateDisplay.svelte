<script lang="ts">
    export let lng: number;
    export let lat: number;
    export let zoom: number;
</script>

<div class="coordinate-display" style="background: rgba(17,17,17,0.9); color: #e5e7eb; border: 1px solid rgba(255,255,255,0.08)">
    <span class="coordinate-item">
        <span class="coordinate-label" style="color:#9ca3af">Longitude:</span>
        <span class="coordinate-value" style="color:#e5e7eb">{lng.toFixed(4)}</span>
    </span>
    <span class="coordinate-separator">|</span>
    <span class="coordinate-item">
        <span class="coordinate-label" style="color:#9ca3af">Latitude:</span>
        <span class="coordinate-value" style="color:#e5e7eb">{lat.toFixed(4)}</span>
    </span>
    <span class="coordinate-separator">|</span>
    <span class="coordinate-item">
        <span class="coordinate-label" style="color:#9ca3af">Zoom:</span>
        <span class="coordinate-value" style="color:#e5e7eb">{zoom.toFixed(2)}</span>
    </span>
}</div>


