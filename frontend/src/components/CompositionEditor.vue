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
                <button
                  @click="removeComponent(item.component)"
                  class="remove-btn"
                >
                  ×
                </button>
              </div>
            </div>

            <div class="total-section" :class="totalStatus">
              <span>Total: {{ totalFraction.toFixed(4) }}</span>
              <span class="status-icon" v-if="isValid">✓</span>
              <span class="status-icon" v-else>⚠️</span>
            </div>

            <button class="btn-secondary small" @click="normalize">
              Normalize to 1.0
            </button>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">Cancel</button>
        <button class="btn-primary" @click="apply" :disabled="!isValid">
          Apply Composition
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { apiClient } from "../api/client";

const props = defineProps<{
  currentComposition: string;
}>();

const emit = defineEmits(["close", "apply"]);

const availableComponents = ref<string[]>([]);
const presets = ref<any[]>([]);
const mixture = ref<{ component: string; fraction: number }[]>([]);
const search = ref("");

// Fetch data on mount
onMounted(async () => {
  try {
    const [compsRes, presetsRes] = await Promise.all([
      apiClient.get("/components"),
      apiClient.get("/presets"),
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

  const parts = compStr.split(",");
  parts.forEach((part) => {
    const [name, val] = part.split("=");
    if (name && val) {
      mixture.value.push({
        component: name.trim(),
        fraction: parseFloat(val),
      });
    }
  });
}

const filteredAvailable = computed(() => {
  return availableComponents.value.filter((c) =>
    c.toLowerCase().includes(search.value.toLowerCase())
  );
});

function isSelected(comp: string) {
  return mixture.value.some((m) => m.component === comp);
}

function addComponent(comp: string) {
  if (!isSelected(comp)) {
    mixture.value.push({ component: comp, fraction: 0 });
  }
}

function removeComponent(comp: string) {
  mixture.value = mixture.value.filter((m) => m.component !== comp);
}

const totalFraction = computed(() => {
  return mixture.value.reduce((sum, item) => sum + (item.fraction || 0), 0);
});

const isValid = computed(() => {
  return (
    Math.abs(totalFraction.value - 1.0) < 0.001 && mixture.value.length > 0
  );
});

const totalStatus = computed(() => {
  if (Math.abs(totalFraction.value - 1.0) < 0.001) return "valid";
  return "invalid";
});

function normalize() {
  const total = totalFraction.value;
  if (total === 0) return;
  mixture.value.forEach((item) => {
    item.fraction = Number((item.fraction / total).toFixed(4));
  });

  // Fix rounding error on largest
  const currentSum = mixture.value.reduce((s, i) => s + i.fraction, 0);
  const diff = 1.0 - currentSum;
  if (Math.abs(diff) > 1e-6) {
    const maxItem = mixture.value.reduce((prev, current) =>
      prev.fraction > current.fraction ? prev : current
    );
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
        fraction: val as number,
      }));
  } catch (e) {
    console.error("Failed to load preset", e);
  }
}

function apply() {
  const compStr = mixture.value
    .map((m) => `${m.component}=${m.fraction.toFixed(4)}`)
    .join(", ");
  emit("apply", compStr);
}
</script>

<style scoped>
@import "tailwindcss";

/* Component-specific modal sizing */
.modal-content {
  @apply w-[90%] max-w-[800px] max-h-[85vh];
}

/* Component-specific modal body scrolling */
.modal-body {
  @apply overflow-y-auto flex-1;
}

.presets-section {
  @apply mb-6;
}

.preset-chips {
  @apply flex flex-wrap gap-2 mt-2;
}

.chip {
  @apply py-1.5 px-3 bg-slate-100 border border-slate-200 rounded-full cursor-pointer text-sm transition-all;
}

.chip:hover {
  @apply bg-blue-500 text-white border-blue-500;
}

.editor-grid {
  @apply grid grid-cols-2 gap-6 h-[400px];
}

.list-container {
  @apply border border-slate-200 rounded-lg p-4 flex flex-col;
}

h4 {
  @apply m-0 mb-2 text-base;
}

.search-input {
  @apply w-full py-2 px-3 mb-2 border border-slate-200 rounded-md bg-white text-slate-800;
}

.component-list {
  @apply flex-1 overflow-y-auto flex flex-col gap-1;
}

.comp-item {
  @apply py-2 px-3 flex justify-between items-center rounded cursor-pointer;
}

.comp-item.add {
  @apply bg-slate-100 border-none text-left;
}

.comp-item.add:hover:not(:disabled) {
  @apply bg-slate-200;
}

.comp-item.add:disabled {
  @apply opacity-50 cursor-default;
}

.comp-item.selected {
  @apply bg-slate-100 cursor-default;
}

.comp-name {
  @apply text-sm flex-1;
}

.fraction-input {
  @apply w-[70px] py-1 px-2 mr-2 text-right border border-slate-200 rounded;
}

.remove-btn {
  @apply border-none bg-transparent text-red-500 cursor-pointer font-bold;
}

.total-section {
  @apply mt-4 p-2 rounded flex justify-between font-bold;
}

.total-section.valid {
  @apply bg-emerald-500/10 text-emerald-500;
}

.total-section.invalid {
  @apply bg-red-500/10 text-red-500;
}

/* Component-specific button styles */
.btn-secondary.small {
  @apply mt-2 text-sm py-1 px-2.5;
}
</style>
