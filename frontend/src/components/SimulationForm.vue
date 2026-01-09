<template>
  <div class="simulation-form">
    <h3>Simulation Parameters</h3>
    
    <div class="form-group">
      <label>Upstream Pressure (psig)</label>
      <input type="number" v-model.number="form.p_up_psig" step="10" />
    </div>

    <div class="form-group">
      <label>Downstream Pressure (psig)</label>
      <input type="number" v-model.number="form.p_down_init_psig" step="10" />
    </div>

    <div class="row">
      <div class="form-group half">
        <label>Volume (ft³)</label>
        <input type="number" v-model.number="form.volume_ft3" step="1" />
      </div>
      <div class="form-group half">
        <label>Valve ID (in)</label>
        <input type="number" v-model.number="form.valve_id_inch" step="0.1" />
      </div>
    </div>

    <div class="form-group">
      <label>Opening Time (s)</label>
      <input type="number" v-model.number="form.opening_time_s" step="1" />
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
        <label title="Molar Mass">M (g/mol)</label>
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
import { reactive, computed, watch } from 'vue';
import { apiClient } from '../api/client';

const props = defineProps<{
  loading: boolean;
  initialComposition?: string;
  resultsEmpty: boolean;
}>();

const emit = defineEmits(['run', 'edit-composition', 'view-results']);

function viewResults() {
  console.log("Emitting view-results event");
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

<style scoped src="../styles/SimulationForm.css"></style>
