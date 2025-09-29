<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';

  // Events: file (File), openList (void), layerChange ("heat"|"pins"|"normal")
  const dispatch = createEventDispatcher<{
    file: File;
    openList: void;
    layerChange: 'heat' | 'pins' | 'normal';
    themeChange: 'dark' | 'light';
  }>();

  export let disabledUpload: boolean = false;
  export let initialLayer: 'heat' | 'pins' | 'normal' = 'heat';
  export let theme: 'dark' | 'light' = 'dark';

  let layer: 'heat' | 'pins' | 'normal' = initialLayer;
  let inputEl: HTMLInputElement | null = null;

  // Mobile expandable state
  let isMobile = false;

  function updateViewport() {
    isMobile = window.matchMedia('(max-width: 640px)').matches;
    // no collapse behaviour; nothing to do
  }

  onMount(() => {
    updateViewport();
    window.addEventListener('resize', updateViewport);
    return () => window.removeEventListener('resize', updateViewport);
  });

  function triggerUpload() {
    if (!disabledUpload) inputEl?.click();
  }

  function onFileChange(e: Event) {
    const file = (e.currentTarget as HTMLInputElement).files?.[0];
    if (file) dispatch('file', file);
    if (inputEl) inputEl.value = '';
  }

  function openList() {
    dispatch('openList');
  }

  function cycleLayer() {
    layer = layer === 'heat' ? 'pins' : layer === 'pins' ? 'normal' : 'heat';
    dispatch('layerChange', layer);
  }

  function toggleTheme() {
    theme = theme === 'dark' ? 'light' : 'dark';
    dispatch('themeChange', theme);
  }
</script>

<div class="fab-menu" >
  <!-- Always-visible actions -->
  <button class="fab-item action-upload" aria-label="Upload poster" on:click|stopPropagation={triggerUpload} disabled={disabledUpload} title="Upload poster">
    <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff" aria-hidden="true">
      <path d="M9 3l-1.172 2H5a2 2 0 00-2 2v10a2 2 0 002 2h14a2 2 0 002-2V7a2 2 0 00-2-2h-2.828L15 3H9zm3 14a5 5 0 110-10 5 5 0 010 10zm0-2a3 3 0 100-6 3 3 0 000 6z"/>
    </svg>
  </button>

  <button class="fab-item action-layer" aria-label="Change layer" on:click|stopPropagation={cycleLayer} title="Change layer">
    {#if layer === 'heat'}
      <span class="emoji">🔥</span>
    {:else if layer === 'pins'}
      <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ffffff" aria-hidden="true">
        <path d="M12 2c-3.866 0-7 3.134-7 7 0 5.25 7 13 7 13s7-7.75 7-13c0-3.866-3.134-7-7-7zm0 11a4 4 0 110-8 4 4 0 010 8z"/>
      </svg>
    {:else}
      <span class="emoji">🗺️</span>
    {/if}
  </button>

  <button class="fab-item action-theme" aria-label="Toggle theme" on:click|stopPropagation={toggleTheme} title="Toggle theme">
    {#if theme === 'dark'}
      <span class="emoji">🌞</span>
    {:else}
      <span class="emoji">🌙</span>
    {/if}
  </button>

  <!-- Hidden file input -->
  <input class="visually-hidden" type="file" accept="image/*" capture="environment" bind:this={inputEl} on:change={onFileChange} />
</div>

<style>
  .fab-menu {
    position: fixed;
    right: 16px;
    bottom: calc(env(safe-area-inset-bottom, 0px) + 16px);
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 12px;
    z-index: 1000;
    transition: height 200ms ease;
  }

  .fab-item {
    width: 56px;
    height: 56px;
    border-radius: 9999px;
    border: 1px solid rgba(255,255,255,0.06);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background: rgba(17,24,39,0.88);
    color: #fff;
    box-shadow: 0 10px 30px rgba(0,0,0,0.28);
    transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease, opacity 160ms ease;
  }

  .fab-item:hover { background: rgba(17,24,39,0.92); box-shadow: 0 12px 36px rgba(0,0,0,0.34); transform: translateY(-1px); }
  .fab-item:active { transform: scale(0.97); }

  .icon { width: 24px; height: 24px; }
  .emoji { font-size: 18px; line-height: 1; }

  /* Accessibility: hidden input */
  .visually-hidden {
    position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
  }

  @media (max-width: 640px) {
    .fab-menu { right: 12px; bottom: calc(env(safe-area-inset-bottom, 0px) + 12px); gap: 10px; }
    .fab-item { width: 56px; height: 56px; }

    /* previously collapsed state removed */
  }
</style>
