<template>
  <div class="unit-system-panel">
    <div class="panel-header">
      <h2>📏 Unit System</h2>
      <p>Unit conversion preferences</p>
    </div>

    <div class="panel-content">
      <div class="coming-soon">
        <div class="icon">🚧</div>
        <h3>Coming Soon</h3>
        <p>Unit system switching is under development</p>
      </div>

      <div class="current-system">
        <label>Current Unit System</label>
        <div class="badge">
          <span class="flag">🇺🇸</span>
          <span class="text">Imperial Units</span>
        </div>
      </div>

      <div class="info-box">
        <h4>Planned Features</h4>
        <ul>
          <li>✓ SI (Metric) units</li>
          <li>✓ Imperial units</li>
          <li>✓ Automatic conversion</li>
          <li>✓ Persistent preferences</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Placeholder component for future unit system switching
</script>

<style scoped>
@import "tailwindcss";

.unit-system-panel {
  @apply h-full flex flex-col;
}

.panel-header {
  @apply border-b border-slate-200 p-6;
}

.panel-header h2 {
  @apply text-xl font-bold text-slate-800 m-0;
}

.panel-header p {
  @apply text-sm text-slate-500 mt-1 mb-0;
}

.panel-content {
  @apply flex-1 p-6 flex flex-col gap-6;
}

.coming-soon {
  @apply text-center py-8 px-4;
}

.coming-soon .icon {
  @apply text-5xl mb-4;
}

.coming-soon h3 {
  @apply text-lg font-bold text-slate-700 m-0 mb-2;
}

.coming-soon p {
  @apply text-sm text-slate-500 m-0;
}

.current-system {
  @apply flex flex-col gap-2;
}

.current-system label {
  @apply text-xs text-slate-500 font-bold uppercase tracking-wider;
}

.badge {
  @apply flex items-center gap-3 bg-blue-50 border border-blue-200 rounded-lg py-3 px-4;
}

.badge .flag {
  @apply text-2xl;
}

.badge .text {
  @apply text-sm font-semibold text-blue-900;
}

.info-box {
  @apply bg-slate-50 border border-slate-200 rounded-lg p-4;
}

.info-box h4 {
  @apply text-sm font-bold text-slate-700 m-0 mb-3;
}

.info-box ul {
  @apply list-none p-0 m-0 flex flex-col gap-2;
}

.info-box li {
  @apply text-sm text-slate-600;
}
</style>
