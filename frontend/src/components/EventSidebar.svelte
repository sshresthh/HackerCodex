<script lang="ts">
  import { onMount } from 'svelte';
  import { getSupabaseClient } from '$lib/supabaseClient';
  import { createEventDispatcher } from 'svelte';
  import { fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  const dispatch = createEventDispatcher<{ focus: any }>();

  // Mobile bottom-sheet collapsed state
  let collapsed: boolean = false;
  let isMobile = false;

  function updateViewport() {
    isMobile = window.matchMedia('(max-width: 640px)').matches;
    if (isMobile && collapsed === false) collapsed = true; // default collapsed on mobile
    if (!isMobile) collapsed = false; // always open on desktop
  }

  let query = '';
  let loading = false;
  let events: any[] = [];
  let page = 0;
  const pageSize = 100;
  let totalShown = 0;
  let errorMsg = '';
  let sidebarEl: HTMLDivElement | null = null;
  let selectedId: any = null;

  async function fetchPage(reset = false) {
    const supabase = getSupabaseClient();
    if (!supabase) { errorMsg = 'Supabase not configured.'; return; }
    loading = true; errorMsg = '';

    const from = (reset ? 0 : page * pageSize);
    const to = from + pageSize - 1;

    let q = supabase
      .from('events')
      .select('id,title,location,date,time,category,lat,lng,description,link', { count: 'exact' })
      .order('date', { ascending: false })
      .order('time', { ascending: false })
      .range(from, to);

    const term = query.trim();
    if (term) {
      const like = `%${term}%`;
      q = q.or(`title.ilike.${like},location.ilike.${like},description.ilike.${like},category.ilike.${like}`);
    }

    const { data, error } = await q;
    if (error) {
      errorMsg = error.message || 'Failed to load events';
      loading = false; return;
    }

    if (reset) {
      events = (data || []).map((e:any)=>({ ...e, link: e.link || e.url || '' }));
      page = 0;
    } else {
      events = [...events, ...(data || [])];
    }
    totalShown = events.length;
    loading = false;
  }

  function search() { fetchPage(true); }
  function loadMore() { page += 1; fetchPage(false); }
  function select(e: any) { selectedId = e?.id ?? null; dispatch('focus', e); }

  onMount(() => {
    updateViewport();
    window.addEventListener('resize', updateViewport);
    return () => window.removeEventListener('resize', updateViewport);
  });
</script>

<div class="sidebar {isMobile ? 'mobile' : 'desktop'} {collapsed ? 'collapsed' : 'open'}" bind:this={sidebarEl}>
  {#if isMobile}
    <button type="button" class="drag-handle" aria-label="Toggle events panel" on:click={() => collapsed = !collapsed} on:keydown={(e)=> (e.key==='Enter'||e.key===' ') && (collapsed=!collapsed)}></button>
  {/if}
  <!-- handle and close buttons removed -->

  <div class="panel">
    <div class="top">
      <div class="title-row">
        <div class="title">Mapster</div>
      </div>
      <div class="search">
        <svg class="sicon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#9ca3af"><path d="M10 4a6 6 0 104.472 10.05l4.239 4.239 1.414-1.414-4.239-4.239A6 6 0 0010 4zm0 2a4 4 0 110 8 4 4 0 010-8z"/></svg>
        <input class="input" placeholder="Search events…" bind:value={query} on:keydown={(e) => e.key==='Enter' && search()} />
        <button class="btn" on:click={search}>Search</button>
      </div>
    </div>

    {#if errorMsg}
      <div class="err">{errorMsg}</div>
    {/if}

    <div class="list">
      {#each events as ev, i}
        <button class="item {ev.id === selectedId ? 'selected' : ''}" on:click={() => select(ev)} in:fly={{ y: 12, duration: 180, delay: i * 15, easing: cubicOut }}>
          <div class="dot" />
          <div class="meta">
            <div class="name">{ev.title || 'Untitled event'}</div>
            <div class="row">
              <div class="date">{ev.date || ''}</div>
              {#if ev.time}
                <span class="time">{ev.time}</span>
              {/if}
            </div>
            {#if ev.location}
              <div class="loc">{ev.location}</div>
            {/if}
            {#if ev.description}
              <div class="desc">{ev.description}</div>
            {/if}
            {#if ev.link}
              <a class="alink" href={ev.link} target="_blank" rel="noopener">Visit website →</a>
            {/if}
          </div>
        </button>
      {/each}
      {#if loading}
        <div class="loading">Loading…</div>
      {/if}
    </div>

    <!-- bottom bar removed -->
  </div>
</div>

<style>
/* Sidebar slides in/out instead of resizing, leaving a 28px handle visible when collapsed */
.sidebar { position: fixed; left: 0; top: 0; bottom: 0; z-index: 1050; display: block; align-items: stretch; width: min(340px, 92vw); transform: translateX(0); transition: transform 250ms cubic-bezier(0.4, 0, 0.2, 1); font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; overflow: visible; }
  /* collapsed state no longer used */
  .sidebar.collapsed { display: none; }

  /* keep open class for semantic clarity (no extra rule needed) */
  .sidebar.open { transform: translateX(0); }
  .panel { width: 100%; height: 100%; display: flex; flex-direction: column; background: rgba(10,12,16,0.92); border: 1px solid rgba(255,255,255,0.06); border-left: none; box-shadow: 0 20px 60px rgba(0,0,0,0.35); }
  .top { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.06); }
  .title-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
  .title { color: #e5e7eb; font-weight: 900; font-size: 18px; letter-spacing: 0.3px; font-family: 'Inter', 'Poppins', system-ui, sans-serif; }
  .search { display: flex; gap: 8px; align-items: center; }
  .sicon { width: 18px; height: 18px; }
  .input { flex: 1; height: 34px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 0 10px; color: #f1f5f9; outline: none; }
  .input::placeholder { color: #94a3b8; }
  .btn { background: rgba(255,255,255,0.08); color: #e5e7eb; border: 1px solid rgba(255,255,255,0.10); border-radius: 10px; height: 34px; padding: 0 12px; font-weight: 700; cursor: pointer; }
  .list { flex: 1; overflow: auto; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
  .item { position: relative; display: flex; gap: 10px; align-items: flex-start; width: 100%; background: transparent; border: 1px solid rgba(255,255,255,0.06); text-align: left; padding: 12px; border-radius: 12px; color: #e5e7eb; cursor: pointer; transition: background 120ms ease, border-color 120ms ease; }
  .item:hover { background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.10); }
  .item.selected { border-color: rgba(229,231,235,0.35); }
  .dot { width: 7px; height: 7px; margin-top: 6px; border-radius: 9999px; background: #94a3b8; flex: 0 0 auto; }
  .name { font-weight: 800; letter-spacing: 0.2px; margin-bottom: 2px; }
  .row { display: flex; align-items: center; gap: 8px; }
  .date { font-size: 12px; color: #a1a1aa; }
  .time { font-size: 11px; padding: 2px 8px; border-radius: 9999px; background: rgba(255,255,255,0.06); color: #e5e7eb; border: 1px solid rgba(255,255,255,0.10); }
  .loc { font-size: 12px; color: #9ca3af; margin-top: 2px; }
  .desc { font-size: 12px; color: #cbd5e1; margin-top: 6px; opacity: 0.95; }
  .alink { font-size: 12px; color: #38bdf8; text-decoration: underline; margin-top: 4px; display: inline-block; }
  /* bottom bar removed */

  /* Subtle scrollbar */
  .list::-webkit-scrollbar { width: 8px; }
  .list::-webkit-scrollbar-thumb { background: rgba(148,163,184,0.25); border-radius: 9999px; }

  /* Mobile bottom-sheet styles */
  @media (max-width: 640px) {
    .sidebar.desktop { display: none; }
    .sidebar.mobile { left: 0; right: 0; width: 100vw; height: 60vh; top: auto; bottom: 0; border-left: 1px solid rgba(255,255,255,0.06); border-top: 1px solid rgba(255,255,255,0.06); border-right: 1px solid rgba(255,255,255,0.06); border-bottom: none; border-radius: 14px 14px 0 0; overflow: hidden; backdrop-filter: blur(10px); }
    .sidebar.mobile.collapsed { transform: translateY(calc(100% - 48px)); }
    .drag-handle { width: 42px; height: 5px; border-radius: 3px; background: rgba(255,255,255,0.35); margin: 8px auto 4px auto; cursor: pointer; }
    .top { padding-top: 0; }
  }
</style>
