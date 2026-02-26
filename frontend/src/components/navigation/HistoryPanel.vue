<template>
  <div class="history-panel">
    <div class="panel-header">
      <h2>📜 History</h2>
      <p>Recent simulations</p>
    </div>

    <div class="panel-content">
      <!-- Search -->
      <div v-if="history.length > 0" class="search-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search by tag, mode, pressure, volume..."
          class="search-input"
        />
      </div>

      <div v-if="history.length === 0" class="empty-state">
        <div class="icon">📭</div>
        <h3>No History</h3>
        <p>Run a simulation to see it here</p>
      </div>

      <div v-else-if="filteredHistory.length === 0" class="empty-state">
        <div class="icon">🔍</div>
        <h3>No Results</h3>
        <p>No simulations match your search</p>
      </div>

      <div v-else class="history-list">
        <div
          v-for="item in filteredHistory"
          :key="item.id"
          class="history-item"
          @click="loadSimulation(item)"
        >
          <div class="item-content">
            <div class="item-header">
              <span class="mode-badge" :class="getModeClass(item.params.mode)">
                {{ getModeIcon(item.params.mode) }}
                {{ formatMode(item.params.mode) }}
              </span>
              <span class="timestamp">{{
                formatTimestamp(item.timestamp)
              }}</span>
            </div>
            <div v-if="item.label" class="item-tag">
              <span class="tag-badge">🏷️ {{ item.label }}</span>
            </div>
            <div class="item-details">
              <div class="detail">
                <span class="label">P (Up/Down):</span>
                <span class="value"
                  >{{ item.params.p_up }} / {{ item.params.p_down_init }}</span
                >
              </div>
              <div class="detail">
                <span class="label">V (Up/Down):</span>
                <span class="value"
                  >{{ item.params.upstream_volume }} /
                  {{ item.params.downstream_volume }}</span
                >
              </div>
              <div v-if="item.unitSystem" class="detail">
                <span class="label">Units:</span>
                <span class="value unit-badge">{{ item.unitSystem }}</span>
              </div>
            </div>
          </div>
          <button
            class="btn-delete"
            @click.stop="confirmDelete(item.id!)"
            title="Delete this simulation"
          >
            🗑️
          </button>
        </div>
      </div>

      <button
        v-if="history.length > 0"
        class="btn-clear"
        @click="confirmClearAll"
      >
        Clear All History
      </button>
    </div>

    <!-- Confirmation Dialog -->
    <div v-if="showConfirmDialog" class="dialog-overlay" @click="cancelDialog">
      <div class="dialog" @click.stop>
        <h3>{{ confirmTitle }}</h3>
        <p>{{ confirmMessage }}</p>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="cancelDialog">Cancel</button>
          <button class="btn-confirm" @click="confirmAction">Confirm</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  clearHistory,
  deleteSimulation,
  getSimulationHistory,
  type SimulationHistoryEntry,
} from "../../db/simulationHistory";

const emit = defineEmits<{
  "load-simulation": [params: Record<string, any>];
}>();

const history = ref<SimulationHistoryEntry[]>([]);
const searchQuery = ref("");
const showConfirmDialog = ref(false);
const confirmTitle = ref("");
const confirmMessage = ref("");
const pendingAction = ref<(() => void) | null>(null);

const filteredHistory = computed(() => {
  const q = searchQuery.value.toLowerCase().trim();
  if (!q) return history.value;
  return history.value.filter((item) => {
    const mode = (item.params.mode || "").toLowerCase();
    const label = (item.label || "").toLowerCase();
    const units = (item.unitSystem || "").toLowerCase();

    // Search in pressures and volumes as well
    const pUp = String(item.params.p_up || "").toLowerCase();
    const pDown = String(item.params.p_down_init || "").toLowerCase();
    const vUp = String(item.params.upstream_volume || "").toLowerCase();
    const vDown = String(item.params.downstream_volume || "").toLowerCase();

    return (
      mode.includes(q) ||
      label.includes(q) ||
      units.includes(q) ||
      pUp.includes(q) ||
      pDown.includes(q) ||
      vUp.includes(q) ||
      vDown.includes(q)
    );
  });
});

async function loadHistory() {
  history.value = await getSimulationHistory();
}

onMounted(() => {
  loadHistory();
});

function loadSimulation(item: SimulationHistoryEntry) {
  emit("load-simulation", item.params);
}

function confirmDelete(id: number) {
  confirmTitle.value = "Delete Simulation?";
  confirmMessage.value =
    "Are you sure you want to delete this simulation from history?";
  pendingAction.value = () => handleDelete(id);
  showConfirmDialog.value = true;
}

function confirmClearAll() {
  confirmTitle.value = "Clear All History?";
  confirmMessage.value =
    "Are you sure you want to clear all simulation history? This cannot be undone.";
  pendingAction.value = handleClearAll;
  showConfirmDialog.value = true;
}

async function handleDelete(id: number) {
  try {
    await deleteSimulation(id);
    await loadHistory();
  } catch (error) {
    console.error("Failed to delete simulation:", error);
    alert("Failed to delete simulation. Check console for details.");
  }
}

async function handleClearAll() {
  try {
    await clearHistory();
    await loadHistory();
  } catch (error) {
    console.error("Failed to clear history:", error);
    alert("Failed to clear history. Check console for details.");
  }
}

function confirmAction() {
  if (pendingAction.value) {
    pendingAction.value();
  }
  cancelDialog();
}

