<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { GalleryItem, GalleryCompareData } from '@/types'
import { 
  Star, 
  StarFilled, 
  Download, 
  Delete, 
  Edit
} from '@element-plus/icons-vue'

const props = defineProps<{
  visible: boolean
  item: GalleryItem | null
  compareData: GalleryCompareData | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'favorite'): void
  (e: 'download'): void
  (e: 'delete'): void
  (e: 'reEdit'): void
}>()

const sliderValue = ref(50)

const dialogVisible = computed({
  get: () => props.visible,
  set: (value: boolean) => emit('update:visible', value)
})

watch(() => props.item, () => {
  sliderValue.value = 50
})

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('ko-KR')
}
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="이미지 상세"
    width="800px"
    :close-on-click-modal="false"
  >
    <template v-if="item">
      <!-- Image Compare Slider -->
      <div v-if="compareData" class="compare-container">
        <div class="compare-slider">
          <div 
            class="compare-original"
            :style="{ clipPath: `inset(0 ${100 - sliderValue}% 0 0)` }"
          >
            <img :src="compareData.original_url" alt="Original" class="compare-image" />
            <span class="compare-label label-left">원본</span>
          </div>
          <div class="compare-edited">
            <img :src="compareData.edited_url" alt="Edited" class="compare-image" />
            <span class="compare-label label-right">편집</span>
          </div>
          <input
            v-model="sliderValue"
            type="range"
            min="0"
            max="100"
            class="slider-input"
          />
          <div 
            class="slider-handle"
            :style="{ left: `${sliderValue}%` }"
          ></div>
        </div>
      </div>

      <!-- Single Image -->
      <div v-else class="single-image-container">
        <img :src="item.image_url" :alt="item.title" class="single-image" />
      </div>

      <!-- Info Section -->
      <div class="info-section">
        <h3 class="info-title">{{ item.title || '제목 없음' }}</h3>
        <p v-if="item.description" class="info-desc">{{ item.description }}</p>

        <div class="meta-info">
          <div class="meta-item">
            <span class="meta-label">프롬프트:</span>
            <span class="meta-value">{{ item.metadata?.prompt || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">시드:</span>
            <span class="meta-value">{{ item.metadata?.seed ?? '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">해상도:</span>
            <span class="meta-value">{{ item.metadata?.width }}x{{ item.metadata?.height }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">생성일:</span>
            <span class="meta-value">{{ formatDate(item.created_at) }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- Actions -->
    <template #footer>
      <div class="footer-actions">
        <div class="left-actions">
          <el-button
            :icon="item?.is_favorite ? StarFilled : Star"
            :class="{ 'favorite-active': item?.is_favorite }"
            @click="emit('favorite')"
          >
            즐겨찾기
          </el-button>
          <el-button :icon="Download" @click="emit('download')">
            다운로드
          </el-button>
          <el-button :icon="Edit" @click="emit('reEdit')">
            재편집
          </el-button>
        </div>
        <div class="right-actions">
          <el-button type="danger" :icon="Delete" @click="emit('delete')">
            삭제
          </el-button>
          <el-button @click="dialogVisible = false">
            닫기
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
@reference "tailwindcss";

.compare-container {
  margin-bottom: 1.5rem;
}

.compare-slider {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  background-color: #f3f4f6;
  border-radius: 0.5rem;
  overflow: hidden;
}

.compare-original,
.compare-edited {
  position: absolute;
  inset: 0;
}

.compare-original {
  z-index: 10;
}

.compare-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.compare-label {
  position: absolute;
  bottom: 1rem;
  padding: 0.25rem 0.75rem;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 0.875rem;
  border-radius: 0.25rem;
}

.label-left {
  left: 1rem;
}

.label-right {
  right: 1rem;
}

.slider-input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: ew-resize;
  z-index: 20;
}

.slider-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 0.25rem;
  background-color: white;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  z-index: 10;
  transform: translateX(-50%);
}

.single-image-container {
  width: 100%;
  aspect-ratio: 1;
  background-color: #f3f4f6;
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.single-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-title {
  font-size: 1.125rem;
  font-weight: 500;
  color: #1f2937;
}

.info-desc {
  color: #4b5563;
}

.meta-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  font-size: 0.875rem;
}

.meta-item {
  display: flex;
  gap: 0.5rem;
}

.meta-label {
  color: #6b7280;
}

.meta-value {
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
}

.left-actions,
.right-actions {
  display: flex;
  gap: 0.5rem;
}

.favorite-active {
  color: #eab308;
}
</style>
