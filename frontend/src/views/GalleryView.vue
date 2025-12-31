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

const handleReEdit = async () => {
  if (galleryStore.currentItem) {
    modalVisible.value = false
    
    // 편집된 이미지 URL 또는 원본 이미지 URL 사용
    const imageUrl = galleryStore.compareData?.edited_url || galleryStore.currentItem.image_url
    
    // editStore에 이미지 설정
    const success = await editStore.setImageFromUrl(imageUrl)
    
    if (success) {
      // 이전 프롬프트 설정 (있으면)
      if (galleryStore.currentItem.metadata?.prompt) {
        editStore.updateParams({
          prompt: galleryStore.currentItem.metadata.prompt
        })
      }
      
      router.push('/edit')
    }
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
    <div class="page-header">
      <h2 class="page-title">갤러리</h2>
      <div class="header-actions">
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
    <div v-else-if="!galleryStore.hasItems" class="empty-state card">
      <div class="empty-content">
        <div class="empty-icon">🖼️</div>
        <h3 class="empty-title">
          {{ galleryStore.favoritesOnly ? '즐겨찾기한 이미지가 없습니다' : '갤러리가 비어있습니다' }}
        </h3>
        <p class="empty-desc">이미지를 편집하면 여기에 저장됩니다.</p>
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
@reference "tailwindcss";

.gallery-view {
  max-width: 72rem;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.loading-container {
  padding: 2rem 0;
}

.card {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #f3f4f6;
  padding: 1rem;
}

.empty-state {
  padding: 4rem 1rem;
}

.empty-content {
  text-align: center;
}

.empty-icon {
  font-size: 3.75rem;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.empty-desc {
  color: #6b7280;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

@media (min-width: 640px) {
  .gallery-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .gallery-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}
</style>