function cancelDialog() {
  showConfirmDialog.value = false;
  pendingAction.value = null;
}

function getModeIcon(mode: string): string {
  switch (mode) {
    case "pressurize":
      return "🔼";
    case "depressurize":
      return "🔽";
    case "equalize":
      return "⇌";
    default:
      return "📊";
  }
}

function getModeClass(mode: string): string {
  switch (mode) {
    case "pressurize":
      return "mode-pressurize";
    case "depressurize":
      return "mode-depressurize";
    case "equalize":
      return "mode-equalize";
    default:
      return "";
  }
}

function formatMode(mode: string): string {
  return mode.charAt(0).toUpperCase() + mode.slice(1);
}

function formatTimestamp(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days}d ago`;
  return new Date(timestamp).toLocaleDateString();
}
</script>

<style scoped>
@import "tailwindcss";

.history-panel {
  @apply h-full flex flex-col;
}

.panel-header {
  @apply border-b p-6;
  border-color: var(--xergiz-border);
}

.panel-header h2 {
  @apply text-xl font-bold m-0;
  color: var(--xergiz-text);
}

.panel-header p {
  @apply text-sm mt-1 mb-0;
  color: var(--xergiz-text-muted);
}

.panel-content {
  @apply flex-1 overflow-y-auto p-6 flex flex-col gap-4;
}

.search-bar {
  @apply shrink-0;
}

.search-input {
  @apply w-full py-2 px-3 border rounded-lg text-sm transition-all duration-200;
  background: var(--xergiz-dark);
  border-color: var(--xergiz-border);
  color: var(--xergiz-text);
}

.search-input::placeholder {
  color: var(--xergiz-text-muted);
}

.search-input:hover {
  border-color: var(--xergiz-border-hover);
}

.search-input:focus {
  @apply outline-none ring-2;
  border-color: var(--xergiz-teal);
  ring-color: var(--xergiz-teal-dim);
}

.empty-state {
  @apply text-center py-12 px-4;
}

.empty-state .icon {
  @apply text-5xl mb-4;
}

.empty-state h3 {
  @apply text-lg font-bold m-0 mb-2;
  color: var(--xergiz-text);
}

.empty-state p {
  @apply text-sm m-0;
  color: var(--xergiz-text-muted);
}

.history-list {
  @apply flex flex-col gap-3;
}

.history-item {
  @apply flex items-center gap-3 border rounded-lg p-4 cursor-pointer transition-all duration-200;
  background: var(--xergiz-surface);
  border-color: var(--xergiz-border);
}

.history-item:hover {
  border-color: var(--xergiz-border-hover);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.item-content {
  @apply flex-1 flex flex-col gap-2;
}

.item-header {
  @apply flex items-center justify-between gap-2;
}

.mode-badge {
  @apply px-2 py-1 rounded text-xs font-bold;
}

.mode-pressurize {
  background: rgba(52, 211, 153, 0.12);
  color: #34d399;
}

.mode-depressurize {
  background: rgba(251, 146, 60, 0.12);
  color: #fb923c;
}

.mode-equalize {
  background: rgba(96, 165, 250, 0.12);
  color: #60a5fa;
}

.timestamp {
  @apply text-xs;
  color: var(--xergiz-text-muted);
}

.item-details {
  @apply flex flex-col gap-1;
}

.detail {
  @apply flex items-center gap-2 text-xs;
}

.detail .label {
  color: var(--xergiz-text-muted);
  @apply font-medium;
}

.detail .value {
  color: var(--xergiz-text);
  @apply font-semibold;
}

.item-tag {
  @apply flex items-center;
}

.tag-badge {
  @apply text-xs rounded px-2 py-0.5 border;
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
  border-color: rgba(251, 191, 36, 0.2);
}

.unit-badge {
  @apply text-xs capitalize;
}

.btn-delete {
  @apply border-none cursor-pointer text-lg p-2 rounded-lg transition-all;
  background: rgba(239, 68, 68, 0.1);
}

.btn-delete:hover {
  background: rgba(239, 68, 68, 0.2);
}

.btn-delete:active {
  @apply scale-90;
}

.btn-clear {
  @apply mt-auto py-2 px-4 border rounded-lg font-semibold text-sm cursor-pointer transition-all;
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.btn-clear:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
}

.dialog-overlay {
  @apply fixed inset-0 backdrop-blur-md flex items-center justify-center z-50;
  background: rgba(2, 6, 23, 0.8);
}

.dialog {
  @apply rounded-xl p-6 max-w-md w-full mx-4 border;
  background: var(--xergiz-panel);
  border-color: var(--xergiz-border);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.dialog h3 {
  @apply text-lg font-bold m-0 mb-2;
  color: var(--xergiz-text);
}

.dialog p {
  @apply text-sm mb-6;
  color: var(--xergiz-text-muted);
}

.dialog-actions {
  @apply flex gap-3 justify-end;
}

.btn-cancel {
  @apply py-2 px-4 border-none rounded-lg font-semibold cursor-pointer transition-all;
  background: rgba(255, 255, 255, 0.05);
  color: var(--xergiz-text-muted);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--xergiz-text);
}

.btn-confirm {
  @apply py-2 px-4 border-none text-white rounded-lg font-semibold cursor-pointer transition-all;
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.btn-confirm:hover {
  filter: brightness(1.1);
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
}
</style>
