<template>
  <div class="app-container">
    <SideNavBar
      :current-dt="currentDt"
      :current-max-sim-time="currentMaxSimTime"
      @update-settings="updateSettings"
      @load-simulation="loadSimulationFromHistory"
      @unit-system-changed="resetAllOutputs"
    />
    <div class="sidebar">
        <div class="sidebar-header">
          <div class="header-top">
            <h1>Pressurization Simulator</h1>
            <a
              href="/products/pressurize/docs/"
              class="btn-docs"
              title="View Documentation"
              target="_blank"
              rel="noopener noreferrer"
              >📖</a
            >
          </div>
          <p>Gas Valves</p>
        </div>
        <SimulationForm
          ref="simulationFormRef"
          :loading="loading"
          :initial-composition="currentComposition"
          :results-empty="results.length === 0"
          :current-dt="currentDt"
          :simulation-completed="simulationCompleted"
          @run="runSimulation"
          @stop="stopSimulation"
          @edit-composition="showCompositionEditor = true"
          @view-results="showResultsTable = true"
        />
      </div>

    <div class="main-content">
      <div class="results-header">
        <KpiCards
          :peak-flow="kpis.peakFlow"
          :final-pressure="kpis.finalPressure"
          :equilibrium-time="kpis.equilibriumTime"
          :total-mass="kpis.totalMass"
          :loading="!kpisReady"
        />
        <button
          v-if="results.length > 0 && simulationCompleted"
          class="btn-download"
          @click="showReportModal = true"
          title="Download Report"
        >
          📥
        </button>
      </div>

      <div class="chart-wrapper">
        <ResultsChart ref="chartRef" :data="results" />
      </div>
    </div>

    <Transition name="fade">
      <CompositionEditor
        v-if="showCompositionEditor"
        key="composition-editor"
        :current-composition="currentComposition"
        @close="showCompositionEditor = false"
        @apply="updateComposition"
      />
    </Transition>

    <Transition name="fade">
      <ResultsTable
        v-if="showResultsTable"
        key="results-table"
        :data="results"
        @close="showResultsTable = false"
      />
    </Transition>

    <Transition name="fade">
      <ReportDownload
        v-if="showReportModal"
        key="report-download"
        :inputs="lastFormParams"
        :kpis="kpis"
        :results="results"
        :chart-data-url="chartDataUrl"
        @close="showReportModal = false"
      />
    </Transition>

    <Transition name="fade">
      <SettingsEditor
        v-if="showSettingsEditor"
        key="settings-editor"
        :current-dt="currentDt"
        :current-max-sim-time="currentMaxSimTime"
        @close="closeSettingsEditor"
        @apply="updateSettings"
      />
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
    fetchUnitConfig,
    getUnitSystem,
    streamSimulation,
    type SimulationRow,
} from "./api/client";
import CompositionEditor from "./components/CompositionEditor.vue";
import KpiCards from "./components/KpiCards.vue";
import SideNavBar from "./components/navigation/SideNavBar.vue";
import ReportDownload from "./components/ReportDownload.vue";
import ResultsChart from "./components/ResultsChart.vue";
import ResultsTable from "./components/ResultsTable.vue";
import SettingsEditor from "./components/SettingsEditor.vue";
import SimulationForm from "./components/SimulationForm.vue";
import { saveSimulation } from "./db/simulationHistory";

const loading = ref(false);
const unitConfigReady = ref(true);
const showCompositionEditor = ref(false);
const showResultsTable = ref(false);
const showReportModal = ref(false);
const showSettingsEditor = ref(false);
const currentComposition = ref(
  "Methane=0.9387, Ethane=0.0121, Propane=0.0004, Carbon dioxide=0.0054, Nitrogen=0.0433",
);
const currentDt = ref(0.05);
const currentMaxSimTime = ref(10000);

// AbortController for stopping simulation
let abortController: AbortController | null = null;

onMounted(async () => {
  try {
    await fetchUnitConfig();
    unitConfigReady.value = true;
  } catch (e) {
    console.error("Failed to fetch unit config in App.vue", e);
    // Still set ready to true to allow app to render, even if units won't display correctly
    unitConfigReady.value = true;
  }
});

// Refs for report generation
const chartRef = ref<InstanceType<typeof ResultsChart> | null>(null);
const simulationFormRef = ref<InstanceType<typeof SimulationForm> | null>(null);
const lastFormParams = ref<Record<string, any>>({});

// Compute chart data URL when modal opens
const chartDataUrl = computed(() => {
  if (showReportModal.value && chartRef.value) {
    try {
      return chartRef.value.getChartDataUrl();
    } catch (e) {
      console.warn("Failed to get chart data URL:", e);
      return null;
    }
  }
  return null;
});

const results = ref<SimulationRow[]>([]);
const loadedRows = ref(0);
const kpis = reactive({
  peakFlow: 0,
  finalPressure: 0,
  equilibriumTime: 0,
  totalMass: 0,
});

// Track if KPIs are ready (simulation complete)
const kpisReady = ref(true);
const simulationCompleted = ref(true);

