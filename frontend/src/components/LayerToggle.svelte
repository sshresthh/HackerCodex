<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { writable } from 'svelte/store';

  // Selected layer store (shared with Map component)
  export const selected = writable('heat');

  const dispatch = createEventDispatcher();
  const options = [
    { id: 'normal', label: 'Map' },
    { id: 'heat', label: 'Heatmap' },
    { id: 'pins', label: 'Pins' }
  ];

  function select(id: string) {
    dispatch('change', id);
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

<style>
.layer-toggle {
  position: fixed;
  left: 50%;
  bottom: calc(env(safe-area-inset-bottom, 0px) + 104px); /* sits just above FABs */
  transform: translateX(-50%);
  display: flex;
  background: rgba(17, 24, 39, 0.85);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  padding: 4px;
  gap: 6px;
  z-index: 1000;
}

.segment {
  width: 36px;
  height: 36px;
  border-radius: 9999px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  color: #fff;
  background: transparent;
  transition: background 0.15s;
}

.segment:hover {
  background: rgba(255, 255, 255, 0.08);
}

.segment.active {
  background: #22d3ee;
  color: #111;
}
</style>
