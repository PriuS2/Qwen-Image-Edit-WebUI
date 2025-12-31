<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useModelStore } from '@/stores/model'
import { Setting, Picture } from '@element-plus/icons-vue'

const router = useRouter()
const modelStore = useModelStore()

const isModelLoaded = computed(() => modelStore.isLoaded)
const vramUsage = computed(() => {
  if (!modelStore.status) return ''
  return `${modelStore.status.vram_used_gb.toFixed(1)} / ${modelStore.status.vram_total_gb.toFixed(1)} GB`
})

const navigateTo = (path: string) => {
  router.push(path)
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo-icon">🎨</div>
      <h1 class="logo-text">Qwen Image Edit</h1>
    </div>

    <div class="header-right">
      <!-- Model Status -->
      <div class="model-status">
        <span 
          class="status-dot"
          :class="isModelLoaded ? 'is-loaded' : 'is-unloaded'"
        ></span>
        <span class="status-text">
          {{ isModelLoaded ? '모델 로드됨' : '모델 미로드' }}
        </span>
        <span v-if="isModelLoaded" class="vram-text">
          | VRAM: {{ vramUsage }}
        </span>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <el-tooltip content="설정" placement="bottom">
          <el-button 
            :icon="Setting" 
            circle 
            @click="navigateTo('/settings')"
          />
        </el-tooltip>
        <el-tooltip content="갤러리" placement="bottom">
          <el-button 
            :icon="Picture" 
            circle 
            @click="navigateTo('/gallery')"
          />
        </el-tooltip>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  @apply bg-white border-b border-gray-200 px-4 md:px-6 py-3 
         flex items-center justify-between shadow-sm;
}

.header-left {
  @apply flex items-center gap-3;
}

.logo-icon {
  @apply text-2xl;
}

.logo-text {
  @apply text-lg md:text-xl font-bold text-gray-800 hidden sm:block;
}

.header-right {
  @apply flex items-center gap-4 md:gap-6;
}

.model-status {
  @apply hidden md:flex items-center gap-2 text-sm;
}

.status-dot {
  @apply w-2.5 h-2.5 rounded-full;
}

.status-dot.is-loaded {
  @apply bg-green-500;
}

.status-dot.is-unloaded {
  @apply bg-gray-400;
}

.status-text {
  @apply text-gray-600;
}

.vram-text {
  @apply text-gray-400;
}

.quick-actions {
  @apply flex items-center gap-2;
}
</style>
