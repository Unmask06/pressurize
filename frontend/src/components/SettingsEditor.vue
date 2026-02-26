<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-content settings-modal">
      <div class="modal-header">
        <h3>Simulation Settings</h3>
        <button class="close-btn" @click="close">×</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label for="step_time">Step Time (s)</label>
          <input
            id="step_time"
            type="number"
            v-model.number="localDt"
            step="0.1"
            min="0.5"
          />
          <span class="hint"
            >Controls simulation resolution. Smaller = more accurate,
            slower.</span
          >
        </div>

        <div class="form-group">
          <label for="max_sim_time"
            >Max Simulation Time ({{ getUnit("time") }})</label
          >
          <input
            id="max_sim_time"
            type="number"
            v-model.number="localMaxSimTime"
            step="50"
            min="1"
          />
          <span class="hint"
            >Maximum time to run simulation. Prevents infinite loops.</span
          >
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="close">Cancel</button>
        <button class="btn-primary" @click="apply">Apply Settings</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { getUnit } from "../api/client";

const props = defineProps<{
  currentDt: number;
  currentMaxSimTime: number;
}>();

const emit = defineEmits(["close", "apply"]);

const localDt = ref(props.currentDt);
const localMaxSimTime = ref(props.currentMaxSimTime);

function apply() {
  emit("apply", { dt: localDt.value, maxSimTime: localMaxSimTime.value });
  console.log("Applied settings:", {
    dt: localDt.value,
    maxSimTime: localMaxSimTime.value,
  });
}

function close() {
  emit("close");
}
</script>

<style scoped>
@import "tailwindcss";

/* Component-specific modal sizing */
.modal-content.settings-modal {
  @apply w-[90%] max-w-100;
}

.form-group {
  @apply flex flex-col gap-2;
}

.form-group label {
  @apply text-xs font-bold uppercase tracking-wider;
  color: var(--xergiz-text-muted);
}

.form-group input {
  @apply py-2.5 px-3 border rounded-md text-base transition-colors;
  background: var(--xergiz-dark);
  border-color: var(--xergiz-border);
  color: var(--xergiz-text);
}

.form-group input:hover {
  border-color: var(--xergiz-border-hover);
}

.form-group input:focus {
  @apply outline-none ring-2;
  border-color: var(--xergiz-teal);
  ring-color: var(--xergiz-teal-dim);
}

.hint {
  @apply text-xs;
  color: var(--xergiz-text-muted);
}
</style>
