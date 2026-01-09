<template>
  <div class="kpi-grid">
    <KpiCard
      label="Peak Flow Rate"
      :value="peakFlow"
      unit="lb/hr"
      icon="📈"
      color="flow"
    />
    <KpiCard
      label="Final Pressure"
      :value="finalPressure"
      unit="psig"
      icon="🎯"
      color="pressure"
      :decimals="1"
    />
    <KpiCard
      label="Equilibrium Time"
      :value="equilibriumTime"
      unit="seconds"
      icon="⏱️"
      color="time"
      :decimals="1"
    />
    <KpiCard
      label="Total Mass Flow"
      :value="totalMass"
      unit="lb"
      icon="⚖️"
      color="mass"
      :decimals="1"
    />
  </div>
</template>

<script setup lang="ts">
import KpiCard from './KpiCard.vue';

const props = defineProps<{
  peakFlow: number;
  finalPressure: number;
  equilibriumTime: number;
  totalMass: number;
}>();
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}
</style>
