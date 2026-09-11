<template>
  <div class="simulation-form">
    <h3>Simulation Parameters</h3>

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
            <div class="form-group full">
              <label>Flow Model</label>
              <div class="toggle-group">
                <button
                  :class="{ active: form.flow_model === 'orifice' }"
                  @click="form.flow_model = 'orifice'"
                  title="Orifice ID-based flow (ISO 5167-2)"
                >
                  🔧 Orifice ID
                </button>
                <button
                  :class="{ active: form.flow_model === 'cv' }"
                  @click="form.flow_model = 'cv'"
                  title="Valve Cv-based flow (ISA/IEC 60534)"
                >
                  📊 Cv
                </button>
              </div>
            </div>
          </div>
          <div class="two-col-row">
            <template v-if="form.flow_model === 'orifice'">
              <div class="form-group">
                <label>Valve ID ({{ getUnit("small_length") }})</label>
                <input type="number" v-model.number="form.valve_id" />
              </div>
              <div class="form-group">
                <label>Discharge Coeff (Cd)</label>
                <input
                  type="number"
                  v-model.number="form.discharge_coeff"
                  step="0.5"
                />
              </div>
            </template>
            <template v-else>
              <div class="form-group">
                <label>Cv (gpm/√psi)</label>
                <input
                  type="number"
                  v-model.number="form.cv_value"
                  step="1"
                  min="0"
                />
              </div>
              <div class="form-group">
                <label>xT</label>
                <input
                  type="number"
                  v-model.number="form.x_t"
                  step="0.05"
                  min="0.1"
                  max="1"
                />
              </div>
            </template>
          </div>
          <div class="row">
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
            <div
              class="form-group quarter"
              v-if="form.opening_mode !== 'orifice'"
            >
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
                <option v-if="form.valve_action === 'open'" value="orifice">
                  Orifice (Instant)
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

    <!-- Tag -->
    <div class="tag-row">
      <label>🏷️ Tag</label>
      <input
        type="text"
        v-model.trim="tag"
        placeholder="Optional label for this run"
        class="tag-input"
        maxlength="50"
      />
    </div>

    <div class="actions">
      <button
        type="button"
        class="btn-table"
        @click="viewResults"
        :disabled="resultsEmpty"
        title="View Results Table"
      >
        📊
      </button>

      <button
        type="button"
        :class="buttonClass"
        @click="loading ? stopSimulation() : runSimulation()"
        :title="buttonText"
      >
        {{ buttonText.split(" ")[0] }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { apiClient, getUnit, type SimulationRequest } from "../api/client";

const props = defineProps<{
  loading: boolean;
  initialComposition?: string;
  resultsEmpty: boolean;
  currentDt: number;
  simulationCompleted: boolean;
}>();

const emit = defineEmits(["run", "stop", "edit-composition", "view-results"]);

function viewResults() {
  emit("view-results");
}

const tag = ref("");

// Use the auto-generated SimulationRequest type from the API schema
const form = reactive<SimulationRequest>({
  mode: "equalize",
  p_up: 500,
  p_down_init: 0,
  upstream_volume: 100,
  downstream_volume: 100,
  valve_id: 2.0, // Default 2 inches
  flow_model: "orifice",
  cv_value: undefined,
  x_t: 0.7,
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
  dt: 0.5,
});

// Reset opening_mode to linear if switching to close while on orifice
watch(
  () => form.valve_action,
  (action) => {
    if (action === "close" && form.opening_mode === "orifice") {
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
  emit("run", { ...form, _tag: tag.value || undefined });
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
  @apply p-5 flex flex-col gap-4 h-full overflow-y-auto;
  background: transparent;
  width: 100%;
}

.form-grid {
  @apply flex flex-col gap-3;
}

.grid-row {
  @apply flex flex-col gap-3;
}

.grid-row.vessels-row {
  @apply grid grid-cols-1 xl:grid-cols-2 gap-3;
}

.grid-row.full-width {
  @apply w-full;
}

.quarter {
  @apply flex-1 min-w-[20%];
}

.full {
  @apply w-full;
}

.two-col-row {
  @apply grid grid-cols-2 gap-3;
}

.actions {
  @apply flex gap-3 mt-3 justify-center;
}

.actions button {
  @apply flex-1 max-w-xs;
}

h3 {
  @apply m-0 text-base font-semibold tracking-tight;
  color: var(--xergiz-text);
}

.form-group {
  @apply flex flex-col gap-1;
}

.row {
  @apply flex flex-wrap gap-3;
}

.half {
  @apply flex-1 min-w-[45%];
}

.third {
  @apply flex-1 min-w-[30%];
}

label {
  @apply text-[10px] font-semibold uppercase tracking-wider;
  color: var(--xergiz-text-muted);
}

input,
select {
  @apply w-full py-1.5 px-3 border rounded-lg text-xs transition-all duration-150;
  background: var(--xergiz-dark);
  border-color: var(--xergiz-border);
  color: var(--xergiz-text);
}

input:hover,
select:hover {
  border-color: var(--xergiz-border-hover);
}

input:focus,
select:focus {
  @apply outline-none;
  border-color: var(--xergiz-teal);
  box-shadow: 0 0 0 3px var(--xergiz-teal-dim);
}

input::placeholder {
  color: var(--xergiz-text-muted);
}

hr {
  @apply border-none border-t my-2;
  border-color: var(--xergiz-border);
}

.toggle-group {
  @apply flex p-0.5 rounded-lg gap-0.5;
  background: var(--xergiz-dark);
  border: 1px solid var(--xergiz-border);
}

.toggle-group button {
  @apply flex-1 py-1.5 px-2 border-none bg-transparent rounded-md cursor-pointer text-[11px] font-semibold transition-all duration-150;
  color: var(--xergiz-text-muted);
}

.toggle-group button:hover:not(.active) {
  color: var(--xergiz-text);
  background: rgba(255, 255, 255, 0.03);
}

.toggle-group button.active {
  background: linear-gradient(135deg, #2dd4bf, #14b8a6);
  color: #020617;
  @apply shadow-sm;
}

input.read-only {
  @apply cursor-not-allowed border-dashed opacity-40;
}

.composition-summary {
  @apply flex items-center justify-between py-2 px-3 rounded-lg border;
  background: var(--xergiz-teal-dim);
  border-color: rgba(45, 212, 191, 0.15);
}

.summary-card {
  @apply flex items-center gap-3;
}

.summary-icon {
  @apply text-base;
}

.summary-text {
  @apply text-[11px] font-semibold;
  color: var(--xergiz-teal);
}

.composition-summary-inline {
  @apply flex items-center gap-2 py-1.5 px-3 rounded-lg border;
  background: var(--xergiz-teal-dim);
  border-color: rgba(45, 212, 191, 0.15);
}

.tag-row {
  @apply flex items-center gap-3;
}

.tag-row label {
  @apply text-[10px] font-semibold uppercase tracking-wider whitespace-nowrap mb-0;
  color: var(--xergiz-text-muted);
}

.tag-input {
  @apply flex-1 py-1.5 px-3 border rounded-lg text-xs transition-all duration-150;
  background: var(--xergiz-dark);
  border-color: var(--xergiz-border);
  color: var(--xergiz-text);
}

.tag-input:hover {
  border-color: var(--xergiz-border-hover);
}

.tag-input:focus {
  @apply outline-none;
  border-color: var(--xergiz-teal);
  box-shadow: 0 0 0 3px var(--xergiz-teal-dim);
}

.btn-table {
  @apply py-2 px-4 border rounded-xl font-bold cursor-pointer transition-all active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed text-xl;
  background: var(--xergiz-surface);
  border-color: var(--xergiz-border);
  color: var(--xergiz-text-muted);
}

.btn-table:hover:not(:disabled) {
  border-color: var(--xergiz-teal);
  color: var(--xergiz-teal);
  box-shadow: 0 0 15px var(--xergiz-teal-dim);
}

.btn-primary {
  @apply py-2 px-4 text-white rounded-xl font-bold text-lg active:scale-[0.98] transition-all disabled:opacity-40 disabled:shadow-none;
  background: linear-gradient(135deg, #f5a623, #e8911a);
  color: #020617;
  box-shadow: 0 4px 20px var(--xergiz-orange-glow);
}

.btn-primary:hover:not(:disabled) {
  filter: brightness(1.08);
  box-shadow: 0 4px 30px rgba(245, 166, 35, 0.4);
}

.btn-stop {
  @apply py-2 px-4 text-white rounded-xl font-bold text-lg active:scale-[0.98] transition-all;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.25);
}

.btn-stop:hover {
  box-shadow: 0 4px 30px rgba(239, 68, 68, 0.35);
}

.btn-secondary {
  @apply py-1 px-2 rounded-lg text-[10px] font-semibold uppercase tracking-wider border;
  background: transparent;
  color: var(--xergiz-teal);
  border-color: rgba(45, 212, 191, 0.2);
}

.btn-secondary:hover {
  background: var(--xergiz-teal-dim);
}

.section-container {
  @apply p-3.5 rounded-xl border flex flex-col gap-2.5;
  background: var(--xergiz-surface);
  border-color: var(--xergiz-border);
}

.section-header {
  @apply text-[10px] font-semibold uppercase tracking-widest flex items-center gap-2;
  color: var(--xergiz-teal);
}

.section-header::after {
  content: "";
  @apply h-px flex-1;
  background: linear-gradient(90deg, var(--xergiz-border-hover), transparent);
}

small {
  @apply text-[9px] font-medium;
  color: var(--xergiz-text-muted);
}
</style>
