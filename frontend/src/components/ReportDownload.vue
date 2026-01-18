<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content report-modal">
      <div class="modal-header">
        <h2>📥 Download Report</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <h3 class="text-lg font-semibold text-slate-800 mb-2">
          Report Details
        </h3>
        <label class="block text-sm font-medium text-slate-600 mb-1">
          Report Title
        </label>
        <textarea
          v-model="reportTitle"
          placeholder="Enter report title... (e.g., Simulation Report for Valve S-101)"
          rows="1"
          class="mb-4"
        ></textarea>

        <label class="block text-sm font-medium text-slate-600 mb-1">
          Additional Notes
        </label>
        <textarea
          v-model="notes"
          placeholder="Enter your notes here... (e.g., purpose of simulation, observations, etc.)"
          rows="4"
        ></textarea>
      </div>

      <div class="modal-footer flex-col gap-4">
        <div class="flex w-full justify-between items-center gap-3">
          <button class="btn-secondary flex-1" @click="$emit('close')">
            Cancel
          </button>
          <button
            class="btn-primary flex-1"
            @click="handleDownload('pdf')"
            :disabled="generating || zipping"
          >
            {{ generating ? "Generating..." : "📄 Download Report" }}
          </button>
          <button
            class="btn-assets flex-1"
            @click="handleDownload('all')"
            :disabled="generating || zipping"
          >
            {{ zipping ? "Zipping..." : "📦 Download All Assets" }}
          </button>
        </div>

        <div class="footer-credits">
          Developed by
          <a
            href="https://github.com/Unmask06"
            target="_blank"
            rel="noopener noreferrer"
            class="author-link"
          >
            Unmask06
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { jsPDF } from "jspdf";
import JSZip from "jszip";
import { type SimulationRow } from "../api/client";
import { ref } from "vue";

const props = defineProps<{
  inputs: Record<string, any>;
  kpis: {
    peakFlow: number;
    final_pressure: number;
    equilibrium_time: number;
    total_mass_lb: number;
  };
  chartDataUrl: string | null;
  results: SimulationRow[];
}>();

const emit = defineEmits(["close"]);

const reportTitle = ref("");
const notes = ref("");
const generating = ref(false);
const zipping = ref(false);

function formatValue(value: any, decimals = 2): string {
  if (typeof value === "number") {
    return value.toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }
  return String(value);
}

function formatInputLabel(key: string): string {
  // Handle dynamic label for opening/closing time based on valve action
  if (key === "opening_time_s") {
    return props.inputs.valve_action === "close" ? "Closing Time" : "Opening Time";
  }

  const labels: Record<string, string> = {
    p_up_psig: "Upstream Pressure",
    p_down_init_psig: "Downstream Pressure",
    volume_ft3: "Volume",
    valve_id_inch: "Valve ID",
    valve_action: "Valve Action",
    temp_f: "Temperature",
    molar_mass: "Molar Mass (MW)",
    z_factor: "Z-Factor",
    k_ratio: "Heat Capacity Ratio (k)",
    discharge_coeff: "Discharge Coefficient (Cd)",
    opening_mode: "Valve Mode",
    k_curve: "Curve Factor (k)",
    property_mode: "Property Mode",
    composition: "Gas Composition",
    dt: "Time Step",
  };
  return labels[key] || key;
}

function formatInputUnit(key: string): string {
  const units: Record<string, string> = {
    p_up_psig: "psig",
    p_down_init_psig: "psig",
    volume_ft3: "ft³",
    valve_id_inch: "in",
    opening_time_s: "s",
    temp_f: "°F",
    molar_mass: "g/mol",
    z_factor: "",
    k_ratio: "",
    discharge_coeff: "",
    opening_mode: "",
    k_curve: "",
    property_mode: "",
    composition: "",
    dt: "s",
  };
  return units[key] || "";
}

