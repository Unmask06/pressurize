<template>
  <div class="simulation-form">
    <div class="header-with-settings">
      <h3>Simulation Parameters</h3>
      <button class="btn-icon" @click="$emit('edit-settings')">⚙️</button>
    </div>
    
    <div class="row">
      <div class="form-group half">
        <label>Upstream Pressure (psig)</label>
        <input type="number" v-model.number="form.p_up_psig" />
      </div>
      <div class="form-group half">
        <label>Downstream Pressure (psig)</label>
        <input type="number" v-model.number="form.p_down_init_psig" />
      </div>
    </div>

    <div class="row">
      <div class="form-group half">
        <label>Volume (ft³)</label>
        <input type="number" v-model.number="form.volume_ft3" />
      </div>
      <div class="form-group half">
        <label>Valve ID (in)</label>
        <input type="number" v-model.number="form.valve_id_inch" />
      </div>
    </div>

    <div class="form-group">
      <label>Opening Time (s)</label>
      <input type="number" v-model.number="form.opening_time_s" />
    </div>

    <div class="row">
      <div class="form-group half">
        <label>Opening Mode</label>
        <select v-model="form.opening_mode">
          <option value="linear">Linear</option>
          <option value="exponential">Exponential</option>
          <option value="quick_opening">Quick Opening</option>
          <option value="fixed">Fixed (Instant)</option>
        </select>
      </div>
      <div class="form-group half" v-if="['exponential', 'quick_opening'].includes(form.opening_mode)">
        <label>Curve Factor (k)</label>
        <input type="number" v-model.number="form.k_curve" step="0.1" />
      </div>
    </div>

    <hr />

    <div class="form-group">
      <label>Property Mode</label>
      <div class="toggle-group">
        <button 
          :class="{ active: form.property_mode === 'manual' }" 
          @click="form.property_mode = 'manual'"
        >Manual</button>
        <button 
          :class="{ active: form.property_mode === 'composition' }" 
          @click="form.property_mode = 'composition'"
        >Composition</button>
      </div>
    </div>

    <div v-show="form.property_mode === 'composition'" class="composition-summary">
      <div class="summary-card">
        <div class="summary-icon">🧪</div>
        <div class="summary-text">{{ compositionSummary }}</div>
      </div>
      <button class="btn-secondary" @click="$emit('edit-composition')">✏️ Edit</button>
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

    <div class="row">
       <div class="form-group half">
        <label>Temp (°F)</label>
        <input type="number" v-model.number="form.temp_f" step="5" />
      </div>
      <div class="form-group half">
        <label>Cd</label>
        <input type="number" v-model.number="form.discharge_coeff" step="0.05" />
      </div>
    </div>

    <button 
      type="button"
      class="btn-table" 
      @click="viewResults" 
      :disabled="resultsEmpty"
    >
      {{ resultsEmpty ? 'No Data Available' : '📊 View Results Table' }}
    </button>

    <button type="button" class="btn-primary" @click="runSimulation" :disabled="loading">
      {{ loading ? 'Running...' : 'Run Simulation' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, watch, ref } from 'vue';
import { apiClient } from '../api/client';

const props = defineProps<{
  loading: boolean;
  initialComposition?: string;
  resultsEmpty: boolean;
  currentDt: number;
}>();

const emit = defineEmits(['run', 'edit-composition', 'view-results', 'edit-settings']);

function viewResults() {
  emit('view-results');
}

const form = reactive({
  p_up_psig: 500,
  p_down_init_psig: 0,
  volume_ft3: 100,
  valve_id_inch: 2.0,
  opening_time_s: 5,
  temp_f: 70,
  molar_mass: 28.97,
  z_factor: 1.0,
  k_ratio: 1.4,
  discharge_coeff: 0.65,
  opening_mode: 'linear',
  k_curve: 4.0,
  property_mode: 'manual',
  composition: 'Methane=1.0',
  dt: 0.05
});

watch(() => props.initialComposition, (newVal) => {
  if (newVal) form.composition = newVal;
}, { immediate: true });

watch(() => props.currentDt, (newVal) => {
  if (newVal !== undefined) form.dt = newVal;
}, { immediate: true });

// Auto-calculate properties in composition mode
watch([
  () => form.property_mode,
  () => form.composition,
  () => form.temp_f,
  () => form.p_down_init_psig
], async ([mode, comp, temp, press]) => {
  if (mode === 'composition' && comp) {
    try {
      const res = await apiClient.post('/properties', {
        composition: comp,
        pressure_psig: press || 0,
        temp_f: temp || 70
      });
      form.molar_mass = Number(res.data.M.toFixed(2));
      form.z_factor = Number(res.data.Z.toFixed(4));
      form.k_ratio = Number(res.data.k.toFixed(4));
    } catch (e) {
      console.error("Property calculation failed", e);
    }
  }
});

const compositionSummary = computed(() => {
  if (!form.composition) return 'No composition';
  const parts = form.composition.split(',').length;
  return `${parts} Component${parts > 1 ? 's' : ''}`;
});

function runSimulation() {
  emit('run', { ...form });
}
</script>

<style scoped>
@import "tailwindcss";

.simulation-form {
    @apply bg-white p-6 rounded-xl border border-slate-200 flex flex-col gap-4 h-full overflow-y-auto;
}

h3 {
    @apply m-0 mb-2 text-xl font-semibold text-slate-800;
}

.form-group {
    @apply flex flex-col gap-1;
}

.row {
    @apply flex gap-3;
}

.half {
    @apply w-1/2;
}

.third {
    @apply w-1/3;
}

label {
    @apply text-sm text-slate-500 font-medium;
}

input,
select {
    @apply py-2.5 px-3 border border-slate-200 rounded-md bg-white text-slate-800 text-base transition-colors;
}

input:focus,
select:focus {
    @apply outline-none border-blue-500 ring-2 ring-blue-500/20;
}

hr {
    @apply border-none border-t border-slate-200 my-2;
}

.toggle-group {
    @apply flex bg-slate-100 p-1 rounded-md;
}

.toggle-group button {
    @apply flex-1 py-1.5 px-2 border-none bg-transparent text-slate-500 rounded cursor-pointer text-sm font-medium transition-all;
}

.toggle-group button.active {
    @apply bg-white text-blue-500 shadow-sm;
}

input.read-only {
    @apply bg-slate-100 text-slate-500 cursor-not-allowed border-dashed;
}

.composition-summary {
    @apply flex items-center justify-between bg-slate-100 py-2 px-3 rounded-lg border border-slate-200;
}

.summary-card {
    @apply flex items-center gap-2;
}

.btn-table {
    @apply mt-2 py-2.5 px-4 bg-transparent border border-blue-500 text-blue-500 rounded-lg font-semibold cursor-pointer transition-all;
}

.btn-table:hover:not(:disabled) {
    @apply bg-blue-500/10;
}

.btn-table:disabled {
    @apply opacity-50 cursor-not-allowed border-slate-200 text-slate-400;
}

/* Component-specific button styles */
.btn-primary {
    @apply mt-auto py-3 px-4 font-semibold transition-colors;
}

.btn-primary:hover {
    @apply bg-blue-600;
}

.btn-primary:disabled {
    @apply opacity-70 cursor-not-allowed;
}

.btn-secondary {
    @apply py-1.5 px-3 rounded-md text-slate-800 text-sm;
}

.btn-secondary:hover {
    @apply bg-slate-100;
}

.header-with-settings {
    @apply flex justify-between items-center;
}

.btn-icon {
    @apply bg-transparent border-none cursor-pointer text-xl p-1 rounded-full w-8 h-8 flex justify-center items-center;
}

.btn-icon:hover {
    @apply bg-slate-100;
}

.settings-group {
    @apply bg-slate-50 p-3 rounded-lg mb-2 border border-dashed border-slate-200;
}
</style>
