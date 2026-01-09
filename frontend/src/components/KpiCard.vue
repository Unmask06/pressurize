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

<style scoped src="../styles/KpiCard.css"></style>
