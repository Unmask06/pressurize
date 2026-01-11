<template>
  <div class="chart-container">
    <v-chart ref="chartRef" class="chart" :option="option" autoresize />
  </div>
</template>

<script setup lang="ts">
import { use, graphic } from 'echarts/core';
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

// Expose chart ref for parent to get image data
const chartRef = ref<InstanceType<typeof VChart> | null>(null);

defineExpose({
  getChartDataUrl: () => {
    if (chartRef.value) {
      // Access the internal echarts instance
      const chart = chartRef.value.chart;
      if (chart) {
        return chart.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#fff' });
      }
    }
    return null;
  }
});

const option = computed(() => {
  if (!props.data || props.data.length === 0) return {};

  const pressures = props.data.map(d => [d.time, d.pressure_psig]);
  const upstream = props.data.map(d => [d.time, d.upstream_pressure_psig]);
  const flows = props.data.map(d => [d.time, d.flowrate_lb_hr]);
  const openings = props.data.map(d => [d.time, d.valve_opening_pct]);

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#eee',
      borderWidth: 1,
      textStyle: { color: '#333' }
    },
    grid: {
      left: '3%',
      right: '180', // More room for labels
      bottom: '60',
      containLabel: true
    },
    legend: {
      data: ['Downstream Pressure', 'Upstream Pressure', 'Flow Rate', 'Valve Opening'],
      top: 0,
      textStyle: { color: '#666' }
    },
    xAxis: {
      type: 'value',
      boundaryGap: false,
      name: 'Time (s)',
      nameLocation: 'middle',
      nameGap: 30,
      axisLine: { lineStyle: { color: '#ccc' } },
      axisLabel: { color: '#666' }
    },
    yAxis: [
      {
        type: 'value',
        name: 'Pressure (psig)',
        position: 'left',
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#007aff', fontWeight: 'bold' },
        splitLine: { 
          show: true, 
          lineStyle: { type: 'dashed', opacity: 0.5 } 
        }
      },
      {
        type: 'value',
        name: 'Flow (lb/hr)',
        position: 'right',
        offset: 0,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#ff9500', formatter: '{value}' },
        splitLine: { show: false }
      },
      {
        type: 'value',
        name: 'Opening (%)',
        position: 'right',
        offset: 80,
        min: 0,
        max: 100,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#34c759', formatter: '{value}%' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'Downstream Pressure',
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 3, color: '#007aff' },
        data: pressures
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
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 3, color: '#ff9500' },
        areaStyle: {
          opacity: 0.2,
          color: new graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 149, 0, 0.6)' },
            { offset: 1, color: 'rgba(255, 149, 0, 0)' }
          ])
        },
        data: flows
      },
      {
        name: 'Valve Opening',
        type: 'line',
        yAxisIndex: 2,
        step: 'end',
        showSymbol: false,
        lineStyle: { width: 2, color: '#34c759', type: 'dashed' },
        data: openings
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: 0,
        filterMode: 'filter'
      },
      {
        type: 'slider',
        xAxisIndex: 0,
        filterMode: 'filter',
        brushSelect: false
      }
    ]
  };
});
</script>

<style scoped>
@import "tailwindcss";

.chart-container {
    @apply w-full h-full bg-white rounded-xl p-4 shadow-sm border border-slate-200 transition-all duration-300;
}

.chart-container:hover {
    @apply -translate-y-0.5 shadow-md;
}

.chart {
    @apply h-full w-full;
}
</style>
