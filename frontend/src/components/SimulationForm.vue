<template>
  <div class="simulation-form">
    <div class="header-with-settings">
      <h3>Simulation Parameters</h3>
      <div class="settings-controls">
        <!-- Unit System Dropdown -->
        <div class="unit-selector">
          <label>Unit System:</label>
          <select
            :value="unitSystem"
            @change="
              (e) =>
                changeUnitSystem((e.target as HTMLSelectElement).value as UnitSystem)
            "
            class="unit-select"
          >
            <option v-for="sys in availableSystems" :key="sys" :value="sys">
              {{ formatSystemName(sys) }}
            </option>
          </select>
        </div>
        <button class="btn-icon" @click="$emit('edit-settings')">⚙️</button>
      </div>
    </div>

    <!-- Mode Selection -->
    <div class="section-container">
      <div class="section-header">📈 Simulation Mode</div>
      <div class="toggle-group">
        <button
          :class="{ active: form.mode === 'pressurize' }"
          @click="form.mode = 'pressurize'"
          title="Pressurize: upstream pressure constant, downstream evolves"
        >
          🔼 Pressurize
        </button>
        <button
          :class="{ active: form.mode === 'depressurize' }"
          @click="form.mode = 'depressurize'"
          title="Depressurize: downstream pressure constant, upstream evolves"
        >
          🔽 Depressurize
        </button>
        <button
          :class="{ active: form.mode === 'equalize' }"
          @click="form.mode = 'equalize'"
          title="Equalize: both upstream and downstream pressures evolve"
        >
          ⇌ Equalize
        </button>
      </div>
    </div>

    <div class="form-grid">
      <!-- Row 1: Upstream and Downstream side by side -->
      <div class="grid-row vessels-row">
        <!-- Upstream Section -->
        <div class="section-container">
          <div class="section-header">📤 Upstream Vessel</div>
          <div class="row">
            <div
              class="form-group"
              :class="form.mode !== 'pressurize' ? 'third' : 'half'"
            >
              <label>Pressure ({{ getUnit("Pressure") }})</label>
              <input type="number" v-model.number="form.p_up" />
            </div>
            <div
              class="form-group"
              :class="form.mode !== 'pressurize' ? 'third' : 'half'"
            >
              <label>Temperature ({{ getUnit("Temperature") }})</label>
              <input
                type="number"
                v-model.number="form.upstream_temp"
                step="5"
              />
            </div>
            <div class="form-group third" v-if="form.mode !== 'pressurize'">
              <label>Volume ({{ getUnit("volume") }})</label>
              <input type="number" v-model.number="form.upstream_volume" />
            </div>
          </div>
        </div>

        <!-- Downstream Section -->
        <div class="section-container">
          <div class="section-header">📥 Downstream Vessel</div>
          <div class="row">
            <div
              class="form-group"
              :class="form.mode !== 'depressurize' ? 'third' : 'half'"
            >
              <label>Pressure ({{ getUnit("pressure") }})</label>
              <input type="number" v-model.number="form.p_down_init" />
            </div>
            <div
              class="form-group"
              :class="form.mode !== 'depressurize' ? 'third' : 'half'"
            >
              <label>Temperature ({{ getUnit("temperature") }})</label>
              <input
                type="number"
                v-model.number="form.downstream_temp"
                step="5"
              />
            </div>
            <div class="form-group third" v-if="form.mode !== 'depressurize'">
              <label>Volume ({{ getUnit("volume") }})</label>
              <input type="number" v-model.number="form.downstream_volume" />
            </div>
          </div>
        </div>
      </div>

      <!-- Row 2: Valve Configuration (full width) -->
      <div class="grid-row full-width">
        <div class="section-container">
          <div class="section-header">🔧 Valve Configuration</div>
          <div class="row">
            <div class="form-group quarter">
              <label>Valve ID ({{ getUnit("small_length") }})</label>
              <input type="number" v-model.number="form.valve_id" />
            </div>
            <div class="form-group quarter">
              <label>Discharge Coeff (Cd)</label>
              <input
                type="number"
                v-model.number="form.discharge_coeff"
                step="0.05"
              />
            </div>
            <div class="form-group quarter">
              <label>Valve Action</label>
              <div class="toggle-group">
                <button
                  :class="{ active: form.valve_action === 'open' }"
                  @click="form.valve_action = 'open'"
                >
                  🔓 Open
                </button>
                <button
                  :class="{ active: form.valve_action === 'close' }"
                  @click="form.valve_action = 'close'"
                >
                  🔒 Close
                </button>
              </div>
            </div>
            <div class="form-group quarter">
              <label>{{
                form.valve_action === "close"
                  ? `Closing Time (${getUnit("time")})`
                  : `Opening Time (${getUnit("time")})`
              }}</label>
              <input type="number" v-model.number="form.opening_time" />
            </div>
          </div>

          <div class="row">
            <div class="form-group quarter">
              <label>{{
                form.valve_action === "close" ? "Closing Mode" : "Opening Mode"
              }}</label>
              <select v-model="form.opening_mode">
                <option value="linear">Linear</option>
                <option value="exponential">Exponential</option>
                <option value="quick_acting">Quick Acting</option>
                <option v-if="form.valve_action === 'open'" value="fixed">
                  Fixed (Instant)
                </option>
              </select>
            </div>
            <div
              class="form-group quarter"
              v-if="['exponential', 'quick_acting'].includes(form.opening_mode)"
            >
              <label>Curve Factor (k)</label>
              <input type="number" v-model.number="form.k_curve" step="0.1" />
            </div>
          </div>
        </div>
      </div>

      <!-- Row 3: Gas Properties (full width) -->
      <div class="grid-row full-width">
        <div class="section-container">
          <div class="section-header">🧪 Gas Properties</div>
          <div class="row">
            <div class="form-group half">
              <label>Property Mode</label>
              <div class="toggle-group">
                <button
                  :class="{ active: form.property_mode === 'manual' }"
                  @click="form.property_mode = 'manual'"
                >
                  Manual
                </button>
                <button
                  :class="{ active: form.property_mode === 'composition' }"
                  @click="form.property_mode = 'composition'"
                >
                  Composition
                </button>
              </div>
            </div>

            <div
              class="form-group half"
              v-show="form.property_mode === 'composition'"
            >
              <label>Composition</label>
              <div class="composition-summary-inline">
                <span class="summary-text">🧪 {{ compositionSummary }}</span>
                <button
                  class="btn-secondary"
                  @click="$emit('edit-composition')"
                >
                  ✏️ Edit
                </button>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="form-group third">
              <label title="Molar Mass">MW (g/mol)</label>
              <input
                type="number"
                v-model.number="form.molar_mass"
                step="0.1"
                :disabled="form.property_mode === 'composition'"
                :class="{ 'read-only': form.property_mode === 'composition' }"
              />
            </div>
            <div class="form-group third">
              <label title="Z-Factor">Z-Factor</label>
              <input
                type="number"
                v-model.number="form.z_factor"
                step="0.01"
                :disabled="form.property_mode === 'composition'"
                :class="{ 'read-only': form.property_mode === 'composition' }"
              />
            </div>
            <div class="form-group third">
              <label title="Heat Capacity Ratio">k (Cp/Cv)</label>
              <input
                type="number"
                v-model.number="form.k_ratio"
                step="0.01"
                :disabled="form.property_mode === 'composition'"
                :class="{ 'read-only': form.property_mode === 'composition' }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="actions">
      <button
        type="button"
        class="btn-table"
        @click="viewResults"
        :disabled="resultsEmpty"
      >
        {{ resultsEmpty ? "No Data Available" : "📊 View Results Table" }}
      </button>

      <button
        type="button"
        :class="buttonClass"
        @click="loading ? stopSimulation() : runSimulation()"
      >
        {{ buttonText }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from "vue";
import {
  apiClient,
  getUnit,
  getUnitSystem,
  setUnitSystem,
  unitConfig,
  type SimulationRequest,
  type UnitSystem,
} from "../api/client";

const props = defineProps<{
  loading: boolean;
  initialComposition?: string;
  resultsEmpty: boolean;
  currentDt: number;
  simulationCompleted: boolean;
}>();

const emit = defineEmits([
  "run",
  "stop",
  "edit-composition",
  "view-results",
  "edit-settings",
  "unit-system-changed",
]);

function viewResults() {
  emit("view-results");
}

const unitSystem = computed(() => getUnitSystem());
const availableSystems = computed(() => unitConfig.systems);

function formatSystemName(sys: string): string {
  // Simple capitalization
  return sys.charAt(0).toUpperCase() + sys.slice(1);
}

// Use the auto-generated SimulationRequest type from the API schema
const form = reactive<SimulationRequest>({
  mode: "equalize",
  p_up: 500,
  p_down_init: 0,
  upstream_volume: 100,
  downstream_volume: 100,
  valve_id: 2.0, // Default 2 inches
  opening_time: 5,
  valve_action: "open",
  upstream_temp: 70,
  downstream_temp: 70,
  molar_mass: 28.97,
  z_factor: 1.0,
  k_ratio: 1.4,
  discharge_coeff: 0.9,
  opening_mode: "linear",
  k_curve: 4.0,
  property_mode: "composition",
  composition: "Methane=1.0",
  dt: 0.05,
});

function changeUnitSystem(system: UnitSystem) {
  setUnitSystem(system);
  // Emit event to parent to clear all results since they're in the old unit system
  emit("unit-system-changed");
}

// Reset opening_mode to linear if switching to close while on fixed
watch(
  () => form.valve_action,
  (action) => {
    if (action === "close" && form.opening_mode === "fixed") {
      form.opening_mode = "linear";
    }
  },
);

watch(
  () => props.initialComposition,
  (newVal) => {
    if (newVal) form.composition = newVal;
  },
  { immediate: true },
);

watch(
  () => props.currentDt,
  (newVal) => {
    if (newVal !== undefined) form.dt = newVal;
  },
  { immediate: true },
);

// Auto-calculate properties in composition mode based on mode and conditions
watch(
  [
    () => form.property_mode,
    () => form.composition,
    () => form.mode,
    () => form.upstream_temp,
    () => form.downstream_temp,
    () => form.p_up,
    () => form.p_down_init,
  ],
  async ([propMode, comp, simMode, tempUp, tempDown, pressUp, pressDown]) => {
    if (propMode === "composition" && comp) {
      try {
        // Use upstream conditions for pressurize/equalize, downstream for depressurize
        const temp = simMode === "depressurize" ? tempDown : tempUp;
        const press = simMode === "depressurize" ? pressDown : pressUp;
        const res = await apiClient.post("/properties", {
          composition: comp,
          pressure: press || 0,
          temp: temp || 70,
        });
        form.molar_mass = Number(res.data.M.toFixed(2));
        form.z_factor = Number(res.data.Z.toFixed(4));
        form.k_ratio = Number(res.data.k.toFixed(4));
      } catch (e) {
        console.error("Property calculation failed", e);
      }
    }
  },
);

const compositionSummary = computed(() => {
  if (!form.composition) return "No composition";
  const parts = form.composition.split(",").length;
  return `${parts} Component${parts > 1 ? "s" : ""}`;
});

function runSimulation() {
  emit("run", { ...form });
}

function stopSimulation() {
  emit("stop");
}

// Compute button text and style based on state
const buttonText = computed(() => {
  if (props.loading) {
    return "⏹ Stop Simulation";
  }
  if (!props.simulationCompleted && !props.resultsEmpty) {
    return "▶ Run Simulation (Partial Data)";
  }
  return "▶ Run Simulation";
});

const buttonClass = computed(() => {
  return props.loading ? "btn-stop" : "btn-primary";
});

// Method to load parameters from history
function loadParameters(params: Record<string, any>) {
  Object.assign(form, params);
}

// Expose method for parent component to use
defineExpose({
  loadParameters,
});
</script>

<style scoped>
@import "tailwindcss";

.simulation-form {
  @apply bg-white p-8 rounded-2xl border border-slate-200 flex flex-col gap-6 h-full overflow-y-auto;
  width: 100%;
}

.form-grid {
  @apply flex flex-col gap-4;
}

.grid-row {
  @apply flex flex-col gap-4;
}

.grid-row.vessels-row {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4;
}

.grid-row.full-width {
  @apply w-full;
}

.quarter {
  @apply flex-1 min-w-30;
}

.actions {
  @apply flex flex-col gap-3 mt-4;
}

h3 {
  @apply m-0 text-2xl font-bold text-slate-800 tracking-tight;
}

.settings-controls {
  @apply flex items-center gap-3;
}

.unit-selector {
  @apply flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-2 py-1;
}

.unit-selector label {
  @apply text-[10px] uppercase font-bold text-slate-400 mb-0;
}

.unit-select {
  @apply border-none bg-transparent py-1 px-1 text-sm font-semibold text-slate-700 cursor-pointer outline-none focus:ring-0 w-auto;
}

.form-group {
  @apply flex flex-col gap-1.5;
}

.row {
  @apply flex flex-wrap gap-4;
}

.half {
  @apply flex-1 min-w-50;
}

.third {
  @apply flex-1 min-w-35;
}

label {
  @apply text-xs text-slate-500 font-bold uppercase tracking-wider;
}

input,
select {
  @apply py-3 px-4 border border-slate-200 rounded-lg bg-slate-50 text-slate-800 text-base transition-all duration-200;
}

input:hover,
select:hover {
  @apply border-slate-300 bg-white;
}

input:focus,
select:focus {
  @apply outline-none border-blue-500 ring-4 ring-blue-500/10 bg-white;
}

hr {
  @apply border-none border-t border-slate-100 my-2;
}

.toggle-group {
  @apply flex bg-slate-100 p-1.5 rounded-xl gap-1;
}

.toggle-group button {
  @apply flex-1 py-2 px-3 border-none bg-transparent text-slate-600 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-200;
}

.toggle-group button.active {
  @apply bg-white text-blue-600 shadow-md shadow-blue-500/10;
}

input.read-only {
  @apply bg-slate-100 text-slate-400 cursor-not-allowed border-dashed;
}

.composition-summary {
  @apply flex items-center justify-between bg-blue-50/50 py-3 px-4 rounded-xl border border-blue-100;
}

.summary-card {
  @apply flex items-center gap-3;
}

.summary-icon {
  @apply text-xl;
}

.summary-text {
  @apply text-sm font-semibold text-blue-900;
}

.composition-summary-inline {
  @apply flex items-center gap-2 bg-blue-50/50 py-2 px-3 rounded-lg border border-blue-100;
}

.btn-table {
  @apply py-3 px-4 bg-white border-2 border-slate-200 text-slate-600 rounded-xl font-bold cursor-pointer transition-all hover:bg-slate-50 hover:border-slate-300 hover:text-slate-800 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply py-4 px-6 bg-blue-600 text-white rounded-xl font-bold text-lg shadow-lg shadow-blue-600/20 active:scale-[0.98] transition-all hover:bg-blue-700 disabled:bg-slate-300 disabled:shadow-none;
}

.btn-stop {
  @apply py-4 px-6 bg-red-600 text-white rounded-xl font-bold text-lg shadow-lg shadow-red-600/20 active:scale-[0.98] transition-all hover:bg-red-700;
}

.btn-secondary {
  @apply py-1.5 px-3 rounded-lg text-blue-600 text-xs font-bold uppercase tracking-wider bg-white border border-blue-100;
}

.btn-secondary:hover {
  @apply bg-blue-50 border-blue-200;
}

.header-with-settings {
  @apply flex justify-between items-center;
}

.btn-icon {
  @apply bg-slate-100 border-none cursor-pointer text-xl p-2 rounded-xl w-10 h-10 flex justify-center items-center transition-all hover:bg-slate-200 hover:rotate-90 active:scale-90;
}

.section-container {
  @apply bg-slate-50/50 p-5 rounded-2xl border border-slate-100 flex flex-col gap-4;
}

.section-header {
  @apply text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2;
}

.section-header::after {
  content: "";
  @apply h-px bg-slate-100 flex-1;
}

small {
  @apply text-[10px] text-slate-400 font-medium;
}
</style>
