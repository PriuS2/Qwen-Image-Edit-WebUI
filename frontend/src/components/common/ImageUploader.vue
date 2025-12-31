<script setup lang="ts">
import { ref, computed } from 'vue'
import { UploadFilled, Close, Plus } from '@element-plus/icons-vue'

export interface ImageItem {
  file: File
  url: string
  id: string
}

const props = defineProps<{
  modelValue?: File | null
  previewUrl?: string | null
  // Multi image support
  multiple?: boolean
  images?: ImageItem[]
  maxImages?: number
  disabled?: boolean
  accept?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', file: File | null): void
  (e: 'change', file: File | null): void
  // Multi image events
  (e: 'add', files: File[]): void
  (e: 'remove', id: string): void
  (e: 'update:images', images: ImageItem[]): void
}>()

const isDragging = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)

const acceptTypes = computed(() => props.accept || 'image/*')
const hasImage = computed(() => props.multiple ? (props.images?.length ?? 0) > 0 : !!props.previewUrl)
const maxCount = computed(() => props.maxImages || 3)
const canAddMore = computed(() => props.multiple && (props.images?.length ?? 0) < maxCount.value)
const imageCount = computed(() => props.images?.length ?? 0)

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  if (!props.disabled) {
    isDragging.value = true
  }
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  
  if (props.disabled) return
  
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    if (props.multiple) {
      // Multi-image mode
      const imageFiles: File[] = []
      const remaining = maxCount.value - imageCount.value
      for (let i = 0; i < Math.min(files.length, remaining); i++) {
        if (files[i].type.startsWith('image/')) {
          imageFiles.push(files[i])
        }
      }
      if (imageFiles.length > 0) {
        emit('add', imageFiles)
      }
    } else {
      // Single-image mode
      const file = files[0]
      if (file.type.startsWith('image/')) {
        emitFile(file)
      }
    }
  }
}

const handleClick = () => {
  if (!props.disabled && (props.multiple ? canAddMore.value : true)) {
    inputRef.value?.click()
  }
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    if (props.multiple) {
      // Multi-image mode
      const imageFiles: File[] = []
      const remaining = maxCount.value - imageCount.value
      for (let i = 0; i < Math.min(files.length, remaining); i++) {
        if (files[i].type.startsWith('image/')) {
          imageFiles.push(files[i])
        }
      }
      if (imageFiles.length > 0) {
        emit('add', imageFiles)
      }
    } else {
      // Single-image mode
      emitFile(files[0])
    }
  }
  // Reset input
  target.value = ''
}

const emitFile = (file: File) => {
  emit('update:modelValue', file)
  emit('change', file)
}

const clearImage = (e: Event) => {
  e.stopPropagation()
  emit('update:modelValue', null)
  emit('change', null)
}

const removeImage = (e: Event, id: string) => {
  e.stopPropagation()
  emit('remove', id)
}
</script>

<template>
  <!-- Multi-image mode -->
  <div v-if="multiple" class="multi-uploader">
    <div class="image-grid">
      <!-- Uploaded images -->
      <div
        v-for="img in images"
        :key="img.id"
        class="image-item"
      >
        <img :src="img.url" alt="Preview" class="item-image" />
        <button
          v-if="!disabled"
          class="remove-btn"
          @click="removeImage($event, img.id)"
          title="이미지 제거"
        >
          <Close class="w-3 h-3" />
        </button>
      </div>

      <!-- Add more button -->
      <div
        v-if="canAddMore"
        class="add-item"
        :class="{ 'is-dragging': isDragging, 'is-disabled': disabled }"
        @click="handleClick"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
      >
        <Plus class="add-icon" />
        <span class="add-text">추가</span>
      </div>
    </div>

    <div class="upload-info">
      <span class="image-count">{{ imageCount }} / {{ maxCount }} 이미지</span>
      <span class="mode-badge" :class="imageCount > 1 ? 'multi' : 'single'">
        {{ imageCount > 1 ? 'Multi 모드' : 'Single 모드' }}
      </span>
    </div>

    <input
      ref="inputRef"
      type="file"
      :accept="acceptTypes"
      :multiple="true"
      class="hidden"
      @change="handleFileChange"
    />
  </div>

  <!-- Single-image mode (original) -->
  <div
    v-else
    class="image-uploader"
    :class="{
      'is-dragging': isDragging,
      'has-image': hasImage,
      'is-disabled': disabled
    }"
    @click="handleClick"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <input
      ref="inputRef"
      type="file"
      :accept="acceptTypes"
      class="hidden"
      @change="handleFileChange"
    />

    <!-- Preview -->
    <template v-if="hasImage">
      <div class="preview-container">
        <img :src="previewUrl!" alt="Preview" class="preview-image" />
        <button
          v-if="!disabled"
          class="clear-btn"
          @click="clearImage"
          title="이미지 제거"
        >
          <Close class="w-4 h-4" />
        </button>
      </div>
    </template>

    <!-- Upload placeholder -->
    <template v-else>
      <div class="upload-placeholder">
        <UploadFilled class="upload-icon" />
        <p class="upload-text">이미지를 드래그하거나 클릭하여 업로드</p>
        <p class="upload-hint">PNG, JPG, WEBP 지원</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

/* Multi-image mode styles */
.multi-uploader {
  width: 100%;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #f9fafb;
}

.item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  padding: 0.25rem;
  background-color: #ef4444;
  color: white;
  border-radius: 9999px;
  transition: background-color 0.2s;
  box-shadow: 0 2px 4px rgb(0 0 0 / 0.1);
}

.remove-btn:hover {
  background-color: #dc2626;
}

.add-item {
  aspect-ratio: 1;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #f9fafb;
}

.add-item:hover {
  border-color: #38bdf8;
  background-color: rgba(240, 249, 255, 0.3);
}

.add-item.is-dragging {
  border-color: #0ea5e9;
  background-color: #f0f9ff;
}

.add-item.is-disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.add-icon {
  width: 2rem;
  height: 2rem;
  color: #9ca3af;
}

.add-text {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.upload-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
  padding: 0 0.25rem;
}

.image-count {
  font-size: 0.875rem;
  color: #6b7280;
}

.mode-badge {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
}

.mode-badge.single {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.mode-badge.multi {
  background-color: #fce7f3;
  color: #be185d;
}

/* Single-image mode styles (original) */
.image-uploader {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border: 2px dashed #d1d5db;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  background-color: #f9fafb;
}

.image-uploader:hover {
  border-color: #38bdf8;
  background-color: rgba(240, 249, 255, 0.3);
}

.image-uploader.is-dragging {
  border-color: #0ea5e9;
  background-color: #f0f9ff;
}

.image-uploader.has-image {
  border-style: solid;
  border-color: #e5e7eb;
}

.image-uploader.is-disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.preview-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.clear-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.375rem;
  background-color: #ef4444;
  color: white;
  border-radius: 9999px;
  transition: background-color 0.2s;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.clear-btn:hover {
  background-color: #dc2626;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  text-align: center;
}

.upload-icon {
  width: 3rem;
  height: 3rem;
  color: #9ca3af;
  margin-bottom: 0.75rem;
}

.upload-text {
  color: #4b5563;
  font-weight: 500;
}

.upload-hint {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.hidden {
  display: none;
}
</style>
