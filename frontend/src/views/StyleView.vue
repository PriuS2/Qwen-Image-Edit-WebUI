<script setup lang="ts">
import { ref, computed } from 'vue'
import { useEditStore } from '@/stores/edit'
import type { StyleType } from '@/types'
import ImageUploader from '@/components/common/ImageUploader.vue'
import ImagePreview from '@/components/common/ImagePreview.vue'
import ProgressBar from '@/components/common/ProgressBar.vue'
import StyleSelector from '@/components/editor/StyleSelector.vue'
import ParameterSlider from '@/components/editor/ParameterSlider.vue'
import { 
  MagicStick,
  Download,
  Delete
} from '@element-plus/icons-vue'

const editStore = useEditStore()

// Local state
const selectedStyle = ref<StyleType | null>(null)
const intensity = ref(1.0)
const additionalPrompt = ref('')

// Computed
const canSubmit = computed(() => 
  editStore.hasImage && 
  selectedStyle.value && 
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
  if (!selectedStyle.value) return
  
  await editStore.submitStyleTransfer(
    selectedStyle.value,
    intensity.value,
    additionalPrompt.value || undefined
  )
}

const handleDownload = () => {
  if (editStore.resultImage) {
    const link = document.createElement('a')
    link.href = editStore.resultImage
    link.download = `styled-${selectedStyle.value}-${Date.now()}.png`
    link.click()
  }
}

const handleClear = () => {
  editStore.reset()
  selectedStyle.value = null
  intensity.value = 1.0
  additionalPrompt.value = ''
}
</script>

<template>
  <div class="style-view">
    <h2 class="page-title">스타일 변환</h2>

    <!-- Image Preview Area -->
    <div class="image-grid">
      <!-- Original Image -->
      <div class="card">
        <h3 class="card-title">원본 이미지</h3>
        <ImageUploader
          :preview-url="editStore.currentImageUrl"
          :disabled="editStore.isProcessing"
          @change="handleImageChange"
        />
      </div>

      <!-- Result Image -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">변환 결과</h3>
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
          placeholder="스타일 변환 결과가 여기에 표시됩니다"
        />
      </div>
    </div>

    <!-- Style Selection -->
    <div class="card style-card">
      <StyleSelector
        v-model="selectedStyle"
        :disabled="editStore.isProcessing"
      />
    </div>

    <!-- Style Options -->
    <div class="card options-card">
      <div class="options-grid">
        <!-- Intensity -->
        <ParameterSlider
          v-model="intensity"
          label="스타일 강도"
          :min="0.1"
          :max="2.0"
          :step="0.1"
          :disabled="editStore.isProcessing"
        />

        <!-- Additional Prompt -->
        <div class="additional-prompt">
          <label class="prompt-label">추가 프롬프트 (선택)</label>
          <el-input
            v-model="additionalPrompt"
            placeholder="추가 효과를 입력하세요... (예: add cherry blossoms)"
            :disabled="editStore.isProcessing"
          />
        </div>
      </div>
    </div>

    <!-- Action Button -->
    <div class="card action-card">
      <div class="action-center">
        <el-button
          type="primary"
          size="large"
          :icon="MagicStick"
          :disabled="!canSubmit"
          :loading="editStore.isProcessing"
          @click="handleSubmit"
        >
          {{ editStore.isProcessing ? '변환 중...' : '스타일 변환 시작' }}
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

.style-view {
  max-width: 72rem;
  margin: 0 auto;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1.5rem;
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

.style-card {
  margin-bottom: 1.5rem;
}

.options-card {
  margin-bottom: 1.5rem;
}

.options-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .options-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.additional-prompt {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.prompt-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.action-card {
  margin-bottom: 1.5rem;
}

.action-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-text {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}
</style>
