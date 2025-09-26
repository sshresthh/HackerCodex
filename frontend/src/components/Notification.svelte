<script lang="ts">
    export let message: string = '';
    export let type: 'info' | 'error' | 'success' = 'info';
    export let onClose: () => void = () => {};
</script>

{#if message}
    <div class="notice {type}">
        <span class="notice-text">{message}</span>
        <button class="notice-close" aria-label="Close" on:click={onClose}>×</button>
    </div>
{/if}


