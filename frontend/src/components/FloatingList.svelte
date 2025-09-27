<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher<{ select: { lng: number, lat: number } }>();

    export let disabled: boolean = false;
    export let events: Array<{
        title: string;
        date?: string;
        location?: string;
        category?: string;
        lat?: number;
        lng?: number;
    }> = [];

    let searchQuery: string = "";
    let isOpen: boolean = false;

    // Filter events by search
    $: filteredEvents = events.filter(e =>
        e.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.location?.toLowerCase().includes(searchQuery.toLowerCase())
    );
</script>

<div class="fab-list">
    <button
        type="button"
        class="fab-button"
        aria-label="Open events list"
        disabled={disabled}
        on:click={() => (isOpen = !isOpen)}
    >
        <!-- List icon -->
        <svg class="fab-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ffffff">
            <path d="M4 6h2v2H4V6zm4 0h12v2H8V6zm-4 5h2v2H4v-2zm4 0h12v2H8v-2zm-4 5h2v2H4v-2zm4 0h12v2H8v-2z"/>
        </svg>
    </button>

    {#if isOpen}
        <!-- Event List Modal -->
        <div class="event-list-modal">
            <h3 class="event-list-title">✨ Explore Events</h3>
            
            <input
                type="text"
                class="event-search"
                placeholder="Search events..."
                bind:value={searchQuery}
            />

            {#if filteredEvents.length > 0}
                {#each filteredEvents.slice(0, 10) as e}
                    <div
                        class="event-card"
                        on:click={() => e.lat && e.lng && dispatch('select', { lat: e.lat, lng: e.lng })}
                    >
                        <div class="event-card-title">{e.title}</div>
                        <div class="event-card-sub">{e.date || "TBA"} • {e.location || "Adelaide"}</div>
                        <div class="event-card-cat">{e.category || "General"}</div>
                    </div>
                {/each}
            {:else}
                <p class="event-empty">No events found.</p>
            {/if}
        </div>
    {/if}
</div>
