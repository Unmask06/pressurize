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
              <th>
                dP/dt Up ({{ getUnit("pressure") }}/{{ getUnit("time") }})
              </th>
              <th>
                dP/dt Down ({{ getUnit("pressure") }}/{{ getUnit("time") }})
              </th>
              <th>Flow ({{ getUnit("mass_flow_rate") }})</th>
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
  @apply w-[95%] max-w-300 max-h-[85vh];
}

.table-container {
  @apply overflow-auto p-0 flex-1;
}

table {
  @apply w-full border-collapse text-sm;
  color: var(--xergiz-text);
}

th {
  @apply sticky top-0 p-4 text-left border-b-2 font-semibold whitespace-nowrap text-xs uppercase tracking-wider;
  background: var(--xergiz-panel);
  border-color: var(--xergiz-border);
  color: var(--xergiz-text-muted);
}

td {
  @apply py-3 px-4 border-b whitespace-nowrap;
  background: var(--xergiz-surface);
  border-color: var(--xergiz-border);
}

tr:hover td {
  background: color-mix(in srgb, var(--xergiz-surface) 80%, white 20%);
}
</style>
