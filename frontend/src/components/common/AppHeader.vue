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
@reference "tailwindcss";

.app-header {
  background-color: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}

@media (min-width: 768px) {
  .app-header {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  display: none;
}

@media (min-width: 640px) {
  .logo-text {
    display: block;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.model-status {
  display: none;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

@media (min-width: 768px) {
  .model-status {
    display: flex;
  }
}

.status-dot {
  width: 0.625rem;
  height: 0.625rem;
  border-radius: 9999px;
}

.status-dot.is-loaded {
  background-color: #22c55e;
}

.status-dot.is-unloaded {
  background-color: #9ca3af;
}

.status-text {
  color: #4b5563;
}

.vram-text {
  color: #9ca3af;
}

.quick-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
