<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: number
  label: string
  min: number
  max: number
  step?: number
  disabled?: boolean
  showInput?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
}>()

const sliderValue = computed({
  get: () => props.modelValue,
  set: (value: number) => emit('update:modelValue', value)
})

const stepValue = computed(() => props.step || 1)
</script>

<template>
  <div class="parameter-slider">
    <div class="header">
      <label class="label">{{ label }}</label>
      <span class="value">{{ modelValue }}</span>
    </div>
    <div class="slider-container">
      <el-slider
        v-model="sliderValue"
        :min="min"
        :max="max"
        :step="stepValue"
        :disabled="disabled"
        :show-tooltip="false"
      />
      <el-input-number
        v-if="showInput"
        v-model="sliderValue"
        :min="min"
        :max="max"
        :step="stepValue"
        :disabled="disabled"
        size="small"
        controls-position="right"
        class="input-number"
      />
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.parameter-slider {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.value {
  font-size: 0.875rem;
  color: #0284c7;
  font-weight: 500;
}

.slider-container {
  display: flex;
  align-items: center;
}

.input-number {
  margin-left: 0.75rem;
  width: 6rem;
}
</style>
