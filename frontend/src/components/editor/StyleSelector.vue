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
@reference "tailwindcss";

.style-selector {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .style-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.style-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  border-radius: 0.75rem;
  border: 2px solid #e5e7eb;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.style-card:hover {
  border-color: #7dd3fc;
  background-color: rgba(240, 249, 255, 0.3);
}

.style-card.is-selected {
  border-color: #0ea5e9;
  background-color: #f0f9ff;
  box-shadow: 0 0 0 2px #bae6fd;
}

.style-card.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.style-card.is-disabled:hover {
  border-color: #e5e7eb;
  background-color: white;
}

.style-icon {
  font-size: 1.875rem;
  margin-bottom: 0.5rem;
}

.style-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
}

.style-desc {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.125rem;
}
</style>
