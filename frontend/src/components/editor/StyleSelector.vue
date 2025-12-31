<script setup lang="ts">
import { computed } from 'vue'
import type { StyleType } from '@/types'

const props = defineProps<{
  modelValue: StyleType | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: StyleType): void
}>()

interface StyleOption {
  value: StyleType
  label: string
  description: string
  icon: string
}

const styles: StyleOption[] = [
  { value: 'ghibli', label: 'Ghibli', description: '지브리 스타일', icon: '🏯' },
  { value: 'anime', label: 'Anime', description: '애니메이션', icon: '🎌' },
  { value: 'realistic', label: 'Realistic', description: '사실적', icon: '📷' },
  { value: 'oil_painting', label: 'Oil Paint', description: '유화', icon: '🎨' },
  { value: 'watercolor', label: 'Watercolor', description: '수채화', icon: '💧' },
  { value: 'sketch', label: 'Sketch', description: '스케치', icon: '✏️' },
  { value: 'cyberpunk', label: 'Cyberpunk', description: '사이버펑크', icon: '🤖' },
  { value: 'vintage', label: 'Vintage', description: '빈티지', icon: '📼' }
]

const selectedStyle = computed(() => props.modelValue)

const selectStyle = (style: StyleType) => {
  if (!props.disabled) {
    emit('update:modelValue', style)
  }
}
</script>

<template>
  <div class="style-selector">
    <label class="label">스타일 선택</label>
    <div class="style-grid">
      <button
        v-for="style in styles"
        :key="style.value"
        class="style-card"
        :class="{ 
          'is-selected': selectedStyle === style.value,
          'is-disabled': disabled
        }"
        :disabled="disabled"
        @click="selectStyle(style.value)"
      >
        <span class="style-icon">{{ style.icon }}</span>
        <span class="style-label">{{ style.label }}</span>
        <span class="style-desc">{{ style.description }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.style-selector {
  @apply space-y-3;
}

.label {
  @apply block text-sm font-medium text-gray-700;
}

.style-grid {
  @apply grid grid-cols-2 sm:grid-cols-4 gap-3;
}

.style-card {
  @apply flex flex-col items-center p-4 rounded-xl border-2 border-gray-200 
         bg-white hover:border-primary-300 hover:bg-primary-50/30 
         transition-all cursor-pointer;
}

.style-card.is-selected {
  @apply border-primary-500 bg-primary-50 ring-2 ring-primary-200;
}

.style-card.is-disabled {
  @apply opacity-50 cursor-not-allowed hover:border-gray-200 hover:bg-white;
}

.style-icon {
  @apply text-3xl mb-2;
}

.style-label {
  @apply text-sm font-medium text-gray-800;
}

.style-desc {
  @apply text-xs text-gray-500 mt-0.5;
}
</style>
