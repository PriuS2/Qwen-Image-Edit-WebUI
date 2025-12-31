import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, setApiKey } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const apiKey = ref<string>(localStorage.getItem('api_key') || 'qwen-image-edit-default-key')
  const isVerified = ref<boolean>(false)
  const isVerifying = ref<boolean>(false)

  // Getters
  const hasApiKey = computed(() => !!apiKey.value)

  // Actions
  async function verify(): Promise<boolean> {
    isVerifying.value = true
    try {
      const result = await authApi.verify()
      isVerified.value = result.success
      return result.success
    } catch {
      isVerified.value = false
      return false
    } finally {
      isVerifying.value = false
    }
  }

  function updateApiKey(newKey: string): void {
    apiKey.value = newKey
    setApiKey(newKey)
    isVerified.value = false
  }

  return {
    // State
    apiKey,
    isVerified,
    isVerifying,
    // Getters
    hasApiKey,
    // Actions
    verify,
    updateApiKey
  }
})
