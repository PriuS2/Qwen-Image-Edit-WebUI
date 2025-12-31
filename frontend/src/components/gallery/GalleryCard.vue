<script setup lang="ts">
import { computed } from 'vue'
import type { GalleryItem } from '@/types'
import { Star, StarFilled, Download, Delete } from '@element-plus/icons-vue'

const props = defineProps<{
  item: GalleryItem
}>()

const emit = defineEmits<{
  (e: 'click'): void
  (e: 'favorite'): void
  (e: 'download'): void
  (e: 'delete'): void
}>()

const thumbnailSrc = computed(() => props.item.thumbnail_url || props.item.image_url)
const isFavorite = computed(() => props.item.is_favorite)
</script>

<template>
  <div class="gallery-card" @click="emit('click')">
    <!-- Thumbnail -->
    <div class="thumbnail-container">
      <img :src="thumbnailSrc" :alt="item.title" class="thumbnail" />
      
      <!-- Favorite badge -->
      <div v-if="isFavorite" class="favorite-badge">
        <StarFilled class="w-3 h-3" />
      </div>
    </div>

    <!-- Info -->
    <div class="card-info">
      <h4 class="title">{{ item.title || '제목 없음' }}</h4>
      <p class="prompt">{{ item.metadata?.prompt || '' }}</p>
    </div>

    <!-- Actions -->
    <div class="card-actions" @click.stop>
      <el-button
        :icon="isFavorite ? StarFilled : Star"
        size="small"
        text
        :class="{ 'text-yellow-500': isFavorite }"
        @click="emit('favorite')"
        title="즐겨찾기"
      />
      <el-button
        :icon="Download"
        size="small"
        text
        @click="emit('download')"
        title="다운로드"
      />
      <el-button
        :icon="Delete"
        size="small"
        text
        class="text-red-500"
        @click="emit('delete')"
        title="삭제"
      />
    </div>
  </div>
</template>

<style scoped>
.gallery-card {
  @apply bg-white rounded-xl border border-gray-200 overflow-hidden 
         hover:shadow-lg hover:border-primary-300 transition-all cursor-pointer;
}

.thumbnail-container {
  @apply relative aspect-square bg-gray-100;
}

.thumbnail {
  @apply w-full h-full object-cover;
}

.favorite-badge {
  @apply absolute top-2 right-2 p-1 bg-yellow-500 text-white rounded-full;
}

.card-info {
  @apply p-3;
}

.title {
  @apply text-sm font-medium text-gray-800 truncate;
}

.prompt {
  @apply text-xs text-gray-500 truncate mt-1;
}

.card-actions {
  @apply flex justify-center gap-1 py-2 border-t border-gray-100;
}
</style>
