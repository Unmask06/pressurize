<template>
  <div class="settings-panel">
    <div class="panel-header">
      <h2>⚙️ Settings</h2>
      <p>Configure simulation parameters</p>
    </div>

    <div class="panel-content">
      <div class="form-group">
        <label>Step Time (dt)</label>
        <input
          type="number"
          v-model.number="localDt"
          step="0.5"
          min="0.5"
          placeholder="0.5"
        />
        <small>Time step for simulation (seconds)</small>
      </div>

      <div class="form-group">
        <label>Max Simulation Time</label>
        <input
          type="number"
          v-model.number="localMaxSimTime"
          step="50"
          min="1"
          placeholder="10000"
        />
        <small>Maximum simulation duration (seconds)</small>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

const props = defineProps<{
  currentDt: number;
  currentMaxSimTime: number;
}>();

const emit = defineEmits<{
  update: [settings: { dt: number; maxSimTime: number }];
}>();

const localDt = ref(props.currentDt);
const localMaxSimTime = ref(props.currentMaxSimTime);

// Sync props to local state
watch(
  () => props.currentDt,
  (newVal) => (localDt.value = newVal),
);
watch(
  () => props.currentMaxSimTime,
  (newVal) => (localMaxSimTime.value = newVal),
);

watch([localDt, localMaxSimTime], () => {
  emit("update", {
    dt: localDt.value,
    maxSimTime: localMaxSimTime.value,
  });
});
</script>

<style scoped>
@import "tailwindcss";

.settings-panel {
  @apply h-full flex flex-col;
  background-color: var(--xergiz-panel);
}

.panel-header {
  @apply border-b p-6;
  border-color: var(--xergiz-border);
}

.panel-header h2 {
  @apply text-xl font-bold m-0;
  color: var(--xergiz-text);
}

.panel-header p {
  @apply text-sm mt-1 mb-0;
  color: var(--xergiz-text-muted);
}

.panel-content {
  @apply flex-1 p-6 flex flex-col gap-6;
}

.form-group {
  @apply flex flex-col gap-2;
}

.form-group label {
  @apply text-[10px] font-bold uppercase tracking-wider;
  color: var(--xergiz-text-muted);
}

.form-group input {
  @apply py-2 px-3 border rounded-lg text-sm transition-all duration-200;
  background-color: var(--xergiz-dark);
  border-color: var(--xergiz-border);
  color: var(--xergiz-text);
}

.form-group input:hover {
  border-color: var(--xergiz-teal);
}

.form-group input:focus {
  @apply outline-none ring-2;
  border-color: var(--xergiz-teal);
  ring-color: var(--xergiz-teal-dim);
}

.form-group small {
  @apply text-[10px];
  color: var(--xergiz-text-muted);
}
</style>
