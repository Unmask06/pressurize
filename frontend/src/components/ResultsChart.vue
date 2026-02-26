<template>
  <div class="chart-container">
    <v-chart ref="chartRef" class="chart" :option="option" autoresize />
  </div>
</template>

<script setup lang="ts">
import { LineChart } from "echarts/charts";
import {
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from "echarts/components";
import { graphic, use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed, ref } from "vue";
import VChart from "vue-echarts";
import { getUnit } from "../api/client";

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
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
        return chart.getDataURL({
          type: "png",
          pixelRatio: 2,
          backgroundColor: "#0f172a",
        });
      }
    }
    return null;
  },
});

const option = computed(() => {
  if (!props.data || props.data.length === 0) return {};

  const pressureUnit = getUnit("pressure");
  const flowUnit = getUnit("mass_flow_rate");

  const downstream = props.data.map((d) => [d.time, d.downstream_pressure]);
  const upstream = props.data.map((d) => [d.time, d.upstream_pressure]);
  const flows = props.data.map((d) => [d.time, d.flowrate]);
  const openings = props.data.map((d) => [d.time, d.valve_opening_pct]);

  return {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross", label: { backgroundColor: "#0f172a" } },
      backgroundColor: "rgba(15, 23, 42, 0.95)",
      borderColor: "rgba(148, 163, 184, 0.12)",
      borderWidth: 1,
      textStyle: { color: "#f1f5f9" },
    },
    grid: {
      left: "3%",
      right: "180", // More room for labels
      bottom: "60",
      containLabel: true,
    },
    legend: {
      data: [
        "Downstream Pressure",
        "Upstream Pressure",
        "Flow Rate",
        "Valve Opening",
      ],
      top: 0,
      textStyle: { color: "#94a3b8" },
    },
    xAxis: {
      type: "value",
      boundaryGap: false,
      name: `Time (${getUnit("time")})`,
      nameLocation: "middle",
      nameGap: 30,
      axisLine: { lineStyle: { color: "rgba(148, 163, 184, 0.12)" } },
      axisLabel: { color: "#64748b" },
      splitLine: {
        lineStyle: { color: "rgba(148, 163, 184, 0.06)", type: "dashed" },
      },
    },
    yAxis: [
      {
        type: "value",
        name: `Pressure (${pressureUnit})`,
        position: "left",
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: "#60a5fa", fontWeight: "bold" },
        splitLine: {
          show: true,
          lineStyle: { color: "rgba(148, 163, 184, 0.06)", type: "dashed" },
        },
      },
      {
        type: "value",
        name: `Flow (${flowUnit})`,
        position: "right",
        offset: 0,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: "#f87171", formatter: "{value}" },
        splitLine: { show: false },
      },
      {
        type: "value",
        name: "Opening (%)",
        position: "right",
        offset: 80,
        min: 0,
        max: 100,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: "#34d399", formatter: "{value}%" },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "Downstream Pressure",
        type: "line",
        smooth: true,
        showSymbol: false,
        lineStyle: { type: "dashed", color: "#60a5fa" },
        data: downstream,
      },
      {
        name: "Upstream Pressure",
        type: "line",
        data: upstream,
        lineStyle: { type: "dashed", color: "#94a3b8" },
        showSymbol: false,
      },
      {
        name: "Flow Rate",
        type: "line",
        yAxisIndex: 1,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 3, color: "#f87171" },
        areaStyle: {
          opacity: 0.2,
          color: new graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(248, 113, 113, 0.6)" },
            { offset: 1, color: "rgba(248, 113, 113, 0)" },
          ]),
        },
        data: flows,
      },
      {
        name: "Valve Opening",
        type: "line",
        yAxisIndex: 2,
        step: "end",
        showSymbol: false,
        lineStyle: { width: 2, color: "#34d399", type: "solid" },
        data: openings,
      },
    ],
    dataZoom: [
      {
        type: "inside",
        xAxisIndex: 0,
        filterMode: "filter",
      },
      {
        type: "slider",
        xAxisIndex: 0,
        filterMode: "filter",
        brushSelect: false,
        bottom: 0,
        textStyle: { color: "#64748b" },
        borderColor: "rgba(148, 163, 184, 0.08)",
        fillerColor: "rgba(45, 212, 191, 0.15)",
        handleStyle: { color: "#2dd4bf" },
      },
    ],
  };
});
</script>

<style scoped>
@import "tailwindcss";

.chart-container {
  @apply w-full h-full rounded-xl p-4 border transition-all duration-300;
  background: var(--xergiz-surface);
  border-color: var(--xergiz-border);
}

.chart-container:hover {
  border-color: var(--xergiz-border-hover);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.chart {
  @apply h-full w-full;
}
</style>
