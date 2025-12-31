<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGalleryStore } from '@/stores/gallery'
import { useEditStore } from '@/stores/edit'
import { galleryApi } from '@/api'
import GalleryCard from '@/components/gallery/GalleryCard.vue'
import GalleryModal from '@/components/gallery/GalleryModal.vue'
import { Star, StarFilled, Refresh } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const galleryStore = useGalleryStore()
const editStore = useEditStore()

// Modal state
const modalVisible = ref(false)

onMounted(() => {
  galleryStore.fetchItems(true)
})

// Handlers
const handleCardClick = async (item: typeof galleryStore.items[0]) => {
  galleryStore.currentItem = item
  await galleryStore.fetchCompareData(item.id)
  modalVisible.value = true
}

const handleFavorite = async (itemId?: string) => {
  const id = itemId || galleryStore.currentItem?.id
  if (id) {
    await galleryStore.toggleFavorite(id)
  }
}

const handleDownload = (itemId?: string) => {
  const id = itemId || galleryStore.currentItem?.id
  if (id) {
    const url = galleryApi.getDownloadUrl(id)
    const link = document.createElement('a')
    link.href = url
    link.download = `image-${id}.png`
    link.click()
  }
}

const handleDelete = async (itemId?: string) => {
  const id = itemId || galleryStore.currentItem?.id
  if (!id) return

  try {
    await ElMessageBox.confirm(
      '이 이미지를 삭제하시겠습니까?',
      '삭제 확인',
      {
        confirmButtonText: '삭제',
        cancelButtonText: '취소',
        type: 'warning'
      }
    )
    
    await galleryStore.deleteItem(id)
    if (modalVisible.value) {
      modalVisible.value = false
    }
  } catch {
    // Cancelled
  }
}

const handleReEdit = () => {
  if (galleryStore.currentItem) {
    // Navigate to edit page with the image
    // In a real implementation, you'd load the image into the edit store
    modalVisible.value = false
    router.push('/edit')
  }
}

const handleRefresh = () => {
  galleryStore.fetchItems(true)
}

const toggleFavoritesOnly = () => {
  galleryStore.setFavoritesOnly(!galleryStore.favoritesOnly)
}
</script>

<template>
  <div class="gallery-view">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">갤러리</h2>
      <div class="flex gap-2">
        <el-button
          :icon="galleryStore.favoritesOnly ? StarFilled : Star"
          :type="galleryStore.favoritesOnly ? 'primary' : 'default'"
          @click="toggleFavoritesOnly"
        >
          즐겨찾기
        </el-button>
        <el-button :icon="Refresh" @click="handleRefresh" :loading="galleryStore.isLoading">
          새로고침
        </el-button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="galleryStore.isLoading && !galleryStore.hasItems" class="loading-container">
      <el-skeleton :rows="4" animated />
    </div>

    <!-- Empty State -->
    <div v-else-if="!galleryStore.hasItems" class="empty-state">
      <div class="text-center py-16">
        <div class="text-6xl mb-4">🖼️</div>
        <h3 class="text-xl font-medium text-gray-700 mb-2">
          {{ galleryStore.favoritesOnly ? '즐겨찾기한 이미지가 없습니다' : '갤러리가 비어있습니다' }}
        </h3>
        <p class="text-gray-500">이미지를 편집하면 여기에 저장됩니다.</p>
      </div>
    </div>

    <!-- Gallery Grid -->
    <div v-else class="gallery-grid">
      <GalleryCard
        v-for="item in galleryStore.items"
        :key="item.id"
        :item="item"
        @click="handleCardClick(item)"
        @favorite="handleFavorite(item.id)"
        @download="handleDownload(item.id)"
        @delete="handleDelete(item.id)"
      />
    </div>

    <!-- Pagination -->
    <div v-if="galleryStore.totalPages > 1" class="pagination-container">
      <el-pagination
        :current-page="galleryStore.currentPage"
        :page-size="galleryStore.limit"
        :total="galleryStore.total"
        layout="prev, pager, next"
        @current-change="galleryStore.setPage"
      />
    </div>

    <!-- Detail Modal -->
    <GalleryModal
      v-model:visible="modalVisible"
      :item="galleryStore.currentItem"
      :compare-data="galleryStore.compareData"
      @favorite="handleFavorite()"
      @download="handleDownload()"
      @delete="handleDelete()"
      @re-edit="handleReEdit"
    />
  </div>
</template>

<style scoped>
.gallery-view {
  @apply max-w-6xl mx-auto;
}

.loading-container {
  @apply py-8;
}

.empty-state {
  @apply card;
}

.gallery-grid {
  @apply grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4;
}

.pagination-container {
  @apply flex justify-center mt-8;
}
</style>
