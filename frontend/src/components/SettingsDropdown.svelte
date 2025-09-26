<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    export let open: boolean;
    export let darkMode: boolean;
    const dispatch = createEventDispatcher<{ toggleTheme: void }>();
</script>

{#if open}
    <div class="settings-dropdown">
        <div class="settings-header">
            <h3>Settings</h3>
        </div>
        <div class="settings-content">
            <div class="setting-item">
                <div class="setting-info">
                    <span class="setting-label">Theme</span>
                    <span class="setting-description">Switch between light and dark mode</span>
                </div>
                <label>
                    <input class="toggle-checkbox" type="checkbox" checked={darkMode} on:change={() => dispatch('toggleTheme')} />
                    <div class="toggle-slot">
                        <div class="sun-icon-wrapper">
                            <div class="iconify sun-icon"></div>
                        </div>
                        <div class="toggle-button"></div>
                        <div class="moon-icon-wrapper">
                            <div class="iconify moon-icon"></div>
                        </div>
                    </div>
                </label>
            </div>
        </div>
    </div>
{/if}


