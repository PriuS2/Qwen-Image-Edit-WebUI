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
    <h2 class="text-2xl font-bold text-gray-800 mb-6">스타일 변환</h2>

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
          <h3 class="text-sm font-medium text-gray-600">변환 결과</h3>
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
          placeholder="스타일 변환 결과가 여기에 표시됩니다"
        />
      </div>
    </div>

    <!-- Style Selection -->
    <div class="card mb-6">
      <StyleSelector
        v-model="selectedStyle"
        :disabled="editStore.isProcessing"
      />
    </div>

    <!-- Style Options -->
    <div class="card mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700">추가 프롬프트 (선택)</label>
          <el-input
            v-model="additionalPrompt"
            placeholder="추가 효과를 입력하세요... (예: add cherry blossoms)"
            :disabled="editStore.isProcessing"
          />
        </div>
      </div>
    </div>

    <!-- Action Button -->
    <div class="card mb-6">
      <div class="flex items-center justify-center">
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
.style-view {
  @apply max-w-6xl mx-auto;
}
</style>
