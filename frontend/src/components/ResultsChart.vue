<template>
  <div class="chart-container">
    <v-chart class="chart" :option="option" autoresize />
  </div>
</template>

<script setup lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components';
import VChart from 'vue-echarts';
import { ref, watch, computed } from 'vue';

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
]);

const props = defineProps<{
  data: any[];
}>();

const option = computed(() => {
  if (!props.data || props.data.length === 0) return {};

  const times = props.data.map(d => d.time);
  const pressures = props.data.map(d => d.pressure_psig);
  const upstream = props.data.map(d => d.upstream_pressure_psig);
  const flows = props.data.map(d => d.flowrate_lb_hr);
  const openings = props.data.map(d => d.valve_opening_pct);

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    grid: {
      left: '60',
      right: '140', // Room for two right-side Y axes
      top: '60',    // Room for legend
      bottom: '80'  // Room for X-axis and dataZoom slider
    },
    legend: {
      top: '5',
      data: ['Downstream Pressure', 'Upstream Pressure', 'Flow Rate', 'Valve Opening']
    },
    xAxis: {
      type: 'category',
      data: times,
      name: 'Time (s)',
      boundaryGap: false
    },
    yAxis: [
      {
        type: 'value',
        name: 'Pressure (psig)',
        position: 'left',
        axisLine: { show: true, lineStyle: { color: '#3498db' } },
        axisLabel: { color: '#3498db' }
      },
      {
        type: 'value',
        name: 'Flow Rate (lb/hr)',
        position: 'right',
        offset: 0,
        axisLine: { show: true, lineStyle: { color: '#e74c3c' } },
        axisLabel: { color: '#e74c3c' },
        splitLine: { show: false }
      },
      {
        type: 'value',
        name: 'Valve (%)',
        position: 'right',
        offset: 70, // Shift 3rd axis
        min: 0,
        max: 105,
        axisLine: { show: true, lineStyle: { color: '#27ae60' } },
        axisLabel: { color: '#27ae60' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'Downstream Pressure',
        type: 'line',
        data: pressures,
        smooth: true,
        lineStyle: { width: 3, color: '#3498db' },
        showSymbol: false,
        areaStyle: { opacity: 0.1, color: '#3498db' }
      },
      {
        name: 'Upstream Pressure',
        type: 'line',
        data: upstream,
        lineStyle: { type: 'dashed', color: '#95a5a6' },
        showSymbol: false
      },
      {
        name: 'Flow Rate',
        type: 'line',
        yAxisIndex: 1,
        data: flows,
        smooth: true,
        lineStyle: { width: 2, type: 'dotted', color: '#e74c3c' },
        showSymbol: false
      },
      {
        name: 'Valve Opening',
        type: 'line',
        yAxisIndex: 2,
        data: openings,
        lineStyle: { width: 2, color: '#27ae60' },
        showSymbol: false,
        step: 'end' // Better for fixed/stepped
      }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: 0 },
      { type: 'slider', xAxisIndex: 0 }
    ]
  };
});
</script>

<style scoped src="../styles/ResultsChart.css"></style>
