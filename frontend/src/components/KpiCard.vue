<template>
  <div class="kpi-card" :class="color">
    <div class="kpi-icon">{{ icon }}</div>
    <div class="kpi-content">
      <div class="kpi-label">{{ label }}</div>
      <div class="kpi-value">{{ formattedValue }}</div>
      <div class="kpi-unit">{{ unit }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  label: string;
  value: number;
  unit: string;
  icon: string;
  color: string;
  decimals?: number;
}>();

const formattedValue = computed(() => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: props.decimals ?? 0,
    maximumFractionDigits: props.decimals ?? 0,
  }).format(props.value);
});
</script>

<style scoped>
@import "tailwindcss";

.kpi-card {
    @apply bg-white rounded-xl p-6 flex items-center gap-4 shadow-sm transition-all duration-200 border border-slate-200;
}

.kpi-card:hover {
    @apply -translate-y-0.5 shadow-md;
}

.kpi-icon {
    @apply text-3xl bg-slate-100 p-3 rounded-full leading-none;
}

.kpi-content {
    @apply flex flex-col;
}

.kpi-label {
    @apply text-sm text-slate-500 font-medium mb-1;
}

.kpi-value {
    @apply text-2xl font-bold text-slate-800 leading-tight;
}

.kpi-unit {
    @apply text-xs text-slate-400;
}

/* Specific accent colors */
.kpi-card.flow .kpi-value {
    @apply text-red-500;
}

.kpi-card.pressure .kpi-value {
    @apply text-blue-500;
}

.kpi-card.time .kpi-value {
    @apply text-emerald-500;
}

.kpi-card.mass .kpi-value {
    @apply text-violet-500;
}
</style>
