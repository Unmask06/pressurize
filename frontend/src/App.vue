<template>
  <div class="app-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <h1>Pressurization Simulator</h1>
        <p>Gas Valves</p>
      </div>
      <SimulationForm
        :loading="loading"
        :initial-composition="currentComposition"
        :results-empty="results.length === 0"
        :current-dt="currentDt"
        @run="runSimulation"
        @edit-composition="showCompositionEditor = true"
        @view-results="showResultsTable = true"
        @edit-settings="showSettingsEditor = true"
      />
    </div>

    <div class="main-content">
      <div class="results-header">
        <KpiCards
          :peak-flow="kpis.peakFlow"
          :final-pressure="kpis.finalPressure"
          :equilibrium-time="kpis.equilibriumTime"
          :total-mass="kpis.totalMass"
        />
        <button
          class="btn-download"
          @click="showReportModal = true"
          :disabled="results.length === 0"
        >
          📥 Download Report
        </button>
      </div>

      <div class="chart-wrapper">
        <ResultsChart ref="chartRef" :data="results" />
      </div>
    </div>

    <Transition name="fade">
      <CompositionEditor
        v-if="showCompositionEditor"
        :current-composition="currentComposition"
        @close="showCompositionEditor = false"
        @apply="updateComposition"
      />
    </Transition>

    <Transition name="fade">
      <ResultsTable
        v-if="showResultsTable"
        :data="results"
        @close="showResultsTable = false"
      />
    </Transition>

    <Transition name="fade">
      <ReportDownload
        v-if="showReportModal"
        :inputs="lastFormParams"
        :kpis="kpis"
        :chart-data-url="chartDataUrl"
        @close="showReportModal = false"
      />
    </Transition>

    <Transition name="fade">
      <SettingsEditor
        v-if="showSettingsEditor"
        :current-dt="currentDt"
        @close="showSettingsEditor = false"
        @apply="updateSettings"
      />
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { apiClient } from "./api/client";
import CompositionEditor from "./components/CompositionEditor.vue";
import KpiCards from "./components/KpiCards.vue";
import ReportDownload from "./components/ReportDownload.vue";
import ResultsChart from "./components/ResultsChart.vue";
import ResultsTable from "./components/ResultsTable.vue";
import SettingsEditor from "./components/SettingsEditor.vue";
import SimulationForm from "./components/SimulationForm.vue";

const loading = ref(false);
const showCompositionEditor = ref(false);
const showResultsTable = ref(false);
const showReportModal = ref(false);
const showSettingsEditor = ref(false);
const currentComposition = ref(
  "Methane=0.9387, Ethane=0.0121, Propane=0.0004, Carbon dioxide=0.0054, Nitrogen=0.0433"
);
const currentDt = ref(0.05);

// Refs for report generation
const chartRef = ref<InstanceType<typeof ResultsChart> | null>(null);
const lastFormParams = ref<Record<string, any>>({});

// Compute chart data URL when modal opens
const chartDataUrl = computed(() => {
  if (showReportModal.value && chartRef.value) {
    return chartRef.value.getChartDataUrl();
  }
  return null;
});

const results = ref<any[]>([]);
const kpis = reactive({
  peakFlow: 0,
  finalPressure: 0,
  equilibriumTime: 0,
  totalMass: 0,
});

async function runSimulation(params: any) {
  loading.value = true;
  // Store form params for report
  lastFormParams.value = { ...params };
  try {
    const res = await apiClient.post("/simulate", params);

    // Update Results
    results.value = res.data.results;

    // Update KPIs
    kpis.peakFlow = res.data.peak_flow;
    kpis.finalPressure = res.data.final_pressure;
    kpis.equilibriumTime = res.data.equilibrium_time;
    kpis.totalMass = res.data.total_mass_lb;
  } catch (e) {
    console.error("Simulation failed", e);
    alert("Simulation failed. Check console for details.");
  } finally {
    loading.value = false;
  }
}

function updateComposition(newComp: string) {
  currentComposition.value = newComp;
  showCompositionEditor.value = false;
}

function updateSettings(newDt: number) {
  currentDt.value = newDt;
  showSettingsEditor.value = false;
}
</script>

<style scoped>
@import "tailwindcss";

.app-container {
  @apply flex h-screen w-screen overflow-hidden;
}

.sidebar {
  @apply w-[350px] bg-white border-r border-slate-200 flex flex-col shrink-0;
}

.sidebar-header {
  @apply p-6 border-b border-slate-200;
}

.sidebar-header h1 {
  @apply m-0 text-2xl font-extrabold text-blue-500 tracking-tight;
}

.sidebar-header p {
  @apply mt-1 mb-0 text-sm text-slate-400 font-medium uppercase tracking-widest;
}

.main-content {
  @apply flex-1 flex flex-col p-8 bg-slate-50 overflow-hidden;
}

.results-header {
  @apply flex justify-between items-start gap-4 mb-4;
}

.results-header .kpi-grid {
  @apply flex-1;
}

.btn-download {
  @apply shrink-0 py-3 px-5 border-none bg-linear-to-br from-emerald-500 to-emerald-600 text-white rounded-xl text-sm font-semibold cursor-pointer transition-all duration-200 shadow-lg shadow-emerald-500/30;
}

.btn-download:hover:not(:disabled) {
  @apply from-emerald-600 to-emerald-700 -translate-y-0.5 shadow-xl shadow-emerald-500/40;
}

.btn-download:disabled {
  @apply opacity-50 cursor-not-allowed transform-none shadow-none;
}

.chart-wrapper {
  @apply flex-1 min-h-0 w-full;
}
</style>
