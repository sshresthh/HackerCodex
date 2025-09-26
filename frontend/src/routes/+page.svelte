<script lang="ts">
	import { onMount } from 'svelte';

	let message = 'Loading...';

	onMount(async () => {
		try {
			const response = await fetch('/api/test');
			const data = await response.json();
			message = data.message;
		} catch (error) {
			message = 'Failed to connect to the backend.';
			console.error(error);
		}
	});
</script>

<main class="flex min-h-screen flex-col items-center justify-center bg-gray-900 text-white">
	<div class="rounded-lg bg-gray-800 p-8 text-center shadow-lg">
		<h1 class="mb-4 text-4xl font-bold text-sky-400">FuseMap Demo</h1>
		<p class="text-xl">Message from the backend:</p>
		<p class="mt-2 rounded-md bg-gray-700 p-4 font-mono text-lg text-green-400">
			{message}
		</p>
	</div>
</main>