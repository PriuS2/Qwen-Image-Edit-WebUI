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
        <UploadFilled class="w-12 h-12 text-gray-400 mb-3" />
        <p class="text-gray-600 font-medium">이미지를 드래그하거나 클릭하여 업로드</p>
        <p class="text-gray-400 text-sm mt-1">PNG, JPG, WEBP 지원</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.image-uploader {
  @apply relative w-full aspect-square border-2 border-dashed border-gray-300 rounded-xl 
         flex items-center justify-center cursor-pointer transition-all overflow-hidden
         bg-gray-50 hover:border-primary-400 hover:bg-primary-50/30;
}

.image-uploader.is-dragging {
  @apply border-primary-500 bg-primary-50;
}

.image-uploader.has-image {
  @apply border-solid border-gray-200;
}

.image-uploader.is-disabled {
  @apply cursor-not-allowed opacity-60;
}

.preview-container {
  @apply relative w-full h-full;
}

.preview-image {
  @apply w-full h-full object-contain;
}

.clear-btn {
  @apply absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full 
         hover:bg-red-600 transition-colors shadow-md;
}

.upload-placeholder {
  @apply flex flex-col items-center justify-center p-6 text-center;
}
</style>
