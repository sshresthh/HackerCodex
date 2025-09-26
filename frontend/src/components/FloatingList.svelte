<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher<{ open: void }>();
    export let disabled: boolean = false;
</script>

<div class="fab-list">
    <button
        type="button"
        class="fab-button"
        aria-label="Open events list"
        disabled={disabled}
        onclick={(e) => { e.preventDefault(); !disabled && dispatch('open'); }}
    >
        <!-- List icon -->
        <svg class="fab-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ffffff" aria-hidden="true">
            <path d="M4 6h2v2H4V6zm4 0h12v2H8V6zm-4 5h2v2H4v-2zm4 0h12v2H8v-2zm-4 5h2v2H4v-2zm4 0h12v2H8v-2z"></path>
        </svg>
    </button>
</div>


