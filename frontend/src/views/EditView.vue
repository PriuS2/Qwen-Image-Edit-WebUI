<script setup lang="ts">
import { computed } from 'vue'
import { useEditStore } from '@/stores/edit'
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

// Handlers
const handleImageChange = (file: File | null) => {
  if (file) {
    editStore.setImage(file)
  } else {
    editStore.clearImage()
  }
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
    <h2 class="text-2xl font-bold text-gray-800 mb-6">이미지 편집</h2>

    <!-- Image Preview Area -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Original Image -->
      <div class="card">
        <h3 class="text-sm font-medium text-gray-600 mb-3">원본 이미지</h3>
        <ImageUploader
          :preview-url="editStore.currentImageUrl"
          :disabled="editStore.isProcessing"
          @change="handleImageChange"
        />
      </div>

      <!-- Result Image -->
      <div class="card">
        <div class="flex justify-between items-center mb-3">
          <h3 class="text-sm font-medium text-gray-600">결과 이미지</h3>
          <div v-if="editStore.resultImage" class="flex gap-2">
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
    <div class="card mb-6">
      <EditForm
        :params="editStore.params"
        :disabled="editStore.isProcessing"
        @update:params="editStore.updateParams($event)"
      />
    </div>

    <!-- Action Buttons -->
    <div class="card mb-6">
      <div class="flex items-center justify-center gap-4">
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
      <h3 class="text-sm font-medium text-gray-600 mb-3">진행 상황</h3>
      <ProgressBar
        :progress="editStore.progress"
        :status="editStore.jobStatus?.status"
        show-text
      />
      <p v-if="editStore.error" class="text-red-500 text-sm mt-2">
        {{ editStore.error }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.edit-view {
  @apply max-w-6xl mx-auto;
}
</style>
