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
        class="ml-3 w-24"
      />
    </div>
  </div>
</template>

<style scoped>
.parameter-slider {
  @apply space-y-2;
}

.header {
  @apply flex justify-between items-center;
}

.label {
  @apply text-sm font-medium text-gray-700;
}

.value {
  @apply text-sm text-primary-600 font-medium;
}

.slider-container {
  @apply flex items-center;
}
</style>
