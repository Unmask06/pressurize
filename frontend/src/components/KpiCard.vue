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
      maximumFractionDigits: 2,
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
  @apply rounded-xl p-3 flex flex-row items-center gap-2.5 transition-all duration-200 border;
  background: var(--xergiz-surface);
  border-color: var(--xergiz-border);
}

.kpi-card:hover {
  @apply -translate-y-0.5;
  border-color: var(--xergiz-border-hover);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.kpi-icon {
  @apply text-base p-2 rounded-lg leading-none shrink-0;
  background: var(--xergiz-teal-dim);
}

.kpi-content {
  @apply flex flex-col flex-1 gap-0;
}

.kpi-label {
  @apply text-[10px] font-medium whitespace-nowrap;
  color: var(--xergiz-text-muted);
}

.kpi-value {
  @apply text-base font-bold leading-tight whitespace-nowrap;
  color: var(--xergiz-text);
}

.kpi-unit {
  @apply text-[10px];
  color: var(--xergiz-text-muted);
}

/* Specific accent colors with glow */
.kpi-card.flow .kpi-icon {
  background: rgba(248, 113, 113, 0.12);
}
.kpi-card.flow .kpi-value {
  color: #f87171;
}

.kpi-card.pressure .kpi-icon {
  background: rgba(96, 165, 250, 0.12);
}
.kpi-card.pressure .kpi-value {
  color: #60a5fa;
}

.kpi-card.time .kpi-icon {
  background: rgba(52, 211, 153, 0.12);
}
.kpi-card.time .kpi-value {
  color: #34d399;
}

.kpi-card.mass .kpi-icon {
  background: rgba(167, 139, 250, 0.12);
}
.kpi-card.mass .kpi-value {
  color: #a78bfa;
}

/* Loading state */
.kpi-value.loading {
  color: var(--xergiz-text-muted);
}

.loading-dots {
  @apply inline-block;
  animation: pulse 1.2s ease-in-out infinite;
  color: var(--xergiz-teal);
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
