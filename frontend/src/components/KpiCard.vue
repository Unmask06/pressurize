<template>
  <div class="kpi-card" :class="color">
    <div class="kpi-icon">{{ icon }}</div>
    <div class="kpi-content">
      <div class="kpi-label">{{ label }}</div>
      <div class="kpi-value" v-if="!loading">{{ formattedValue }}</div>
      <div class="kpi-value loading" v-else>
        <span class="loading-dots">•••</span>
      </div>
      <div class="kpi-unit">{{ unit }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  label: string;
  value: number;
  unit: string;
  icon: string;
  color: string;
  decimals?: number;
  loading?: boolean;
}>();

const formattedValue = computed(() => {
  const value = props.value;

  // Use compact notation for large numbers
  if (Math.abs(value) >= 1_000_000) {
    return new Intl.NumberFormat("en-US", {
      notation: "compact",
      compactDisplay: "short",
      maximumFractionDigits: 2,
    }).format(value);
  } else if (Math.abs(value) >= 10_000) {
    return new Intl.NumberFormat("en-US", {
      notation: "compact",
      compactDisplay: "short",
      maximumFractionDigits: 1,
    }).format(value);
  }

  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: props.decimals ?? 0,
    maximumFractionDigits: props.decimals ?? 0,
  }).format(value);
});
</script>

<style scoped>
@import "tailwindcss";

.kpi-card {
  @apply bg-white rounded-lg p-2 sm:p-3 flex flex-row items-center gap-2 shadow-sm transition-all duration-200 border border-slate-200;
}

.kpi-card:hover {
  @apply -translate-y-0.5 shadow-md;
}

.kpi-icon {
  @apply text-lg sm:text-xl bg-slate-100 p-1.5 sm:p-2 rounded-lg leading-none flex-shrink-0;
}

.kpi-content {
  @apply flex flex-col flex-1;
}

.kpi-label {
  @apply text-xs text-slate-500 font-medium whitespace-nowrap;
}

.kpi-value {
  @apply text-sm sm:text-base md:text-lg font-bold text-slate-800 leading-tight whitespace-nowrap;
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

/* Loading state */
.kpi-value.loading {
  @apply text-slate-400;
}

.loading-dots {
  @apply inline-block;
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.3;
  }
  50% {
    opacity: 1;
  }
}
</style>
