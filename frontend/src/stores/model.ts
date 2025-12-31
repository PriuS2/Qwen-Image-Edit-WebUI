import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { modelApi } from '@/api'
import type { ModelStatus, AvailableModel, DownloadStatus, OptimizationSettings } from '@/types'
import { ElMessage } from 'element-plus'

export const useModelStore = defineStore('model', () => {
  // State
  const status = ref<ModelStatus | null>(null)
  const availableModels = ref<AvailableModel[]>([])
  const downloadStatus = ref<DownloadStatus | null>(null)
  const isLoading = ref<boolean>(false)
  const isDownloading = ref<boolean>(false)

  // Getters
  const isLoaded = computed(() => status.value?.is_loaded ?? false)
  const currentModel = computed(() => status.value?.model_name ?? null)
  const vramUsed = computed(() => status.value?.vram_used_gb ?? 0)
  const vramTotal = computed(() => status.value?.vram_total_gb ?? 0)
  const optimization = computed(() => status.value?.optimization ?? null)

  // Actions
  async function fetchStatus(): Promise<void> {
    try {
      const response = await modelApi.getStatus()
      if (response.success && response.data) {
        status.value = response.data
      }
    } catch (error) {
      console.error('Failed to fetch model status:', error)
    }
  }

  async function fetchAvailableModels(): Promise<void> {
    try {
      const response = await modelApi.getAvailable()
      if (response.success) {
        availableModels.value = response.models
      }
    } catch (error) {
      console.error('Failed to fetch available models:', error)
    }
  }

  async function loadModel(options: {
    model_name?: string
    optimization?: Partial<OptimizationSettings>
    force_reload?: boolean
  } = {}): Promise<boolean> {
    isLoading.value = true
    try {
      const response = await modelApi.load(options)
      if (response.success && response.data) {
        status.value = response.data
        ElMessage.success('모델이 로드되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to load model:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function unloadModel(): Promise<boolean> {
    isLoading.value = true
    try {
      const response = await modelApi.unload()
      if (response.success) {
        await fetchStatus()
        ElMessage.success(`모델이 언로드되었습니다. (${response.vram_freed_gb.toFixed(1)} GB 해제됨)`)
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to unload model:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function startDownload(modelName?: string, forceDownload: boolean = false): Promise<boolean> {
    isDownloading.value = true
    try {
      const response = await modelApi.download({ model_name: modelName, force_download: forceDownload })
      if (response.success && response.data) {
        downloadStatus.value = response.data
        ElMessage.success('다운로드가 시작되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to start download:', error)
      return false
    }
  }

  async function fetchDownloadStatus(): Promise<void> {
    try {
      const response = await modelApi.getDownloadStatus()
      if (response.success && response.data) {
        downloadStatus.value = response.data
        if (response.data.status === 'completed' || response.data.status === 'failed' || response.data.status === 'cancelled') {
          isDownloading.value = false
        }
      }
    } catch (error) {
      console.error('Failed to fetch download status:', error)
    }
  }

  async function cancelDownload(): Promise<boolean> {
    try {
      const response = await modelApi.cancelDownload()
      if (response.success) {
        downloadStatus.value = response.data ?? null
        isDownloading.value = false
        ElMessage.info('다운로드가 취소되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to cancel download:', error)
      return false
    }
  }

  async function updateOptimization(
    settings: Partial<OptimizationSettings>,
    applyImmediately: boolean = false
  ): Promise<boolean> {
    try {
      const response = await modelApi.updateOptimization({
        optimization: settings as OptimizationSettings,
        apply_immediately: applyImmediately
      })
      if (response.success) {
        if (applyImmediately) {
          await fetchStatus()
        }
        ElMessage.success('최적화 설정이 업데이트되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to update optimization:', error)
      return false
    }
  }

  return {
    // State
    status,
    availableModels,
    downloadStatus,
    isLoading,
    isDownloading,
    // Getters
    isLoaded,
    currentModel,
    vramUsed,
    vramTotal,
    optimization,
    // Actions
    fetchStatus,
    fetchAvailableModels,
    loadModel,
    unloadModel,
    startDownload,
    fetchDownloadStatus,
    cancelDownload,
    updateOptimization
  }
})
