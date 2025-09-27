<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
  let open = false;
  const options = [
    { id: 'normal', label: 'Map' },
    { id: 'heat', label: 'Heatmap' },
    { id: 'pins', label: 'Pins' }
  ];
  function select(id: string) {
    dispatch('change', id);
    open = false;
  }
</script>

<div class="layer-toggle">
  {#each options as o}
    <button
      class="segment {o.id === $selected ? 'active' : ''}"
      on:click={() => select(o.id)}
      aria-label={o.label}
    >
      {#if o.id === 'normal'}🗺️{/if}
      {#if o.id === 'heat'}🔥{/if}
      {#if o.id === 'pins'}📍{/if}
    </button>
  {/each}
</div>

<script context="module">
  import { writable } from 'svelte/store';
  export const selected = writable('heat');
</script>

<style>
.layer-toggle{
  position:fixed;
  left:50%;
  bottom:calc(env(safe-area-inset-bottom,0px)+80px);
  transform:translateX(-50%);
  display:flex;
  background:rgba(17,24,39,0.85);
  backdrop-filter:blur(6px);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:9999px;
  padding:4px;
  gap:10px;
  z-index:1000;
  margin-top: 800px;
}
.segment{
  width:40px;height:40px;border-radius:9999px;border:none;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:18px;color:#fff;background:transparent;transition:background 0.15s;
}
.segment:hover{background:rgba(255,255,255,0.08);} 
.segment.active{background:#22d3ee;color:#111;}
</style>
