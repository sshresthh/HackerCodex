<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { getSupabaseClient } from '$lib/supabaseClient';

  export let visible: boolean = false;

  const dispatch = createEventDispatcher<{ focus: any; close: void }>();

  let query = '';
  let loading = false;
  let results: any[] = [];
  let errorMsg = '';
  let inputEl: HTMLInputElement | null = null;

  async function runSearch() {
    const supabase = getSupabaseClient();
    if (!supabase) { errorMsg = 'Supabase not configured.'; return; }
    loading = true; errorMsg = '';

    const term = query.trim();
    let q = supabase
      .from('events')
      .select('id,title,location,date,time,category,lat,lng,description')
      .limit(50);

    if (term) {
      const like = `%${term}%`;
      q = q.or(`title.ilike.${like},location.ilike.${like},description.ilike.${like},category.ilike.${like}`);
    }

    q = q.order('date', { ascending: false }).order('time', { ascending: false });

    const { data, error } = await q;
    if (error) {
      errorMsg = error.message || 'Search failed';
      results = [];
    } else {
      results = data || [];
    }
    loading = false;
  }

  function selectItem(item: any) {
    dispatch('focus', item);
  }

  function handleKey(e: KeyboardEvent) {
    if (e.key === 'Enter') runSearch();
    if (e.key === 'Escape') dispatch('close');
  }

  onMount(() => {
    if (visible) setTimeout(() => inputEl?.focus(), 0);
  });
</script>

{#if visible}
  <div class="search-overlay" on:keydown={handleKey}>
    <div class="panel" role="dialog" aria-label="Search events">
      <div class="row">
        <svg class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#9ca3af" aria-hidden="true"><path d="M10 4a6 6 0 104.472 10.05l4.239 4.239 1.414-1.414-4.239-4.239A6 6 0 0010 4zm0 2a4 4 0 110 8 4 4 0 010-8z"/></svg>
        <input bind:this={inputEl} class="input" placeholder="Search events, venues, categories..." bind:value={query} on:keydown={handleKey} />
        <button class="btn" on:click={runSearch} aria-label="Run search">Search</button>
      </div>
      {#if errorMsg}
        <div class="err">{errorMsg}</div>
      {/if}
      <div class="results">
        {#if loading}
          <div class="loading">Searching…</div>
        {:else if results.length === 0}
          <div class="empty">No results yet</div>
        {:else}
          {#each results as r}
            <button class="item" on:click={() => selectItem(r)}>
              <div class="title">{r.title || 'Untitled event'}</div>
              <div class="sub">{r.date || ''} {r.time || ''} • {r.location || ''}</div>
            </button>
          {/each}
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .search-overlay { position: fixed; inset: 0; display: flex; align-items: flex-start; justify-content: center; padding-top: 16px; z-index: 1100; pointer-events: none; }
  .panel { pointer-events: auto; width: min(720px, 92vw); background: rgba(17,24,39,0.85); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; box-shadow: 0 20px 60px rgba(0,0,0,0.35); }
  .row { display: flex; gap: 10px; align-items: center; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.06); }
  .icon { width: 20px; height: 20px; }
  .input { flex: 1; height: 40px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10); border-radius: 10px; padding: 0 12px; color: #f8fafc; outline: none; }
  .input::placeholder { color: #94a3b8; }
  .btn { background: #22d3ee; color: #111827; border: none; border-radius: 10px; height: 40px; padding: 0 14px; font-weight: 700; cursor: pointer; }
  .results { max-height: 50vh; overflow: auto; padding: 8px; }
  .item { width: 100%; text-align: left; background: transparent; border: none; padding: 10px 12px; border-radius: 10px; color: #e5e7eb; cursor: pointer; }
  .item:hover { background: rgba(255,255,255,0.06); }
  .title { font-weight: 700; }
  .sub { font-size: 12px; color: #a1a1aa; }
  .loading, .empty, .err { padding: 12px; color: #cbd5e1; }
  .err { color: #fda4af; }

  @media (max-width: 640px) {
    .panel { width: 94vw; }
  }
</style>
