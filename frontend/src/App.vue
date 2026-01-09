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
        @run="runSimulation" 
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { apiClient } from './api/client';
import SimulationForm from './components/SimulationForm.vue';
import KpiCards from './components/KpiCards.vue';
import ResultsChart from './components/ResultsChart.vue';
import CompositionEditor from './components/CompositionEditor.vue';
import ResultsTable from './components/ResultsTable.vue';
import ReportDownload from './components/ReportDownload.vue';

const loading = ref(false);
const showCompositionEditor = ref(false);
const showResultsTable = ref(false);
const showReportModal = ref(false);
const currentComposition = ref('Methane=0.9387, Ethane=0.0121, Propane=0.0004, Carbon dioxide=0.0054, Nitrogen=0.0433');

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
  totalMass: 0
});

async function runSimulation(params: any) {
  loading.value = true;
  // Store form params for report
  lastFormParams.value = { ...params };
  try {
    const res = await apiClient.post('/simulate', params);
    
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
</script>

<style scoped src="./styles/AppLayout.css"></style>
