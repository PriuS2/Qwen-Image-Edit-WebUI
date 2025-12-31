<script setup lang="ts">
import { ref } from 'vue'
import { useBatchStore } from '@/stores/batch'
import PromptInput from '@/components/editor/PromptInput.vue'
import ParameterSlider from '@/components/editor/ParameterSlider.vue'
import ProgressBar from '@/components/common/ProgressBar.vue'
import { 
  UploadFilled, 
  Close, 
  VideoPlay, 
  Delete,
  CircleClose
} from '@element-plus/icons-vue'

const batchStore = useBatchStore()

// File input ref
const fileInputRef = ref<HTMLInputElement | null>(null)

// Handlers
const handleFilesChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    const imageFiles = Array.from(files).filter(f => f.type.startsWith('image/'))
    batchStore.addImages(imageFiles)
  }
  target.value = ''
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const imageFiles = Array.from(files).filter(f => f.type.startsWith('image/'))
    batchStore.addImages(imageFiles)
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
}

const openFilePicker = () => {
  fileInputRef.value?.click()
}

const handleSubmit = async () => {
  await batchStore.submitBatch()
}

const handleCancel = async () => {
  await batchStore.cancelBatch()
}

const handleReset = () => {
  batchStore.reset()
}

const getStatusClass = (status: string) => {
  switch (status) {
    case 'completed': return 'bg-green-500'
    case 'processing': return 'bg-blue-500'
    case 'failed': return 'bg-red-500'
    default: return 'bg-gray-400'
  }
}
</script>

<template>
  <div class="batch-view">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">배치 처리</h2>

    <!-- Upload Area -->
    <div 
      class="card mb-6"
      @drop="handleDrop"
      @dragover="handleDragOver"
    >
      <div 
        class="upload-zone"
        :class="{ 'has-images': batchStore.hasImages }"
        @click="openFilePicker"
      >
        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          multiple
          class="hidden"
          @change="handleFilesChange"
        />
        <UploadFilled class="w-10 h-10 text-gray-400 mb-2" />
        <p class="text-gray-600">이미지를 드래그하거나 클릭하여 업로드</p>
        <p class="text-gray-400 text-sm mt-1">여러 이미지를 한 번에 선택할 수 있습니다</p>
      </div>
    </div>

    <!-- Image Grid -->
    <div v-if="batchStore.hasImages" class="card mb-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-sm font-medium text-gray-600">
          업로드된 이미지 ({{ batchStore.images.length }}개)
        </h3>
        <el-button 
          size="small" 
          :icon="Delete" 
          @click="batchStore.clearImages"
          :disabled="batchStore.isProcessing"
        >
          모두 삭제
        </el-button>
      </div>

      <div class="image-grid">
        <div 
          v-for="image in batchStore.images" 
          :key="image.id"
          class="image-item"
        >
          <div class="image-thumbnail">
            <img :src="image.previewUrl" :alt="image.file.name" />
            
            <!-- Status indicator -->
            <div 
              class="status-dot"
              :class="getStatusClass(image.status)"
            ></div>

            <!-- Remove button -->
            <button
              v-if="!batchStore.isProcessing"
              class="remove-btn"
              @click="batchStore.removeImage(image.id)"
            >
              <Close class="w-3 h-3" />
            </button>

            <!-- Progress overlay -->
            <div v-if="image.status === 'processing'" class="progress-overlay">
              <span class="text-white text-sm font-medium">{{ image.progress }}%</span>
            </div>

            <!-- Completed overlay -->
            <div v-if="image.status === 'completed'" class="completed-overlay">
              ✓
            </div>
          </div>
          <p class="image-name">{{ image.file.name }}</p>
        </div>

        <!-- Add more button -->
        <div 
          v-if="!batchStore.isProcessing"
          class="add-more-btn"
          @click="openFilePicker"
        >
          <span class="text-3xl text-gray-400">+</span>
        </div>
      </div>
    </div>

    <!-- Common Prompt -->
    <div class="card mb-6">
      <h3 class="text-sm font-medium text-gray-600 mb-4">공통 설정</h3>
      
      <div class="space-y-4">
        <PromptInput
          :model-value="batchStore.commonParams.prompt"
          @update:model-value="batchStore.updateParams({ prompt: $event })"
          label="공통 프롬프트"
          placeholder="모든 이미지에 적용할 프롬프트를 입력하세요..."
          :disabled="batchStore.isProcessing"
        />

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ParameterSlider
            :model-value="batchStore.commonParams.num_inference_steps || 20"
            @update:model-value="batchStore.updateParams({ num_inference_steps: $event })"
            label="추론 스텝"
            :min="1"
            :max="100"
            :disabled="batchStore.isProcessing"
          />
          <ParameterSlider
            :model-value="batchStore.commonParams.true_cfg_scale || 4.0"
            @update:model-value="batchStore.updateParams({ true_cfg_scale: $event })"
            label="True CFG 스케일"
            :min="1"
            :max="20"
            :step="0.1"
            :disabled="batchStore.isProcessing"
          />
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="card mb-6">
      <div class="flex items-center justify-center gap-4">
        <el-button
          v-if="!batchStore.isProcessing"
          type="primary"
          size="large"
          :icon="VideoPlay"
          :disabled="!batchStore.canSubmit"
          @click="handleSubmit"
        >
          배치 처리 시작
        </el-button>

        <el-button
          v-else
          type="danger"
          size="large"
          :icon="CircleClose"
          @click="handleCancel"
        >
          취소
        </el-button>

        <el-button
          v-if="!batchStore.isProcessing"
          :icon="Delete"
          @click="handleReset"
        >
          초기화
        </el-button>
      </div>
    </div>

    <!-- Overall Progress -->
    <div v-if="batchStore.isProcessing" class="card">
      <h3 class="text-sm font-medium text-gray-600 mb-3">전체 진행 상황</h3>
      <ProgressBar
        :progress="batchStore.totalProgress"
        :status="batchStore.currentJob?.status"
        show-text
      />
    </div>
  </div>
</template>

<style scoped>
.batch-view {
  @apply max-w-6xl mx-auto;
}

.upload-zone {
  @apply flex flex-col items-center justify-center py-10 border-2 border-dashed 
         border-gray-300 rounded-lg cursor-pointer hover:border-primary-400 
         hover:bg-primary-50/30 transition-all;
}

.upload-zone.has-images {
  @apply py-6;
}

.image-grid {
  @apply grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3;
}

.image-item {
  @apply text-center;
}

.image-thumbnail {
  @apply relative aspect-square rounded-lg overflow-hidden border border-gray-200;
}

.image-thumbnail img {
  @apply w-full h-full object-cover;
}

.status-dot {
  @apply absolute top-1 left-1 w-2.5 h-2.5 rounded-full;
}

.remove-btn {
  @apply absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full 
         hover:bg-red-600 transition-colors;
}

.progress-overlay {
  @apply absolute inset-0 bg-black/50 flex items-center justify-center;
}

.completed-overlay {
  @apply absolute inset-0 bg-green-500/70 flex items-center justify-center 
         text-white text-2xl font-bold;
}

.image-name {
  @apply text-xs text-gray-500 mt-1 truncate;
}

.add-more-btn {
  @apply aspect-square rounded-lg border-2 border-dashed border-gray-300 
         flex items-center justify-center cursor-pointer hover:border-primary-400 
         hover:bg-primary-50/30 transition-all;
}
</style>
