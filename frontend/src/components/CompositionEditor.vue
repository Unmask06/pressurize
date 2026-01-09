<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Gas Composition Editor</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
      
      <div class="modal-body">
        <div class="presets-section">
          <label>Presets:</label>
          <div class="preset-chips">
            <button 
              v-for="preset in presets" 
              :key="preset.id"
              @click="loadPreset(preset.id)"
              class="chip"
            >
              {{ preset.name }}
            </button>
          </div>
        </div>

        <div class="editor-grid">
          <!-- Available Components -->
          <div class="list-container">
            <h4>Available</h4>
            <input 
              v-model="search" 
              placeholder="Search components..." 
              class="search-input"
            />
            <div class="component-list">
              <button 
                v-for="comp in filteredAvailable" 
                :key="comp"
                @click="addComponent(comp)"
                class="comp-item add"
                :disabled="isSelected(comp)"
              >
                {{ comp }}
                <span class="action-icon">+</span>
              </button>
            </div>
          </div>

          <!-- Selected Components -->
          <div class="list-container">
            <h4>Selected Mixture</h4>
            <div class="component-list">
              <div 
                v-for="item in mixture" 
                :key="item.component"
                class="comp-item selected"
              >
                <span class="comp-name">{{ item.component }}</span>
                <input 
                  type="number" 
                  v-model.number="item.fraction" 
                  step="0.01" 
                  min="0" 
                  max="1"
                  class="fraction-input"
                />
                <button @click="removeComponent(item.component)" class="remove-btn">×</button>
              </div>
            </div>
            
            <div class="total-section" :class="totalStatus">
              <span>Total: {{ totalFraction.toFixed(4) }}</span>
              <span class="status-icon" v-if="isValid">✓</span>
              <span class="status-icon" v-else>⚠️</span>
            </div>
            
            <button class="btn-secondary small" @click="normalize">Normalize to 1.0</button>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">Cancel</button>
        <button class="btn-primary" @click="apply" :disabled="!isValid">Apply Composition</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { apiClient } from '../api/client';

const props = defineProps<{
  currentComposition: string;
}>();

const emit = defineEmits(['close', 'apply']);

const availableComponents = ref<string[]>([]);
const presets = ref<any[]>([]);
const mixture = ref<{component: string, fraction: number}[]>([]);
const search = ref('');

// Fetch data on mount
onMounted(async () => {
  try {
    const [compsRes, presetsRes] = await Promise.all([
      apiClient.get('/components'),
      apiClient.get('/presets')
    ]);
    availableComponents.value = compsRes.data;
    presets.value = presetsRes.data;
    
    parseComposition(props.currentComposition);
  } catch (e) {
    console.error("Failed to load component data", e);
  }
});

function parseComposition(compStr: string) {
  mixture.value = [];
  if (!compStr) return;
  
  const parts = compStr.split(',');
  parts.forEach(part => {
    const [name, val] = part.split('=');
    if (name && val) {
      mixture.value.push({
        component: name.trim(),
        fraction: parseFloat(val)
      });
    }
  });
}

const filteredAvailable = computed(() => {
  return availableComponents.value.filter(c => 
    c.toLowerCase().includes(search.value.toLowerCase())
  );
});

function isSelected(comp: string) {
  return mixture.value.some(m => m.component === comp);
}

function addComponent(comp: string) {
  if (!isSelected(comp)) {
    mixture.value.push({ component: comp, fraction: 0 });
  }
}

function removeComponent(comp: string) {
  mixture.value = mixture.value.filter(m => m.component !== comp);
}

const totalFraction = computed(() => {
  return mixture.value.reduce((sum, item) => sum + (item.fraction || 0), 0);
});

const isValid = computed(() => {
  return Math.abs(totalFraction.value - 1.0) < 0.001 && mixture.value.length > 0;
});

const totalStatus = computed(() => {
  if (Math.abs(totalFraction.value - 1.0) < 0.001) return 'valid';
  return 'invalid';
});

function normalize() {
  const total = totalFraction.value;
  if (total === 0) return;
  mixture.value.forEach(item => {
    item.fraction = Number((item.fraction / total).toFixed(4));
  });
  
  // Fix rounding error on largest
  const currentSum = mixture.value.reduce((s, i) => s + i.fraction, 0);
  const diff = 1.0 - currentSum;
  if (Math.abs(diff) > 1e-6) {
    const maxItem = mixture.value.reduce((prev, current) => (prev.fraction > current.fraction) ? prev : current);
    maxItem.fraction += diff;
  }
}

async function loadPreset(presetId: string) {
  try {
    const res = await apiClient.get(`/presets/${presetId}`);
    const compDict = res.data;
    mixture.value = Object.entries(compDict)
      .filter(([_, val]) => (val as number) > 0)
      .map(([comp, val]) => ({
        component: comp,
        fraction: val as number
      }));
  } catch (e) {
    console.error("Failed to load preset", e);
  }
}

function apply() {
  const compStr = mixture.value
    .map(m => `${m.component}=${m.fraction.toFixed(4)}`)
    .join(', ');
  emit('apply', compStr);
}
</script>

<style scoped src="../styles/CompositionEditor.css"></style>
