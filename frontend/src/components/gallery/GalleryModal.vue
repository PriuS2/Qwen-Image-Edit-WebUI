<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { GalleryItem, GalleryCompareData } from '@/types'
import { 
  Star, 
  StarFilled, 
  Download, 
  Delete, 
  Edit,
  Close
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
const isEditing = ref(false)
const editTitle = ref('')
const editDescription = ref('')

const dialogVisible = computed({
  get: () => props.visible,
  set: (value: boolean) => emit('update:visible', value)
})

watch(() => props.item, (newItem) => {
  if (newItem) {
    editTitle.value = newItem.title
    editDescription.value = newItem.description
  }
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
            <span class="compare-label left">원본</span>
          </div>
          <div class="compare-edited">
            <img :src="compareData.edited_url" alt="Edited" class="compare-image" />
            <span class="compare-label right">편집</span>
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
        <template v-if="!isEditing">
          <h3 class="text-lg font-medium text-gray-800 mb-2">{{ item.title || '제목 없음' }}</h3>
          <p v-if="item.description" class="text-gray-600 mb-4">{{ item.description }}</p>
        </template>
        <template v-else>
          <el-input v-model="editTitle" placeholder="제목" class="mb-2" />
          <el-input v-model="editDescription" type="textarea" placeholder="설명" :rows="2" />
        </template>

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
      <div class="flex justify-between">
        <div class="flex gap-2">
          <el-button
            :icon="item?.is_favorite ? StarFilled : Star"
            :class="{ 'text-yellow-500': item?.is_favorite }"
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
        <div class="flex gap-2">
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
.compare-container {
  @apply mb-6;
}

.compare-slider {
  @apply relative w-full aspect-square bg-gray-100 rounded-lg overflow-hidden;
}

.compare-original,
.compare-edited {
  @apply absolute inset-0;
}

.compare-original {
  @apply z-10;
}

.compare-image {
  @apply w-full h-full object-contain;
}

.compare-label {
  @apply absolute bottom-4 px-3 py-1 bg-black/50 text-white text-sm rounded;
}

.compare-label.left {
  @apply left-4;
}

.compare-label.right {
  @apply right-4;
}

.slider-input {
  @apply absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20;
}

.slider-handle {
  @apply absolute top-0 bottom-0 w-1 bg-white shadow-lg z-10 -translate-x-1/2;
}

.single-image-container {
  @apply w-full aspect-square bg-gray-100 rounded-lg overflow-hidden mb-6;
}

.single-image {
  @apply w-full h-full object-contain;
}

.info-section {
  @apply space-y-4;
}

.meta-info {
  @apply grid grid-cols-2 gap-2 text-sm;
}

.meta-item {
  @apply flex gap-2;
}

.meta-label {
  @apply text-gray-500;
}

.meta-value {
  @apply text-gray-800 truncate;
}
</style>
