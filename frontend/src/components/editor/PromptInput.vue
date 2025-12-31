<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
  rows?: number
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const inputValue = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value)
})
</script>

<template>
  <div class="prompt-input">
    <label v-if="label" class="label">{{ label }}</label>
    <el-input
      v-model="inputValue"
      type="textarea"
      :rows="rows || 3"
      :placeholder="placeholder || '프롬프트를 입력하세요...'"
      :disabled="disabled"
      resize="none"
    />
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.prompt-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}
</style>
