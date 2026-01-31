<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Simulation Data Results</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Time ({{ getUnit("time") }})</th>
              <th>P Up ({{ getUnit("pressure") }})</th>
              <th>P Down ({{ getUnit("pressure") }})</th>
              <th>dP/dt Up</th>
              <th>dP/dt Down</th>
              <th>Flow ({{ getUnit("mass") }}/s)</th>
              <th>Valve (%)</th>
              <th>Regime</th>
              <th>Z</th>
              <th>k</th>
              <th>M (g/mol)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in data" :key="idx">
              <td>{{ row.time?.toFixed(2) ?? "-" }}</td>
              <td>{{ row.upstream_pressure?.toFixed(1) ?? "-" }}</td>
              <td>{{ row.downstream_pressure?.toFixed(1) ?? "-" }}</td>
              <td>{{ row.dp_dt_upstream?.toFixed(6) ?? "-" }}</td>
              <td>{{ row.dp_dt_downstream?.toFixed(6) ?? "-" }}</td>
              <td>{{ row.flowrate?.toFixed(1) ?? "-" }}</td>
              <td>{{ row.valve_opening_pct?.toFixed(1) ?? "-" }}</td>
              <td>{{ row.flow_regime ?? "-" }}</td>
              <td>{{ row.z_factor?.toFixed(4) ?? "-" }}</td>
              <td>{{ row.k_ratio?.toFixed(4) ?? "-" }}</td>
              <td>{{ row.molar_mass?.toFixed(2) ?? "-" }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getUnit } from "../api/client";

const props = defineProps<{
  data: any[];
}>();

const emit = defineEmits(["close"]);
</script>

<style scoped>
@import "tailwindcss";

/* Component-specific modal sizing */
.modal-content {
  @apply w-[95%] max-w-[1200px] max-h-[85vh];
}

.table-container {
  @apply overflow-auto p-0 flex-1;
}

table {
  @apply w-full border-collapse text-sm text-slate-800;
}

th {
  @apply sticky top-0 bg-slate-100 p-4 text-left border-b-2 border-slate-200 font-semibold whitespace-nowrap;
}

td {
  @apply py-3 px-4 border-b border-slate-200 whitespace-nowrap;
}

tr:hover {
  @apply bg-slate-100;
}
</style>
