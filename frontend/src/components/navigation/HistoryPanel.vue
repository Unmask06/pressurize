<template>
  <div class="history-panel">
    <div class="panel-header">
      <h2>📜 History</h2>
      <p>Recent simulations</p>
    </div>

    <div class="panel-content">
      <div v-if="history.length === 0" class="empty-state">
        <div class="icon">📭</div>
        <h3>No History</h3>
        <p>Run a simulation to see it here</p>
      </div>

      <div v-else class="history-list">
        <div
          v-for="item in history"
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
              <span class="timestamp">{{ formatTimestamp(item.timestamp) }}</span>
            </div>
            <div class="item-details">
              <div class="detail">
                <span class="label">Upstream:</span>
                <span class="value">{{ item.params.p_up }} psig</span>
              </div>
              <div class="detail">
                <span class="label">Downstream:</span>
                <span class="value">{{ item.params.p_down_init }} psig</span>
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
import { onMounted, ref } from "vue";
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
const showConfirmDialog = ref(false);
const confirmTitle = ref("");
const confirmMessage = ref("");
const pendingAction = ref<(() => void) | null>(null);

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
  @apply border-b border-slate-200 p-6;
}

.panel-header h2 {
  @apply text-xl font-bold text-slate-800 m-0;
}

.panel-header p {
  @apply text-sm text-slate-500 mt-1 mb-0;
}

.panel-content {
  @apply flex-1 overflow-y-auto p-6 flex flex-col gap-4;
}

.empty-state {
  @apply text-center py-12 px-4;
}

.empty-state .icon {
  @apply text-5xl mb-4;
}

.empty-state h3 {
  @apply text-lg font-bold text-slate-700 m-0 mb-2;
}

.empty-state p {
  @apply text-sm text-slate-500 m-0;
}

.history-list {
  @apply flex flex-col gap-3;
}

.history-item {
  @apply flex items-center gap-3 bg-white border border-slate-200 rounded-lg p-4 cursor-pointer transition-all duration-200 hover:border-blue-300 hover:shadow-md;
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
  @apply bg-green-100 text-green-700;
}

.mode-depressurize {
  @apply bg-orange-100 text-orange-700;
}

.mode-equalize {
  @apply bg-blue-100 text-blue-700;
}

.timestamp {
  @apply text-xs text-slate-400;
}

.item-details {
  @apply flex flex-col gap-1;
}

.detail {
  @apply flex items-center gap-2 text-xs;
}

.detail .label {
  @apply text-slate-500 font-medium;
}

.detail .value {
  @apply text-slate-700 font-semibold;
}

.btn-delete {
  @apply bg-red-50 border-none cursor-pointer text-lg p-2 rounded-lg transition-all hover:bg-red-100 active:scale-90;
}

.btn-clear {
  @apply mt-auto py-2 px-4 bg-red-50 border border-red-200 text-red-600 rounded-lg font-semibold text-sm cursor-pointer transition-all hover:bg-red-100 hover:border-red-300;
}

.dialog-overlay {
  @apply fixed inset-0 bg-black/50 flex items-center justify-center z-50;
}

.dialog {
  @apply bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl;
}

.dialog h3 {
  @apply text-lg font-bold text-slate-800 m-0 mb-2;
}

.dialog p {
  @apply text-sm text-slate-600 mb-6;
}

.dialog-actions {
  @apply flex gap-3 justify-end;
}

.btn-cancel {
  @apply py-2 px-4 bg-slate-100 border-none text-slate-700 rounded-lg font-semibold cursor-pointer transition-all hover:bg-slate-200;
}

.btn-confirm {
  @apply py-2 px-4 bg-red-600 border-none text-white rounded-lg font-semibold cursor-pointer transition-all hover:bg-red-700;
}
</style>
