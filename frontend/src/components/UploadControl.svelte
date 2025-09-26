<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher<{ file: File }>();

    export let disabled: boolean = false;
    let inputEl: HTMLInputElement;

    function handleChange(e: Event) {
        const file = (e.currentTarget as HTMLInputElement).files?.[0];
        if (file) dispatch('file', file);
        if (inputEl) inputEl.value = '';
    }
</script>

<button
    class="button upload-button"
    aria-label="Upload event poster"
    onclick={() => !disabled && inputEl && inputEl.click()}
    disabled={disabled}
>
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="#1f2937"><path d="M19 15v4H5v-4H3v4c0 1.103.897 2 2 2h14c1.103 0 2-.897 2-2v-4h-2z"></path><path d="M11 6.414V16h2V6.414l3.293 3.293 1.414-1.414L12 2.586 6.293 8.293l1.414 1.414z"></path></svg>
    <span class="tooltip">upload</span>
    <input class="visually-hidden" type="file" accept="image/*" capture="environment" bind:this={inputEl} onchange={handleChange} />
</button>


