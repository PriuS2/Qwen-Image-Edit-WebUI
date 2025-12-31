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
    case 'completed': return 'status-completed'
    case 'processing': return 'status-processing'
    case 'failed': return 'status-failed'
    default: return 'status-pending'
  }
}
</script>

<template>
  <div class="batch-view">
    <h2 class="page-title">배치 처리</h2>

    <!-- Upload Area -->
    <div 
      class="card upload-card"
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
        <UploadFilled class="upload-icon" />
        <p class="upload-text">이미지를 드래그하거나 클릭하여 업로드</p>
        <p class="upload-hint">여러 이미지를 한 번에 선택할 수 있습니다</p>
      </div>
    </div>

    <!-- Image Grid -->
    <div v-if="batchStore.hasImages" class="card images-card">
      <div class="images-header">
        <h3 class="card-title">
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
            <div class="status-dot" :class="getStatusClass(image.status)"></div>

            <!-- Remove button -->
            <button
              v-if="!batchStore.isProcessing"
              class="remove-btn"
              @click="batchStore.removeImage(image.id)"
            >
              <Close class="remove-icon" />
            </button>

            <!-- Progress overlay -->
            <div v-if="image.status === 'processing'" class="progress-overlay">
              <span class="progress-text">{{ image.progress }}%</span>
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
          <span class="add-icon">+</span>
        </div>
      </div>
    </div>

    <!-- Common Prompt -->
    <div class="card settings-card">
      <h3 class="card-title">공통 설정</h3>
      
      <div class="settings-content">
        <PromptInput
          :model-value="batchStore.commonParams.prompt"
          @update:model-value="batchStore.updateParams({ prompt: $event })"
          label="공통 프롬프트"
          placeholder="모든 이미지에 적용할 프롬프트를 입력하세요..."
          :disabled="batchStore.isProcessing"
        />

        <div class="params-grid">
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
    <div class="card action-card">
      <div class="action-buttons">
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
      <h3 class="card-title">전체 진행 상황</h3>
      <ProgressBar
        :progress="batchStore.totalProgress"
        :status="batchStore.currentJob?.status"
        show-text
      />
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.batch-view {
  max-width: 72rem;
  margin: 0 auto;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.card {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  border: 1px solid #f3f4f6;
  padding: 1rem;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 0.75rem;
}

.upload-card {
  margin-bottom: 1.5rem;
}

.upload-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-zone:hover {
  border-color: #38bdf8;
  background-color: rgba(240, 249, 255, 0.3);
}

.upload-zone.has-images {
  padding: 1.5rem;
}

.upload-icon {
  width: 2.5rem;
  height: 2.5rem;
  color: #9ca3af;
  margin-bottom: 0.5rem;
}

.upload-text {
  color: #4b5563;
}

.upload-hint {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.hidden {
  display: none;
}

.images-card {
  margin-bottom: 1.5rem;
}

.images-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .image-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 768px) {
  .image-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

.image-item {
  text-align: center;
}

.image-thumbnail {
  position: relative;
  aspect-ratio: 1;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.image-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-dot {
  position: absolute;
  top: 0.25rem;
  left: 0.25rem;
  width: 0.625rem;
  height: 0.625rem;
  border-radius: 9999px;
}

.status-pending {
  background-color: #9ca3af;
}

.status-processing {
  background-color: #3b82f6;
}

.status-completed {
  background-color: #22c55e;
}

.status-failed {
  background-color: #ef4444;
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
}

.remove-btn:hover {
  background-color: #dc2626;
}

.remove-icon {
  width: 0.75rem;
  height: 0.75rem;
}

.progress-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-text {
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
}

.completed-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(34, 197, 94, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
}

.image-name {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.add-more-btn {
  aspect-ratio: 1;
  border-radius: 0.5rem;
  border: 2px dashed #d1d5db;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.add-more-btn:hover {
  border-color: #38bdf8;
  background-color: rgba(240, 249, 255, 0.3);
}

.add-icon {
  font-size: 1.875rem;
  color: #9ca3af;
}

.settings-card {
  margin-bottom: 1.5rem;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.params-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .params-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.action-card {
  margin-bottom: 1.5rem;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}
</style>
