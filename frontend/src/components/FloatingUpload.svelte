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

<div class="fab-upload">
	<button
		type="button"
		class="fab-button"
		aria-label="Upload event poster"
		disabled={disabled}
		onclick={(e) => { e.preventDefault(); !disabled && inputEl && inputEl.click(); }}
	>
		<!-- Camera icon -->
		<svg class="fab-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ffffff" aria-hidden="true">
			<path d="M9 3l-1.172 2H5a2 2 0 00-2 2v10a2 2 0 002 2h14a2 2 0 002-2V7a2 2 0 00-2-2h-2.828L15 3H9zm3 14a5 5 0 110-10 5 5 0 010 10zm0-2a3 3 0 100-6 3 3 0 000 6z"></path>
		</svg>
	</button>
	<input class="visually-hidden" type="file" accept="image/*" capture="environment" bind:this={inputEl} onchange={handleChange} />
</div>


