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
  return sys
    .replace(/_/g, " ")
    .split(" ")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}

function getSystemIcon(sys: string): string {
  switch (sys.toLowerCase()) {
    case "imperial":
      return "🇺🇸";
    case "us":
      return "🏛️";
    case "si":
      return "🌍";
    case "engg_si":
      return "🔧";
    case "engg_field":
      return "🏗️";
    case "cgs":
      return "📊";
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

.system-options {
  @apply flex flex-col gap-3;
}

.system-option {
  @apply flex items-center gap-3 py-3 px-4 border rounded-lg cursor-pointer transition-all duration-200 text-left;
  background-color: var(--xergiz-dark);
  border-color: var(--xergiz-border);
}

.system-option:hover {
  border-color: var(--xergiz-teal);
  background-color: var(--xergiz-teal-dim);
}

.system-option.active {
  @apply ring-2;
  border-color: var(--xergiz-teal);
  background-color: var(--xergiz-teal-dim);
  ring-color: var(--xergiz-teal-glow);
}

.system-icon {
  @apply text-2xl;
}

.system-name {
  @apply text-sm font-semibold;
  color: var(--xergiz-text);
}

.system-option.active .system-name {
  color: var(--xergiz-teal);
}
</style>
