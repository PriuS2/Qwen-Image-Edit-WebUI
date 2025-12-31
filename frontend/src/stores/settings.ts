import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { settingsApi } from '@/api'
import type { AppSettings, OptimizationSettings } from '@/types'
import { ElMessage } from 'element-plus'

const defaultSettings: AppSettings = {
  auto_unload: {
    enabled: true,
    timeout_minutes: 30
  },
  auto_load: {
    enabled: true
  },
  default_model: 'ovedrive/Qwen-Image-Edit-2511-4bit',
  torch_dtype: 'bfloat16',
  optimization: {
    enable_model_cpu_offload: true,
    enable_attention_slicing: true,
    enable_vae_slicing: true,
    enable_vae_tiling: false,
    enable_xformers: false
  },
  edit_defaults: {
    num_inference_steps: 20,
    true_cfg_scale: 4.0,
    guidance_scale: 1.0
  },
  gallery: {
    max_history_per_session: 10,
    auto_cleanup_days: 7,
    thumbnail_size: 256
  }
}

export const useSettingsStore = defineStore('settings', () => {
  // State
  const settings = ref<AppSettings>({ ...defaultSettings })
  const isLoading = ref<boolean>(false)
  const isDirty = ref<boolean>(false)

  // Getters
  const autoUnload = computed(() => settings.value.auto_unload)
  const autoLoad = computed(() => settings.value.auto_load)
  const optimization = computed(() => settings.value.optimization)
  const editDefaults = computed(() => settings.value.edit_defaults)
  const gallerySettings = computed(() => settings.value.gallery)

  // Actions
  async function fetchSettings(): Promise<void> {
    isLoading.value = true
    try {
      const response = await settingsApi.getAll()
      if (response.success && response.data) {
        settings.value = response.data
        isDirty.value = false
      }
    } catch (error) {
      console.error('Failed to fetch settings:', error)
    } finally {
      isLoading.value = false
    }
  }

  async function saveSettings(): Promise<boolean> {
    isLoading.value = true
    try {
      const response = await settingsApi.updateAll(settings.value)
      if (response.success) {
        isDirty.value = false
        ElMessage.success('설정이 저장되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to save settings:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function resetSettings(): Promise<boolean> {
    isLoading.value = true
    try {
      const response = await settingsApi.reset()
      if (response.success && response.data) {
        settings.value = response.data
        isDirty.value = false
        ElMessage.success('설정이 초기화되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to reset settings:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  function updateAutoUnload(enabled: boolean, timeoutMinutes?: number): void {
    settings.value.auto_unload.enabled = enabled
    if (timeoutMinutes !== undefined) {
      settings.value.auto_unload.timeout_minutes = timeoutMinutes
    }
    isDirty.value = true
  }

  function updateAutoLoad(enabled: boolean): void {
    settings.value.auto_load.enabled = enabled
    isDirty.value = true
  }

  function updateOptimization(optimization: Partial<OptimizationSettings>): void {
    settings.value.optimization = {
      ...settings.value.optimization,
      ...optimization
    }
    isDirty.value = true
  }

  function updateEditDefaults(defaults: Partial<typeof settings.value.edit_defaults>): void {
    settings.value.edit_defaults = {
      ...settings.value.edit_defaults,
      ...defaults
    }
    isDirty.value = true
  }

  function updateGallerySettings(gallerySettings: Partial<typeof settings.value.gallery>): void {
    settings.value.gallery = {
      ...settings.value.gallery,
      ...gallerySettings
    }
    isDirty.value = true
  }

  return {
    // State
    settings,
    isLoading,
    isDirty,
    // Getters
    autoUnload,
    autoLoad,
    optimization,
    editDefaults,
    gallerySettings,
    // Actions
    fetchSettings,
    saveSettings,
    resetSettings,
    updateAutoUnload,
    updateAutoLoad,
    updateOptimization,
    updateEditDefaults,
    updateGallerySettings
  }
})
