<script lang="ts">
  export let visible: boolean = false;
  export let message: string = 'Processing…';
</script>

{#if visible}
  <div class="overlay" role="alert" aria-busy="true">
    <div class="box">
      <div class="spinner" aria-hidden="true"></div>
      <div class="text">{message}</div>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    z-index: 1300;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.45);
  }
  .box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 14px 18px;
    border-radius: 12px;
    background: rgba(17, 24, 39, 0.92);
    border: 1px solid rgba(255,255,255,0.06);
    color: #e5e7eb;
  }
  .spinner {
    width: 44px;
    height: 44px;
    border-radius: 9999px;
    border: 3px solid rgba(255,255,255,0.15);
    border-top-color: #22d3ee;
    animation: spin 0.9s linear infinite;
  }
  .text { font-weight: 700; letter-spacing: 0.2px; }

  @keyframes spin { to { transform: rotate(360deg); } }

  @media (max-width: 640px) {
    .box { padding: 12px 14px; }
  }
</style>
