<template>
  <div class="side-navbar">
    <!-- Icon Bar -->
    <div class="icon-bar">
      <button
        class="nav-icon"
        :class="{ active: activePanel === 'settings' }"
        @click="togglePanel('settings')"
        title="Settings"
      >
        ⚙️
      </button>
      <button
        class="nav-icon"
        :class="{ active: activePanel === 'units' }"
        @click="togglePanel('units')"
        title="Unit System"
      >
        📏
      </button>
      <button
        class="nav-icon"
        :class="{ active: activePanel === 'history' }"
        @click="togglePanel('history')"
        title="History"
      >
        📜
      </button>
    </div>

    <!-- Expandable Panel -->
    <Transition name="slide">
      <div v-if="activePanel" class="expanded-panel">
        <SettingsPanel
          v-if="activePanel === 'settings'"
          :current-dt="currentDt"
          :current-max-sim-time="currentMaxSimTime"
          @update="handleSettingsUpdate"
        />
        <UnitSystemPanel
          v-else-if="activePanel === 'units'"
          @unit-system-changed="handleUnitSystemChanged"
        />
        <HistoryPanel
          v-else-if="activePanel === 'history'"
          @load-simulation="handleLoadSimulation"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import HistoryPanel from "./HistoryPanel.vue";
import SettingsPanel from "./SettingsPanel.vue";
import UnitSystemPanel from "./UnitSystemPanel.vue";

defineProps<{
  currentDt: number;
  currentMaxSimTime: number;
}>();

const emit = defineEmits<{
  "update-settings": [settings: { dt: number; maxSimTime: number }];
  "load-simulation": [params: Record<string, any>];
  "unit-system-changed": [];
}>();

type PanelType = "settings" | "units" | "history" | null;
const activePanel = ref<PanelType>(null);

function togglePanel(panel: PanelType) {
  if (activePanel.value === panel) {
    activePanel.value = null;
  } else {
    activePanel.value = panel;
  }
}

function handleSettingsUpdate(settings: { dt: number; maxSimTime: number }) {
  emit("update-settings", settings);
}

function handleLoadSimulation(params: Record<string, any>) {
  emit("load-simulation", params);
  activePanel.value = null;
}

function handleUnitSystemChanged() {
  emit("unit-system-changed");
}
</script>

<style scoped>
@import "tailwindcss";

.side-navbar {
  @apply flex shrink-0;
}

.icon-bar {
  @apply w-16 bg-slate-800 flex flex-col items-center gap-2 py-4;
}

.nav-icon {
  @apply w-12 h-12 bg-transparent border-none cursor-pointer text-2xl rounded-lg transition-all duration-200 flex items-center justify-center;
}

.nav-icon:hover {
  @apply bg-slate-700;
}

.nav-icon.active {
  @apply bg-slate-600;
}

.expanded-panel {
  @apply w-80 bg-white border-r border-slate-200;
}

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  @apply transition-all duration-300 ease-in-out;
}

.slide-enter-from,
.slide-leave-to {
  @apply -translate-x-full opacity-0;
}

.slide-enter-to,
.slide-leave-from {
  @apply translate-x-0 opacity-100;
}
</style>