async function runSimulation(params: any) {
  loading.value = true;
  kpisReady.value = false;
  simulationCompleted.value = true;
  // Store form params for report
  lastFormParams.value = { ...params };
  // Clear previous results
  results.value = [];
  loadedRows.value = 0;
  // Reset KPIs
  kpis.peakFlow = 0;
  kpis.finalPressure = 0;
  kpis.equilibriumTime = 0;
  kpis.totalMass = 0;

  // Create new AbortController
  abortController = new AbortController();

  try {
    await streamSimulation(
      params,
      {
        onChunk: (rows, totalRows) => {
          // Append new rows to results
          results.value = [...results.value, ...rows];
          loadedRows.value = totalRows;
        },
        onComplete: (kpiData) => {
          kpis.peakFlow = kpiData.peak_flow;
          kpis.finalPressure = kpiData.final_pressure;
          kpis.equilibriumTime = kpiData.equilibrium_time;
          kpis.totalMass = kpiData.total_mass;
          simulationCompleted.value =
            kpiData.completed !== undefined ? kpiData.completed : true;
          kpisReady.value = true;

          // Save simulation to history
          const simTag = params._tag;
          saveSimulation(params, simTag, getUnitSystem()).catch((e) => {
            console.error("Failed to save simulation to history:", e);
          });
        },
        onError: (message) => {
          console.error("Simulation failed:", message);
          alert(`Simulation failed: ${message}`);
        },
      },
      abortController.signal,
    );
  } catch (e: any) {
    if (e.name === "AbortError") {
      console.log("Simulation stopped by user");
    } else {
      console.error("Simulation failed", e);
      alert("Simulation failed. Check console for details.");
    }
  } finally {
    loading.value = false;
    kpisReady.value = true;
    abortController = null;
  }
}

function stopSimulation() {
  if (abortController) {
    abortController.abort();
    abortController = null;
  }
}

function updateComposition(newComp: string) {
  currentComposition.value = newComp;
  showCompositionEditor.value = false;
}

function updateSettings(settings: { dt: number; maxSimTime: number }) {
  currentDt.value = settings.dt;
  currentMaxSimTime.value = settings.maxSimTime;
  showSettingsEditor.value = false;
}

function closeSettingsEditor() {
  showSettingsEditor.value = false;
}

function resetAllOutputs() {
  // Clear all results when unit system changes
  results.value = [];
  loadedRows.value = 0;
  
  // Reset KPIs to zero
  kpis.peakFlow = 0;
  kpis.finalPressure = 0;
  kpis.equilibriumTime = 0;
  kpis.totalMass = 0;
  
  // Reset KPI ready state
  kpisReady.value = true;
  simulationCompleted.value = true;
  
  // Clear last form params
  lastFormParams.value = {};
}

function loadSimulationFromHistory(params: Record<string, any>) {
  if (simulationFormRef.value) {
    simulationFormRef.value.loadParameters(params);
    // Update lastFormParams so report generation has access to loaded parameters
    // This ensures consistency if user generates a report before running a new simulation
    lastFormParams.value = { ...params };
  } else {
    console.warn("Cannot load simulation: SimulationForm ref is not available");
  }
}
</script>

<style scoped>
@import "tailwindcss";

.app-container {
  @apply flex h-screen w-screen overflow-hidden;
}

.sidebar {
  @apply w-[30%] min-w-80 bg-white border-r border-slate-200 flex flex-col shrink-0;
}

.sidebar-header {
  @apply p-6 border-b border-slate-200;
}

.header-top {
  @apply flex items-center justify-between gap-2;
}

.sidebar-header h1 {
  @apply m-0 text-2xl font-extrabold text-blue-500 tracking-tight;
}

.btn-docs {
  @apply text-xl hover:scale-110 transition-transform cursor-pointer no-underline;
}

.sidebar-header p {
  @apply mt-1 mb-0 text-sm text-slate-400 font-medium uppercase tracking-widest;
}

.main-content {
  @apply w-[70%] flex-1 flex flex-col p-4 sm:p-6 md:p-8 bg-slate-50 overflow-hidden gap-3 sm:gap-4;
}

.results-header {
  @apply flex flex-col sm:flex-row justify-between items-stretch sm:items-start gap-3 sm:gap-4 shrink-0;
}

.results-header .kpi-grid {
  @apply flex-1;
}

.btn-download {
  @apply shrink-0 py-2 px-3 border-none bg-linear-to-br from-emerald-500 to-emerald-600 text-white rounded-lg text-xl font-semibold cursor-pointer transition-all duration-200 shadow-lg shadow-emerald-500/30 flex items-center justify-center;
}

.btn-download:hover {
  @apply from-emerald-600 to-emerald-700 -translate-y-0.5 shadow-xl shadow-emerald-500/40;
}

.chart-wrapper {
  @apply flex-1 min-h-0 w-full;
}

.loading-overlay {
  @apply flex items-center justify-center w-full h-full bg-slate-50;
}

.loading-spinner {
  @apply text-2xl font-bold text-blue-600 animate-pulse;
}
</style>