async function getPdfBlob(): Promise<Blob> {
  try {
    const doc = new jsPDF("p", "mm", "a4");
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 15;
    let y = margin;

    // === HEADER ===
    doc.setFillColor(30, 41, 59); // Dark slate
    doc.rect(0, 0, pageWidth, 40, "F");

    doc.setTextColor(255, 255, 255);

    // User-entered Report Title (Left)
    doc.setFontSize(20);
    doc.setFont("helvetica", "bold");
    doc.text(reportTitle.value.trim() || "Simulation Report", margin, 25);

    // App Branding and Timestamp (Right)
    doc.setFontSize(10);
    doc.text("Pressurization Simulator Report", pageWidth - margin, 18, {
      align: "right",
    });

    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");
    const timestamp = new Date().toLocaleString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
    doc.text(`Generated: ${timestamp}`, pageWidth - margin, 28, {
      align: "right",
    });

    y = 55;
    doc.setTextColor(30, 41, 59);

    // === SIMULATION INPUTS ===
    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text("Simulation Inputs", margin, y);
    y += 8;

    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");

    const inputKeys = Object.keys(props.inputs).filter((k) => {
      // Always exclude dt and composition
      if (k === "dt" || k === "composition") return false;
      // Exclude k_curve (Curve Factor) for Linear mode since it's not used
      if (k === "k_curve" && props.inputs.opening_mode === "linear") return false;
      return true;
    });
    const colWidth = (pageWidth - 2 * margin) / 2;
    let col = 0;

    for (const key of inputKeys) {
      const value = props.inputs[key];
      const label = formatInputLabel(key);
      const unit = formatInputUnit(key);
      const displayValue = `${formatValue(value, 2)}${unit ? " " + unit : ""}`;

      const xPos = margin + col * colWidth;
      doc.setFont("helvetica", "bold");
      doc.text(`${label}:`, xPos, y);
      doc.setFont("helvetica", "normal");
      doc.text(displayValue, xPos + 50, y);

      col++;
      if (col >= 2) {
        col = 0;
        y += 6;
      }
    }
    if (col !== 0) y += 6;

    // Special handling for Composition if in composition mode
    if (
      props.inputs.property_mode === "composition" &&
      props.inputs.composition
    ) {
      y += 2;
      doc.setFont("helvetica", "bold");
      doc.text("Gas Composition:", margin, y);
      y += 5;
      doc.setFont("helvetica", "normal");
      doc.setFontSize(8);
      const compLines = doc.splitTextToSize(
        props.inputs.composition,
        pageWidth - 2 * margin
      );
      doc.text(compLines, margin, y);
      y += compLines.length * 4 + 2;
      doc.setFontSize(9);
    }

    y += 5;

    // === KPI OUTPUTS ===
    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text("Key Performance Indicators", margin, y);
    y += 10;

    const kpiData = [
      {
        label: "Peak Flow Rate",
        value: props.kpis.peakFlow,
        unit: "lb/hr",
        decimals: 0,
      },
      {
        label: "Final Pressure",
        value: props.kpis.final_pressure,
        unit: "psig",
        decimals: 1,
      },
      {
        label: "Equilibrium Time",
        value: props.kpis.equilibrium_time,
        unit: "seconds",
        decimals: 1,
      },
      {
        label: "Total Mass Flow",
        value: props.kpis.total_mass_lb,
        unit: "lb",
        decimals: 1,
      },
    ];

    const kpiBoxWidth = (pageWidth - 2 * margin - 15) / 4;
    kpiData.forEach((kpi, i) => {
      const xPos = margin + i * (kpiBoxWidth + 5);

      // KPI Box
      doc.setFillColor(248, 250, 252);
      doc.roundedRect(xPos, y, kpiBoxWidth, 22, 2, 2, "F");

      // Label
      doc.setFontSize(8);
      doc.setFont("helvetica", "normal");
      doc.setTextColor(100, 116, 139);
      doc.text(kpi.label, xPos + kpiBoxWidth / 2, y + 6, { align: "center" });

      // Value
      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(30, 41, 59);
      doc.text(
        formatValue(kpi.value, kpi.decimals),
        xPos + kpiBoxWidth / 2,
        y + 14,
        { align: "center" }
      );

      // Unit
      doc.setFontSize(7);
      doc.setFont("helvetica", "normal");
      doc.setTextColor(100, 116, 139);
      doc.text(kpi.unit, xPos + kpiBoxWidth / 2, y + 19, { align: "center" });
    });

    y += 30;
    doc.setTextColor(30, 41, 59);

    // === GRAPH ===
    if (props.chartDataUrl) {
      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.text("Simulation Results Chart", margin, y);
      y += 5;

      const imgWidth = pageWidth - 2 * margin;
      const imgHeight = imgWidth * 0.5; // Aspect ratio

      doc.addImage(props.chartDataUrl, "PNG", margin, y, imgWidth, imgHeight);
      y += imgHeight + 10;
    }

    // === NOTES ===
    if (notes.value.trim()) {
      // Check if we need a new page
      if (y > 250) {
        doc.addPage();
        y = margin;
      }

      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.text("Notes", margin, y);
      y += 8;

      doc.setFontSize(10);
      doc.setFont("helvetica", "normal");

      // Word wrap notes
      const lines = doc.splitTextToSize(notes.value, pageWidth - 2 * margin);
      doc.text(lines, margin, y);
    }

    // === FOOTER ===
    const pageCount = doc.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150);
      doc.text(
        `Page ${i} of ${pageCount}`,
        pageWidth / 2,
        doc.internal.pageSize.getHeight() - 10,
        { align: "center" }
      );
    }

    return doc.output("blob");
  } catch (error) {
    console.error("PDF generation failed:", error);
    throw error;
  }
}


