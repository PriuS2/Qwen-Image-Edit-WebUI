<script setup lang="ts">
import { computed } from 'vue'
import { useEditStore, type ImageItem } from '@/stores/edit'
import { useHistoryStore } from '@/stores/history'
import ImageUploader from '@/components/common/ImageUploader.vue'
import ImagePreview from '@/components/common/ImagePreview.vue'
import ProgressBar from '@/components/common/ProgressBar.vue'
import EditForm from '@/components/editor/EditForm.vue'
import { 
  VideoPlay, 
  Back, 
  Right,
  Download,
  Delete
} from '@element-plus/icons-vue'

const editStore = useEditStore()
const historyStore = useHistoryStore()

// Computed
const canSubmit = computed(() => 
  editStore.hasImage && 
  editStore.params.prompt.trim() && 
  !editStore.isProcessing
)

const showProgress = computed(() => 
  editStore.isProcessing || 
  (editStore.jobStatus && editStore.jobStatus.status !== 'completed')
)

// Edit mode text
const editModeText = computed(() => 
  editStore.isMultiMode ? 'Multi 모드 (이미지 합성)' : 'Single 모드 (이미지 편집)'
)

// Handlers
const handleImageChange = (file: File | null) => {
  if (file) {
    editStore.setImage(file)
  } else {
    editStore.clearImage()
  }
}

const handleAddImages = (files: File[]) => {
  editStore.addImages(files)
}

const handleRemoveImage = (id: string) => {
  editStore.removeImage(id)
}

const handleSubmit = async () => {
  await editStore.submitEdit()
}

const handleUndo = async () => {
  if (historyStore.currentItem) {
    await historyStore.undo(historyStore.currentItem.id)
  }
}

const handleRedo = async () => {
  if (historyStore.currentItem) {
    await historyStore.redo(historyStore.currentItem.id)
  }
}

const handleDownload = () => {
  if (editStore.resultImage) {
    const link = document.createElement('a')
    link.href = editStore.resultImage
    link.download = `edited-${Date.now()}.png`
    link.click()
  }
}

const handleClear = () => {
  editStore.reset()
}
</script>

<template>
  <div class="edit-view">
    <div class="page-header">
      <h2 class="page-title">이미지 편집</h2>
      <span v-if="editStore.hasImage" class="mode-indicator" :class="editStore.isMultiMode ? 'multi' : 'single'">
        {{ editModeText }}
      </span>
    </div>

    <!-- Image Preview Area -->
    <div class="image-grid">
      <!-- Original Images (Multi-image uploader) -->
      <div class="card">
        <h3 class="card-title">입력 이미지 (최대 3장)</h3>
        <ImageUploader
          :multiple="true"
          :images="editStore.images"
          :max-images="editStore.maxImages"
          :disabled="editStore.isProcessing"
          @add="handleAddImages"
          @remove="handleRemoveImage"
        />
      </div>

      <!-- Result Image -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">결과 이미지</h3>
          <div v-if="editStore.resultImage" class="card-actions">
            <el-button
              size="small"
              :icon="Download"
              @click="handleDownload"
              title="다운로드"
            />
            <el-button
              size="small"
              :icon="Delete"
              @click="handleClear"
              title="초기화"
            />
          </div>
        </div>
        <ImagePreview
          :src="editStore.resultImage"
          :loading="editStore.isProcessing"
          placeholder="편집 결과가 여기에 표시됩니다"
        />
      </div>
    </div>

    <!-- Edit Form -->
    <div class="card form-card">
      <EditForm
        :params="editStore.params"
        :disabled="editStore.isProcessing"
        @update:params="editStore.updateParams($event)"
      />
    </div>

    <!-- Action Buttons -->
    <div class="card action-card">
      <div class="action-buttons">
        <el-button
          :icon="Back"
          :disabled="!historyStore.canUndo || editStore.isProcessing"
          @click="handleUndo"
        >
          Undo
        </el-button>

        <el-button
          type="primary"
          size="large"
          :icon="VideoPlay"
          :disabled="!canSubmit"
          :loading="editStore.isProcessing"
          @click="handleSubmit"
        >
          {{ editStore.isProcessing ? '처리 중...' : '편집 시작' }}
        </el-button>

        <el-button
          :icon="Right"
          :disabled="!historyStore.canRedo || editStore.isProcessing"
          @click="handleRedo"
        >
          Redo
        </el-button>
      </div>
    </div>

    <!-- Progress Bar -->
    <div v-if="showProgress" class="card">
      <h3 class="card-title">진행 상황</h3>
      <ProgressBar
        :progress="editStore.progress"
        :status="editStore.jobStatus?.status"
        show-text
      />
      <p v-if="editStore.error" class="error-text">
        {{ editStore.error }}
      </p>
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.edit-view {
  max-width: 72rem;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.mode-indicator {
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
}

.mode-indicator.single {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.mode-indicator.multi {
  background-color: #fce7f3;
  color: #be185d;
}

.image-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 1024px) {
  .image-grid {
    grid-template-columns: repeat(2, 1fr);
  }
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.form-card {
  margin-bottom: 1.5rem;
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

.error-text {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}
</style>
