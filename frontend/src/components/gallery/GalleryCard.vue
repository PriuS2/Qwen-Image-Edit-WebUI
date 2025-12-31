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
        <StarFilled class="badge-icon" />
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
        :class="{ 'favorite-active': isFavorite }"
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
        class="delete-btn"
        @click="emit('delete')"
        title="삭제"
      />
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.gallery-card {
  background-color: white;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.gallery-card:hover {
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  border-color: #7dd3fc;
}

.thumbnail-container {
  position: relative;
  aspect-ratio: 1;
  background-color: #f3f4f6;
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.favorite-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.25rem;
  background-color: #eab308;
  color: white;
  border-radius: 9999px;
}

.badge-icon {
  width: 0.75rem;
  height: 0.75rem;
}

.card-info {
  padding: 0.75rem;
}

.title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.prompt {
  font-size: 0.75rem;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 0.25rem;
}

.card-actions {
  display: flex;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.5rem;
  border-top: 1px solid #f3f4f6;
}

.favorite-active {
  color: #eab308;
}

.delete-btn {
  color: #ef4444;
}
</style>
