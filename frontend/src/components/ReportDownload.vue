<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content report-modal">
      <div class="modal-header">
        <h2>📥 Download Report</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <p class="instructions">Add any notes you'd like to include in the report (optional):</p>
        <textarea 
          v-model="notes" 
          placeholder="Enter your notes here... (e.g., purpose of simulation, observations, etc.)"
          rows="5"
        ></textarea>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">Cancel</button>
        <button class="btn-primary" @click="generatePdf" :disabled="generating">
          {{ generating ? 'Generating...' : '📄 Generate PDF' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { jsPDF } from 'jspdf';

const props = defineProps<{
  inputs: Record<string, any>;
  kpis: {
    peakFlow: number;
    finalPressure: number;
    equilibriumTime: number;
    totalMass: number;
  };
  chartDataUrl: string | null;
}>();

const emit = defineEmits(['close']);

const notes = ref('');
const generating = ref(false);

function formatValue(value: any, decimals = 2): string {
  if (typeof value === 'number') {
    return value.toLocaleString('en-US', { 
      minimumFractionDigits: decimals, 
      maximumFractionDigits: decimals 
    });
  }
  return String(value);
}

function formatInputLabel(key: string): string {
  const labels: Record<string, string> = {
    p_up_psig: 'Upstream Pressure',
    p_down_init_psig: 'Downstream Pressure',
    volume_ft3: 'Volume',
    valve_id_inch: 'Valve ID',
    opening_time_s: 'Opening Time',
    temp_f: 'Temperature',
    molar_mass: 'Molar Mass (MW)',
    z_factor: 'Z-Factor',
    k_ratio: 'Heat Capacity Ratio (k)',
    discharge_coeff: 'Discharge Coefficient (Cd)',
    opening_mode: 'Opening Mode',
    k_curve: 'Curve Factor (k)',
    property_mode: 'Property Mode',
    composition: 'Gas Composition',
    dt: 'Time Step'
  };
  return labels[key] || key;
}

function formatInputUnit(key: string): string {
  const units: Record<string, string> = {
    p_up_psig: 'psig',
    p_down_init_psig: 'psig',
    volume_ft3: 'ft³',
    valve_id_inch: 'in',
    opening_time_s: 's',
    temp_f: '°F',
    molar_mass: 'g/mol',
    z_factor: '',
    k_ratio: '',
    discharge_coeff: '',
    opening_mode: '',
    k_curve: '',
    property_mode: '',
    composition: '',
    dt: 's'
  };
  return units[key] || '';
}

async function generatePdf() {
  generating.value = true;
  
  try {
    const doc = new jsPDF('p', 'mm', 'a4');
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 15;
    let y = margin;

    // === HEADER ===
    doc.setFillColor(30, 41, 59); // Dark slate
    doc.rect(0, 0, pageWidth, 35, 'F');
    
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.text('Pressurization Simulator', margin, 18);
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const timestamp = new Date().toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    doc.text(`Report Generated: ${timestamp}`, margin, 28);
    
    y = 45;
    doc.setTextColor(30, 41, 59);

    // === SIMULATION INPUTS ===
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Simulation Inputs', margin, y);
    y += 8;

    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    
    const inputKeys = Object.keys(props.inputs).filter(k => k !== 'dt' && k !== 'composition');
    const colWidth = (pageWidth - 2 * margin) / 2;
    let col = 0;

    for (const key of inputKeys) {
      const value = props.inputs[key];
      const label = formatInputLabel(key);
      const unit = formatInputUnit(key);
      const displayValue = `${formatValue(value, 2)}${unit ? ' ' + unit : ''}`;
      
      const xPos = margin + col * colWidth;
      doc.setFont('helvetica', 'bold');
      doc.text(`${label}:`, xPos, y);
      doc.setFont('helvetica', 'normal');
      doc.text(displayValue, xPos + 50, y);
      
      col++;
      if (col >= 2) {
        col = 0;
        y += 6;
      }
    }
    if (col !== 0) y += 6;

    // Special handling for Composition if in composition mode
    if (props.inputs.property_mode === 'composition' && props.inputs.composition) {
      y += 2;
      doc.setFont('helvetica', 'bold');
      doc.text('Gas Composition:', margin, y);
      y += 5;
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8);
      const compLines = doc.splitTextToSize(props.inputs.composition, pageWidth - 2 * margin);
      doc.text(compLines, margin, y);
      y += (compLines.length * 4) + 2;
      doc.setFontSize(9);
    }
    
    y += 5;

    // === KPI OUTPUTS ===
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Key Performance Indicators', margin, y);
    y += 10;

    const kpiData = [
      { label: 'Peak Flow Rate', value: props.kpis.peakFlow, unit: 'lb/hr', decimals: 0 },
      { label: 'Final Pressure', value: props.kpis.finalPressure, unit: 'psig', decimals: 1 },
      { label: 'Equilibrium Time', value: props.kpis.equilibriumTime, unit: 'seconds', decimals: 1 },
      { label: 'Total Mass Flow', value: props.kpis.totalMass, unit: 'lb', decimals: 1 }
    ];

    const kpiBoxWidth = (pageWidth - 2 * margin - 15) / 4;
    kpiData.forEach((kpi, i) => {
      const xPos = margin + i * (kpiBoxWidth + 5);
      
      // KPI Box
      doc.setFillColor(248, 250, 252);
      doc.roundedRect(xPos, y, kpiBoxWidth, 22, 2, 2, 'F');
      
      // Label
      doc.setFontSize(8);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(100, 116, 139);
      doc.text(kpi.label, xPos + kpiBoxWidth / 2, y + 6, { align: 'center' });
      
      // Value
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(30, 41, 59);
      doc.text(formatValue(kpi.value, kpi.decimals), xPos + kpiBoxWidth / 2, y + 14, { align: 'center' });
      
      // Unit
      doc.setFontSize(7);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(100, 116, 139);
      doc.text(kpi.unit, xPos + kpiBoxWidth / 2, y + 19, { align: 'center' });
    });
    
    y += 30;
    doc.setTextColor(30, 41, 59);

    // === GRAPH ===
    if (props.chartDataUrl) {
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('Simulation Results Chart', margin, y);
      y += 5;

      const imgWidth = pageWidth - 2 * margin;
      const imgHeight = imgWidth * 0.5; // Aspect ratio
      
      doc.addImage(props.chartDataUrl, 'PNG', margin, y, imgWidth, imgHeight);
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
      doc.setFont('helvetica', 'bold');
      doc.text('Notes', margin, y);
      y += 8;

      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      
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
        { align: 'center' }
      );
    }

    // Save the PDF
    const filename = `pressurization-report-${new Date().toISOString().slice(0, 10)}.pdf`;
    doc.save(filename);
    
    emit('close');
  } catch (error) {
    console.error('PDF generation failed:', error);
    alert('Failed to generate PDF. Please try again.');
  } finally {
    generating.value = false;
  }
}
</script>

<style scoped src="../styles/ReportDownload.css"></style>
