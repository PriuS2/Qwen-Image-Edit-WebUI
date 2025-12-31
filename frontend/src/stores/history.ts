import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { historyApi } from '@/api'
import type { HistoryItem } from '@/types'
import { ElMessage } from 'element-plus'

export const useHistoryStore = defineStore('history', () => {
  // State
  const items = ref<HistoryItem[]>([])
  const total = ref<number>(0)
  const currentItem = ref<HistoryItem | null>(null)
  const currentPosition = ref<number>(0)
  const canUndo = ref<boolean>(false)
  const canRedo = ref<boolean>(false)
  const isLoading = ref<boolean>(false)
  const sessionId = ref<string | null>(null)
  const limit = ref<number>(50)
  const offset = ref<number>(0)

  // Getters
  const hasItems = computed(() => items.value.length > 0)
  const currentImagePath = computed(() => {
    if (!currentItem.value) return null
    return currentPosition.value === 0 
      ? currentItem.value.original_image_path 
      : currentItem.value.edited_image_path
  })

  // Actions
  async function fetchItems(reset: boolean = false): Promise<void> {
    if (reset) {
      offset.value = 0
    }

    isLoading.value = true
    try {
      const response = await historyApi.list({
        session_id: sessionId.value ?? undefined,
        limit: limit.value,
        offset: offset.value
      })

      if (response.success) {
        items.value = response.data
        total.value = response.total
      }
    } catch (error) {
      console.error('Failed to fetch history items:', error)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchItem(historyId: string): Promise<void> {
    isLoading.value = true
    try {
      const response = await historyApi.get(historyId)
      if (response.success && response.data) {
        currentItem.value = response.data
        currentPosition.value = response.data.position
        updateUndoRedoState()
      }
    } catch (error) {
      console.error('Failed to fetch history item:', error)
    } finally {
      isLoading.value = false
    }
  }

  async function undo(historyId: string): Promise<boolean> {
    if (!canUndo.value) return false

    isLoading.value = true
    try {
      const response = await historyApi.undo(historyId)
      if (response.success) {
        currentPosition.value = response.current_position
        canUndo.value = response.can_undo
        canRedo.value = response.can_redo
        ElMessage.success('이전 상태로 복원되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to undo:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function redo(historyId: string): Promise<boolean> {
    if (!canRedo.value) return false

    isLoading.value = true
    try {
      const response = await historyApi.redo(historyId)
      if (response.success) {
        currentPosition.value = response.current_position
        canUndo.value = response.can_undo
        canRedo.value = response.can_redo
        ElMessage.success('다음 상태로 복원되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to redo:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function deleteItem(historyId: string): Promise<boolean> {
    isLoading.value = true
    try {
      const response = await historyApi.delete(historyId)
      if (response.success) {
        items.value = items.value.filter(i => i.id !== historyId)
        total.value--
        if (currentItem.value?.id === historyId) {
          currentItem.value = null
        }
        ElMessage.success('히스토리가 삭제되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to delete history item:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  function setSessionId(id: string | null): void {
    sessionId.value = id
    fetchItems(true)
  }

  function updateUndoRedoState(): void {
    if (!currentItem.value) {
      canUndo.value = false
      canRedo.value = false
      return
    }
    // This would be determined by the API response
    // For now, basic logic based on position
    canUndo.value = currentPosition.value > 0
    canRedo.value = items.value.some(item => 
      item.parent_id === currentItem.value?.id && 
      item.position > currentPosition.value
    )
  }

  function clearCurrent(): void {
    currentItem.value = null
    currentPosition.value = 0
    canUndo.value = false
    canRedo.value = false
  }

  return {
    // State
    items,
    total,
    currentItem,
    currentPosition,
    canUndo,
    canRedo,
    isLoading,
    sessionId,
    limit,
    offset,
    // Getters
    hasItems,
    currentImagePath,
    // Actions
    fetchItems,
    fetchItem,
    undo,
    redo,
    deleteItem,
    setSessionId,
    clearCurrent
  }
})
