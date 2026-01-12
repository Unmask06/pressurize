<template>
  <div class="kpi-grid">
    <KpiCard
      label="Peak Flow Rate"
      :value="peakFlow"
      unit="lb/hr"
      icon="📈"
      color="flow"
      :loading="loading"
    />
    <KpiCard
      label="Final Pressure"
      :value="finalPressure"
      unit="psig"
      icon="🎯"
      color="pressure"
      :decimals="2"
      :loading="loading"
    />
    <KpiCard
      label="Equilibrium Time"
      :value="equilibriumTime"
      unit="seconds"
      icon="⏱️"
      color="time"
      :decimals="1"
      :loading="loading"
    />
    <KpiCard
      label="Total Mass Flow"
      :value="totalMass"
      unit="lb"
      icon="⚖️"
      color="mass"
      :decimals="1"
      :loading="loading"
    />
  </div>
</template>

<script setup lang="ts">
import KpiCard from "./KpiCard.vue";

const props = defineProps<{
  peakFlow: number;
  finalPressure: number;
  equilibriumTime: number;
  totalMass: number;
  loading?: boolean;
}>();
</script>

<style scoped>
@reference "tailwindcss";

.kpi-grid {
  @apply grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-6 mb-8;
}
</style>
