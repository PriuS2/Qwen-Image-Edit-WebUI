import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { galleryApi } from '@/api'
import type { GalleryItem, GalleryCompareData } from '@/types'
import { ElMessage } from 'element-plus'

export const useGalleryStore = defineStore('gallery', () => {
  // State
  const items = ref<GalleryItem[]>([])
  const total = ref<number>(0)
  const currentItem = ref<GalleryItem | null>(null)
  const compareData = ref<GalleryCompareData | null>(null)
  const isLoading = ref<boolean>(false)
  const limit = ref<number>(20)
  const offset = ref<number>(0)
  const favoritesOnly = ref<boolean>(false)

  // Getters
  const hasItems = computed(() => items.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / limit.value))
  const currentPage = computed(() => Math.floor(offset.value / limit.value) + 1)

  // Actions
  async function fetchItems(reset: boolean = false): Promise<void> {
    if (reset) {
      offset.value = 0
    }

    isLoading.value = true
    try {
      const response = await galleryApi.list({
        limit: limit.value,
        offset: offset.value,
        favorites_only: favoritesOnly.value
      })

      if (response.success) {
        items.value = response.data
        total.value = response.total
      }
    } catch (error) {
      console.error('Failed to fetch gallery items:', error)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchItem(galleryId: string): Promise<void> {
    isLoading.value = true
    try {
      const response = await galleryApi.get(galleryId)
      if (response.success && response.data) {
        currentItem.value = response.data
      }
    } catch (error) {
      console.error('Failed to fetch gallery item:', error)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCompareData(galleryId: string): Promise<void> {
    try {
      const response = await galleryApi.compare(galleryId)
      if (response.success && response.data) {
        compareData.value = response.data
      }
    } catch (error) {
      console.error('Failed to fetch compare data:', error)
    }
  }

  async function toggleFavorite(galleryId: string): Promise<boolean> {
    const item = items.value.find(i => i.id === galleryId)
    if (!item) return false

    try {
      const response = await galleryApi.update(galleryId, {
        is_favorite: !item.is_favorite
      })

      if (response.success) {
        item.is_favorite = !item.is_favorite
        if (currentItem.value?.id === galleryId) {
          currentItem.value.is_favorite = item.is_favorite
        }
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to toggle favorite:', error)
      return false
    }
  }

  async function updateItem(
    galleryId: string,
    updates: { title?: string; description?: string }
  ): Promise<boolean> {
    try {
      const response = await galleryApi.update(galleryId, updates)
      if (response.success) {
        const item = items.value.find(i => i.id === galleryId)
        if (item) {
          if (updates.title) item.title = updates.title
          if (updates.description) item.description = updates.description
        }
        if (currentItem.value?.id === galleryId) {
          if (updates.title) currentItem.value.title = updates.title
          if (updates.description) currentItem.value.description = updates.description
        }
        ElMessage.success('갤러리 항목이 업데이트되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to update item:', error)
      return false
    }
  }

  async function deleteItem(galleryId: string, deleteFiles: boolean = true): Promise<boolean> {
    try {
      const response = await galleryApi.delete(galleryId, deleteFiles)
      if (response.success) {
        items.value = items.value.filter(i => i.id !== galleryId)
        total.value--
        if (currentItem.value?.id === galleryId) {
          currentItem.value = null
        }
        ElMessage.success('갤러리 항목이 삭제되었습니다.')
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to delete item:', error)
      return false
    }
  }

  function setPage(page: number): void {
    offset.value = (page - 1) * limit.value
    fetchItems()
  }

  function setFavoritesOnly(value: boolean): void {
    favoritesOnly.value = value
    fetchItems(true)
  }

  function clearCurrentItem(): void {
    currentItem.value = null
    compareData.value = null
  }

  return {
    // State
    items,
    total,
    currentItem,
    compareData,
    isLoading,
    limit,
    offset,
    favoritesOnly,
    // Getters
    hasItems,
    totalPages,
    currentPage,
    // Actions
    fetchItems,
    fetchItem,
    fetchCompareData,
    toggleFavorite,
    updateItem,
    deleteItem,
    setPage,
    setFavoritesOnly,
    clearCurrentItem
  }
})
