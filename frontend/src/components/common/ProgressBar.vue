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
      return 'bg-green-500'
    case 'failed':
      return 'bg-red-500'
    default:
      return 'bg-primary-500'
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
.progress-container {
  @apply w-full flex items-center gap-3;
}

.progress-bar {
  @apply flex-1 h-2.5 bg-gray-200 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full rounded-full transition-all duration-300 ease-out;
}

.progress-text {
  @apply text-sm text-gray-600 min-w-[80px] text-right;
}
</style>
