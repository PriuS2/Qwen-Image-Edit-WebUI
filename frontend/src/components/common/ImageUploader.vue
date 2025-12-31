<script setup lang="ts">
import { ref, computed } from 'vue'
import { UploadFilled, Close } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue?: File | null
  previewUrl?: string | null
  disabled?: boolean
  accept?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', file: File | null): void
  (e: 'change', file: File | null): void
}>()

const isDragging = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)

const acceptTypes = computed(() => props.accept || 'image/*')
const hasImage = computed(() => !!props.previewUrl)

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
    const file = files[0]
    if (file.type.startsWith('image/')) {
      emitFile(file)
    }
  }
}

const handleClick = () => {
  if (!props.disabled) {
    inputRef.value?.click()
  }
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    emitFile(files[0])
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
</script>

<template>
  <div
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
