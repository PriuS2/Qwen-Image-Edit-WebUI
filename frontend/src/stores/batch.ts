import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { batchApi } from '@/api'
import type { BatchJob, EditParams } from '@/types'
import { ElMessage } from 'element-plus'

interface BatchImage {
  id: string
  file: File
  previewUrl: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  resultUrl?: string
  error?: string
}

export const useBatchStore = defineStore('batch', () => {
  // State
  const images = ref<BatchImage[]>([])
  const currentJobId = ref<string | null>(null)
  const currentJob = ref<BatchJob | null>(null)
  const isProcessing = ref<boolean>(false)
  const commonParams = ref<EditParams>({
    prompt: '',
    negative_prompt: '',
    num_inference_steps: 20,
    true_cfg_scale: 4.0,
    guidance_scale: 1.0,
    seed: -1,
    num_images_per_prompt: 1
  })

  // Getters
  const hasImages = computed(() => images.value.length > 0)
  const canSubmit = computed(() => hasImages.value && commonParams.value.prompt.trim() && !isProcessing.value)
  const totalProgress = computed(() => {
    if (images.value.length === 0) return 0
    const total = images.value.reduce((sum, img) => sum + img.progress, 0)
    return Math.round(total / images.value.length)
  })

  // Actions
  function addImages(files: File[]) {
    const newImages: BatchImage[] = files.map(file => ({
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      file,
      previewUrl: URL.createObjectURL(file),
      status: 'pending',
      progress: 0
    }))
    images.value.push(...newImages)
  }

  function removeImage(id: string) {
    const index = images.value.findIndex(img => img.id === id)
    if (index !== -1) {
      URL.revokeObjectURL(images.value[index].previewUrl)
      images.value.splice(index, 1)
    }
  }

  function clearImages() {
    images.value.forEach(img => URL.revokeObjectURL(img.previewUrl))
    images.value = []
  }

  function updateParams(params: Partial<EditParams>) {
    commonParams.value = { ...commonParams.value, ...params }
  }

  async function submitBatch(): Promise<boolean> {
    if (!canSubmit.value) return false

    isProcessing.value = true
    
    // Convert images to base64
    const items = await Promise.all(
      images.value.map(async (img) => {
        const base64 = await fileToBase64(img.file)
        return {
          image: base64,
          params: commonParams.value
        }
      })
    )

    try {
      const response = await batchApi.submit({
        items,
        response_format: 'url',
        save_to_gallery: true
      })

      if (response.success) {
        currentJobId.value = response.job_id
        ElMessage.success(`배치 작업이 시작되었습니다. (${response.total_items}개 이미지)`)
        
        // Start polling
        pollBatchStatus()
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to submit batch:', error)
      isProcessing.value = false
      return false
    }
  }

  async function pollBatchStatus() {
    if (!currentJobId.value) return

    const poll = async () => {
      try {
        const response = await batchApi.getStatus(currentJobId.value!)
        if (response.success && response.data) {
          currentJob.value = response.data
          
          // Update individual image progress (simplified)
          const progress = response.data.progress
          images.value.forEach((img, index) => {
            const itemProgress = Math.min(100, (progress / 100) * images.value.length - index) * 100
            img.progress = Math.max(0, Math.min(100, itemProgress))
            
            if (img.progress >= 100) {
              img.status = 'completed'
            } else if (img.progress > 0) {
              img.status = 'processing'
            }
          })

          if (response.data.status === 'completed') {
            isProcessing.value = false
            images.value.forEach(img => {
              img.status = 'completed'
              img.progress = 100
            })
            ElMessage.success('배치 처리가 완료되었습니다.')
            return
          } else if (response.data.status === 'failed') {
            isProcessing.value = false
            images.value.forEach(img => {
              if (img.status !== 'completed') {
                img.status = 'failed'
                img.error = response.data?.error_message || '처리 실패'
              }
            })
            ElMessage.error('배치 처리가 실패했습니다.')
            return
          }
          
          // Continue polling
          setTimeout(poll, 1000)
        }
      } catch (error) {
        console.error('Polling error:', error)
        setTimeout(poll, 2000)
      }
    }

    poll()
  }

  async function cancelBatch(): Promise<boolean> {
    if (!currentJobId.value) return false

    try {
      const response = await batchApi.cancel(currentJobId.value)
      if (response.success) {
        isProcessing.value = false
        ElMessage.info('배치 작업이 취소되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to cancel batch:', error)
      return false
    }
  }

  function reset() {
    clearImages()
    currentJobId.value = null
    currentJob.value = null
    isProcessing.value = false
    commonParams.value = {
      prompt: '',
      negative_prompt: '',
      num_inference_steps: 20,
      true_cfg_scale: 4.0,
      guidance_scale: 1.0,
      seed: -1,
      num_images_per_prompt: 1
    }
  }

  return {
    // State
    images,
    currentJobId,
    currentJob,
    isProcessing,
    commonParams,
    // Getters
    hasImages,
    canSubmit,
    totalProgress,
    // Actions
    addImages,
    removeImage,
    clearImages,
    updateParams,
    submitBatch,
    cancelBatch,
    reset
  }
})

// Helper function
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}
