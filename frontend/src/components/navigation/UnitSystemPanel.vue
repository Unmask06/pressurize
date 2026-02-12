<template>
  <div class="unit-system-panel">
    <div class="panel-header">
      <h2>📏 Unit System</h2>
      <p>Unit conversion preferences</p>
    </div>

    <div class="panel-content">
      <div class="system-options">
        <button
          v-for="sys in availableSystems"
          :key="sys"
          class="system-option"
          :class="{ active: unitSystem === sys }"
          @click="changeUnitSystem(sys)"
        >
          <span class="system-icon">{{ getSystemIcon(sys) }}</span>
          <span class="system-name">{{ formatSystemName(sys) }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import {
  getUnitSystem,
  setUnitSystem,
  unitConfig,
  type UnitSystem,
} from "../../api/client";

const emit = defineEmits<{
  "unit-system-changed": [];
}>();

const unitSystem = computed(() => getUnitSystem());
const availableSystems = computed(() => unitConfig.systems);

function formatSystemName(sys: string): string {
  return sys.charAt(0).toUpperCase() + sys.slice(1);
}

function getSystemIcon(sys: string): string {
  switch (sys.toLowerCase()) {
    case "imperial":
      return "🇺🇸";
    case "si":
    case "metric":
      return "🌍";
    default:
      return "📐";
  }
}

function changeUnitSystem(system: UnitSystem) {
  setUnitSystem(system);
  emit("unit-system-changed");
}
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

.system-options {
  @apply flex flex-col gap-3;
}

.system-option {
  @apply flex items-center gap-3 py-3 px-4 bg-white border border-slate-200 rounded-lg cursor-pointer transition-all duration-200 text-left;
}

.system-option:hover {
  @apply border-blue-300 bg-blue-50/30;
}

.system-option.active {
  @apply border-blue-500 bg-blue-50 ring-2 ring-blue-500/20;
}

.system-icon {
  @apply text-2xl;
}

.system-name {
  @apply text-sm font-semibold text-slate-700;
}

.system-option.active .system-name {
  @apply text-blue-700;
}
</style>
