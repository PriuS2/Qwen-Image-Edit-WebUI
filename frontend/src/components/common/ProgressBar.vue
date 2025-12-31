<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  progress: number
  status?: 'pending' | 'processing' | 'completed' | 'failed'
  showText?: boolean
}>()

const progressText = computed(() => {
  switch (props.status) {
    case 'pending':
      return '대기 중...'
    case 'processing':
      return `처리 중... ${props.progress}%`
    case 'completed':
      return '완료!'
    case 'failed':
      return '실패'
    default:
      return `${props.progress}%`
  }
})

const progressClass = computed(() => {
  switch (props.status) {
    case 'completed':
      return 'fill-success'
    case 'failed':
      return 'fill-error'
    default:
      return 'fill-primary'
  }
})
</script>

<template>
  <div class="progress-container">
    <div class="progress-bar">
      <div
        class="progress-fill"
        :class="progressClass"
        :style="{ width: `${Math.min(100, Math.max(0, progress))}%` }"
      ></div>
    </div>
    <span v-if="showText" class="progress-text">{{ progressText }}</span>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.progress-container {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-bar {
  flex: 1;
  height: 0.625rem;
  background-color: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: all 0.3s ease-out;
}

.fill-primary {
  background-color: #0ea5e9;
}

.fill-success {
  background-color: #22c55e;
}

.fill-error {
  background-color: #ef4444;
}

.progress-text {
  font-size: 0.875rem;
  color: #4b5563;
  min-width: 80px;
  text-align: right;
}
</style>
