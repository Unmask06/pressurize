<template>
  <div class="kpi-grid">
    <KpiCard
      label="Peak Flow Rate"
      :value="peakFlow"
      :unit="getUnit('mass_flow_rate')"
      icon="📈"
      color="flow"
      :loading="loading"
    />
    <KpiCard
      label="Final Pressure"
      :value="finalPressure"
      :unit="getUnit('Pressure')"
      icon="🎯"
      color="pressure"
      :decimals="2"
      :loading="loading"
    />
    <KpiCard
      label="Equilibrium Time"
      :value="equilibriumTime"
      :unit="getUnit('time')"
      icon="⏱️"
      color="time"
      :decimals="1"
      :loading="loading"
    />
    <KpiCard
      label="Total Mass Flow"
      :value="totalMass"
      :unit="getUnit('mass')"
      icon="⚖️"
      color="mass"
      :decimals="1"
      :loading="loading"
    />
  </div>
</template>

<script setup lang="ts">
import { getUnit } from "../api/client";
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
  @apply grid grid-cols-2 md:grid-cols-4 gap-2 sm:gap-3 md:gap-4;
}
</style>
