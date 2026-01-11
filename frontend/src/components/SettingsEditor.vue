<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content settings-modal">
      <div class="modal-header">
        <h3>Simulation Settings</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label for="step_time">Step Time (s)</label>
          <input 
            id="step_time" 
            type="number" 
            v-model.number="localDt" 
            step="0.01" 
            min="0.001"
          />
          <span class="hint">Controls simulation resolution. Smaller = more accurate, slower.</span>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">Cancel</button>
        <button class="btn-primary" @click="apply">Apply Settings</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  currentDt: number;
}>();

const emit = defineEmits(['close', 'apply']);

const localDt = ref(props.currentDt);

function apply() {
  emit('apply', localDt.value);
}
</script>

<style scoped src="../styles/SettingsEditor.css"></style>