function generateCsv(data: SimulationRow[]): string {
  if (!data || data.length === 0) return "";

  const headers = Object.keys(data[0]);
  const csvRows = [
    headers.join(","),
    ...data.map((row) =>
      headers.map((header) => (row as any)[header]).join(",")
    ),
  ];

  return csvRows.join("\n");
}

function getFilename(extension: string): string {
  const dateStr = new Date().toISOString().slice(0, 10);
  const titleSlug = reportTitle.value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .slice(0, 30);

  return titleSlug
    ? `${titleSlug}-${dateStr}.${extension}`
    : `pressurization-report-${dateStr}.${extension}`;
}

async function handleDownload(type: "pdf" | "all") {
  if (type === "pdf") {
    generating.value = true;
    try {
      const blob = await getPdfBlob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = getFilename("pdf");
      link.click();
      URL.revokeObjectURL(url);
      emit("close");
    } catch (e) {
      alert("Failed to generate PDF.");
    } finally {
      generating.value = false;
    }
  } else {
    zipping.value = true;
    try {
      const zip = new JSZip();

      // 1. PDF Report
      const pdfBlob = await getPdfBlob();
      zip.file(getFilename("pdf"), pdfBlob);

      // 2. CSV Data
      const csvData = generateCsv(props.results);
      zip.file(getFilename("csv"), csvData);

      // 3. PNG Graph
      if (props.chartDataUrl) {
        const base64Data = props.chartDataUrl.split(",")[1];
        zip.file(getFilename("png"), base64Data, { base64: true });
      }

      const content = await zip.generateAsync({ type: "blob" });
      const url = URL.createObjectURL(content);
      const link = document.createElement("a");
      link.href = url;
      link.download = getFilename("zip");
      link.click();
      URL.revokeObjectURL(url);
      emit("close");
    } catch (e) {
      console.error("ZIP creation failed:", e);
      alert("Failed to create ZIP file.");
    } finally {
      zipping.value = false;
    }
  }
}
</script>

<style scoped>
@import "tailwindcss";

/* Component-specific modal sizing and animation */
.modal-content.report-modal {
  @apply w-[90%] max-w-125 animate-[slideIn_0.2s_ease-out];
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-1.25rem);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Component-specific modal header styling */
.modal-header h2 {
  @apply text-xl text-slate-800;
}

/* Component-specific close button styling */
.close-btn {
  @apply p-1 leading-none transition-colors text-slate-400;
}

.close-btn:hover {
  @apply text-slate-500;
}

/* Component-specific body and textarea styling */
.instructions {
  @apply m-0 mb-4 text-slate-500 text-sm;
}

.modal-body textarea {
  @apply w-full p-3.5 border-2 border-slate-200 rounded-lg text-sm font-sans resize-y transition-all;
}

.modal-body textarea:focus {
  @apply outline-none border-blue-500 ring-4 ring-blue-500/10;
}

.modal-body textarea::placeholder {
  @apply text-slate-400;
}

/* Component-specific footer styling */
.modal-footer {
  @apply bg-slate-50 rounded-b-2xl;
}

/* Component-specific button styles */
.btn-secondary {
  @apply border-2 bg-white text-slate-500 font-medium;
}

.btn-secondary:hover {
  @apply border-slate-300 bg-slate-50;
}

.btn-primary {
  @apply bg-gradient-to-br from-blue-500 to-blue-600 font-semibold text-xs sm:text-sm;
}

.btn-primary:hover:not(:disabled) {
  @apply from-blue-600 to-blue-700 -translate-y-px;
}

.btn-assets {
  @apply bg-gradient-to-br from-emerald-500 to-emerald-600 font-semibold text-white rounded-lg text-xs sm:text-sm transition-all;
}

.btn-assets:hover:not(:disabled) {
  @apply from-emerald-600 to-emerald-700 -translate-y-px shadow-md;
}

.btn-assets:disabled {
  @apply opacity-60 cursor-not-allowed;
}

.footer-credits {
  @apply text-center text-[10px] text-slate-400 mt-2;
}

.author-link {
  @apply text-blue-400 hover:text-blue-500 hover:underline transition-colors font-medium;
}

.btn-primary:disabled {
  @apply opacity-60 cursor-not-allowed;
}
</style>
