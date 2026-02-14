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

.form-group {
  @apply flex flex-col gap-2;
}

.form-group label {
  @apply text-xs text-slate-500 font-bold uppercase tracking-wider;
}

.form-group input {
  @apply py-3 px-4 border border-slate-200 rounded-lg bg-slate-50 text-slate-800 text-base transition-all duration-200;
}

.form-group input:hover {
  @apply border-slate-300 bg-white;
}

.form-group input:focus {
  @apply outline-none border-blue-500 ring-4 ring-blue-500/10 bg-white;
}

.form-group small {
  @apply text-xs text-slate-400;
}

</style>
