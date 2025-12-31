import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { editApi, createJobProgressSocket, type JobProgressWebSocket } from '@/api'
import type { EditParams, JobStatus, JobResult, StyleType, ProgressMessage } from '@/types'
import { ElMessage } from 'element-plus'

export const useEditStore = defineStore('edit', () => {
  // State
  const currentImage = ref<File | null>(null)
  const currentImageUrl = ref<string | null>(null)
  const resultImage = ref<string | null>(null)
  const jobId = ref<string | null>(null)
  const jobStatus = ref<JobStatus | null>(null)
  const progress = ref<number>(0)
  const isProcessing = ref<boolean>(false)
  const error = ref<string | null>(null)
  const sessionId = ref<string>(`session-${Date.now()}`)

  // Default edit params
  const params = ref<EditParams>({
    prompt: '',
    negative_prompt: '',
    num_inference_steps: 20,
    true_cfg_scale: 4.0,
    guidance_scale: 1.0,
    seed: -1,
    num_images_per_prompt: 1
  })

  // WebSocket connection
  let wsConnection: JobProgressWebSocket | null = null

  // Getters
  const hasImage = computed(() => !!currentImage.value || !!currentImageUrl.value)
  const canEdit = computed(() => hasImage.value && !!params.value.prompt && !isProcessing.value)
  const lastResult = computed(() => jobStatus.value?.result ?? null)

  // Actions
  function setImage(file: File): void {
    currentImage.value = file
    currentImageUrl.value = URL.createObjectURL(file)
    resultImage.value = null
    error.value = null
  }

  function clearImage(): void {
    if (currentImageUrl.value) {
      URL.revokeObjectURL(currentImageUrl.value)
    }
    currentImage.value = null
    currentImageUrl.value = null
    resultImage.value = null
    error.value = null
  }

  function updateParams(newParams: Partial<EditParams>): void {
    params.value = { ...params.value, ...newParams }
  }

  function resetParams(): void {
    params.value = {
      prompt: '',
      negative_prompt: '',
      num_inference_steps: 20,
      true_cfg_scale: 4.0,
      guidance_scale: 1.0,
      seed: -1,
      num_images_per_prompt: 1
    }
  }

  async function submitEdit(): Promise<boolean> {
    if (!currentImage.value) {
      ElMessage.warning('이미지를 먼저 업로드해주세요.')
      return false
    }

    if (!params.value.prompt) {
      ElMessage.warning('프롬프트를 입력해주세요.')
      return false
    }

    isProcessing.value = true
    error.value = null
    progress.value = 0

    try {
      const response = await editApi.editSingleUpload(
        currentImage.value,
        params.value,
        {
          response_format: 'url',
          session_id: sessionId.value,
          save_to_gallery: true
        }
      )

      if (response.success) {
        jobId.value = response.job_id
        connectWebSocket(response.job_id)
        return true
      }
      return false
    } catch (err) {
      error.value = '편집 요청 실패'
      isProcessing.value = false
      return false
    }
  }

  async function submitStyleTransfer(
    style: StyleType,
    intensity: number = 1.0,
    additionalPrompt?: string
  ): Promise<boolean> {
    if (!currentImage.value) {
      ElMessage.warning('이미지를 먼저 업로드해주세요.')
      return false
    }

    isProcessing.value = true
    error.value = null
    progress.value = 0

    try {
      const response = await editApi.styleTransferUpload(
        currentImage.value,
        style,
        {
          intensity,
          additional_prompt: additionalPrompt,
          response_format: 'url',
          session_id: sessionId.value,
          save_to_gallery: true
        }
      )

      if (response.success) {
        jobId.value = response.job_id
        connectWebSocket(response.job_id)
        return true
      }
      return false
    } catch (err) {
      error.value = '스타일 변환 요청 실패'
      isProcessing.value = false
      return false
    }
  }

  function connectWebSocket(jobIdValue: string): void {
    disconnectWebSocket()

    wsConnection = createJobProgressSocket(
      jobIdValue,
      (message: ProgressMessage) => {
        progress.value = message.progress
        jobStatus.value = {
          job_id: message.job_id,
          status: message.status,
          progress: message.progress,
          result: message.result,
          error: message.error
        }

        if (message.status === 'completed' && message.result) {
          resultImage.value = message.result.image
          isProcessing.value = false
          ElMessage.success('이미지 편집이 완료되었습니다.')
        } else if (message.status === 'failed') {
          error.value = message.error || '편집 실패'
          isProcessing.value = false
          ElMessage.error(error.value)
        }
      },
      {
        onError: () => {
          error.value = 'WebSocket 연결 오류'
          // Fallback to polling
          startPolling(jobIdValue)
        },
        onClose: () => {
          wsConnection = null
        }
      }
    )
  }

  function disconnectWebSocket(): void {
    if (wsConnection) {
      wsConnection.close()
      wsConnection = null
    }
  }

  // Polling fallback
  let pollingInterval: number | null = null

  function startPolling(jobIdValue: string): void {
    stopPolling()
    pollingInterval = window.setInterval(async () => {
      try {
        const status = await editApi.getJobStatus(jobIdValue)
        progress.value = status.progress
        jobStatus.value = status

        if (status.status === 'completed' && status.result) {
          resultImage.value = status.result.image
          isProcessing.value = false
          ElMessage.success('이미지 편집이 완료되었습니다.')
          stopPolling()
        } else if (status.status === 'failed') {
          error.value = status.error || '편집 실패'
          isProcessing.value = false
          ElMessage.error(error.value)
          stopPolling()
        }
      } catch (err) {
        console.error('Polling error:', err)
      }
    }, 1000)
  }

  function stopPolling(): void {
    if (pollingInterval !== null) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  }

  function reset(): void {
    disconnectWebSocket()
    stopPolling()
    clearImage()
    resetParams()
    jobId.value = null
    jobStatus.value = null
    progress.value = 0
    isProcessing.value = false
    error.value = null
  }

  return {
    // State
    currentImage,
    currentImageUrl,
    resultImage,
    jobId,
    jobStatus,
    progress,
    isProcessing,
    error,
    sessionId,
    params,
    // Getters
    hasImage,
    canEdit,
    lastResult,
    // Actions
    setImage,
    clearImage,
    updateParams,
    resetParams,
    submitEdit,
    submitStyleTransfer,
    reset
  }
})
