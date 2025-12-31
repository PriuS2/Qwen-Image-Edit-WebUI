<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useEditStore } from '@/stores/edit'
import { stylesApi } from '@/api'
import type { StylePreset, StylePresetCreate, StylePresetUpdate } from '@/types'
import ImageUploader from '@/components/common/ImageUploader.vue'
import ImagePreview from '@/components/common/ImagePreview.vue'
import ProgressBar from '@/components/common/ProgressBar.vue'
import StyleSelector from '@/components/editor/StyleSelector.vue'
import ParameterSlider from '@/components/editor/ParameterSlider.vue'
import { 
  MagicStick,
  Download,
  Delete,
  Setting,
  Plus,
  Edit,
  Refresh
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const editStore = useEditStore()

// Local state
const selectedStyle = ref<string | null>(null)
const intensity = ref(1.0)
const additionalPrompt = ref('')

// Style management state
const showStyleManager = ref(false)
const styleList = ref<StylePreset[]>([])
const isLoadingStyles = ref(false)
const editingStyle = ref<StylePreset | null>(null)
const showEditDialog = ref(false)
const isNewStyle = ref(false)

// Style editor form
const styleForm = ref<{
  name: string
  label: string
  description: string
  icon: string
  prompt: string
  negative_prompt: string
  is_enabled: boolean
  sort_order: number
}>({
  name: '',
  label: '',
  description: '',
  icon: '🎨',
  prompt: '',
  negative_prompt: '',
  is_enabled: true,
  sort_order: 0
})

// StyleSelector ref
const styleSelectorRef = ref<InstanceType<typeof StyleSelector> | null>(null)

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

// Style Management Functions
const loadStyles = async () => {
  isLoadingStyles.value = true
  try {
    const response = await stylesApi.getAll(false) // 모든 스타일 (비활성화 포함)
    if (response.success && response.data) {
      styleList.value = response.data
    }
  } catch (err) {
    console.error('Failed to load styles:', err)
    ElMessage.error('스타일 목록 로드 실패')
  } finally {
    isLoadingStyles.value = false
  }
}

const openAddDialog = () => {
  isNewStyle.value = true
  editingStyle.value = null
  styleForm.value = {
    name: '',
    label: '',
    description: '',
    icon: '🎨',
    prompt: '',
    negative_prompt: '',
    is_enabled: true,
    sort_order: styleList.value.length
  }
  showEditDialog.value = true
}

const openEditDialog = (style: StylePreset) => {
  isNewStyle.value = false
  editingStyle.value = style
  styleForm.value = {
    name: style.name,
    label: style.label,
    description: style.description || '',
    icon: style.icon,
    prompt: style.prompt,
    negative_prompt: style.negative_prompt || '',
    is_enabled: style.is_enabled,
    sort_order: style.sort_order
  }
  showEditDialog.value = true
}

const saveStyle = async () => {
  if (!styleForm.value.name || !styleForm.value.label || !styleForm.value.prompt) {
    ElMessage.warning('이름, 표시 이름, 프롬프트는 필수입니다.')
    return
  }

  try {
    if (isNewStyle.value) {
      // 새 스타일 생성
      const createData: StylePresetCreate = {
        name: styleForm.value.name,
        label: styleForm.value.label,
        description: styleForm.value.description || undefined,
        icon: styleForm.value.icon,
        prompt: styleForm.value.prompt,
        negative_prompt: styleForm.value.negative_prompt,
        is_enabled: styleForm.value.is_enabled,
        sort_order: styleForm.value.sort_order
      }
      await stylesApi.create(createData)
      ElMessage.success('스타일이 추가되었습니다.')
    } else if (editingStyle.value) {
      // 기존 스타일 수정
      const updateData: StylePresetUpdate = {
        label: styleForm.value.label,
        description: styleForm.value.description,
        icon: styleForm.value.icon,
        prompt: styleForm.value.prompt,
        negative_prompt: styleForm.value.negative_prompt,
        is_enabled: styleForm.value.is_enabled,
        sort_order: styleForm.value.sort_order
      }
      // 기본 스타일이 아닌 경우만 이름 변경 가능
      if (!editingStyle.value.is_builtin) {
        updateData.name = styleForm.value.name
      }
      await stylesApi.update(editingStyle.value.id, updateData)
      ElMessage.success('스타일이 수정되었습니다.')
    }
    
    showEditDialog.value = false
    await loadStyles()
    
    // StyleSelector 새로고침
    styleSelectorRef.value?.refresh()
  } catch (err: any) {
    console.error('Failed to save style:', err)
    ElMessage.error(err.response?.data?.detail || '스타일 저장 실패')
  }
}

const deleteStyle = async (style: StylePreset) => {
  if (style.is_builtin) {
    ElMessage.warning('기본 스타일은 삭제할 수 없습니다. 비활성화만 가능합니다.')
    return
  }

  try {
    await ElMessageBox.confirm(
      `'${style.label}' 스타일을 삭제하시겠습니까?`,
      '스타일 삭제',
      {
        confirmButtonText: '삭제',
        cancelButtonText: '취소',
        type: 'warning'
      }
    )
    
    await stylesApi.delete(style.id)
    ElMessage.success('스타일이 삭제되었습니다.')
    await loadStyles()
    
    // StyleSelector 새로고침
    styleSelectorRef.value?.refresh()
  } catch (err: any) {
    if (err !== 'cancel') {
      console.error('Failed to delete style:', err)
      ElMessage.error('스타일 삭제 실패')
    }
  }
}

const toggleStyleEnabled = async (style: StylePreset) => {
  try {
    await stylesApi.update(style.id, { is_enabled: !style.is_enabled })
    style.is_enabled = !style.is_enabled
    ElMessage.success(style.is_enabled ? '스타일이 활성화되었습니다.' : '스타일이 비활성화되었습니다.')
    
    // StyleSelector 새로고침
    styleSelectorRef.value?.refresh()
  } catch (err) {
    console.error('Failed to toggle style:', err)
    ElMessage.error('스타일 상태 변경 실패')
  }
}

const resetStyles = async () => {
  try {
    await ElMessageBox.confirm(
      '모든 스타일을 기본값으로 초기화하시겠습니까?\n사용자 정의 스타일은 삭제됩니다.',
      '스타일 초기화',
      {
        confirmButtonText: '초기화',
        cancelButtonText: '취소',
        type: 'warning'
      }
    )
    
    await stylesApi.reset()
    ElMessage.success('스타일이 초기화되었습니다.')
    await loadStyles()
    
    // StyleSelector 새로고침
    styleSelectorRef.value?.refresh()
  } catch (err: any) {
    if (err !== 'cancel') {
      console.error('Failed to reset styles:', err)
      ElMessage.error('스타일 초기화 실패')
    }
  }
}

// 이모지 옵션
const emojiOptions = [
  '🎨', '🏯', '🎌', '📷', '💧', '✏️', '🤖', '📼', 
  '👾', '💥', '🌸', '🌙', '⭐', '🔥', '❄️', '🌈',
  '🎭', '🎪', '🎬', '🖼️', '🎵', '💎', '🦋', '🌺'
]

onMounted(() => {
  loadStyles()
})
</script>

<template>
  <div class="style-view">
    <div class="page-header">
      <h2 class="page-title">스타일 변환</h2>
      <el-button
        type="default"
        :icon="Setting"
        @click="showStyleManager = !showStyleManager"
      >
        {{ showStyleManager ? '스타일 변환' : '스타일 설정' }}
      </el-button>
    </div>

    <!-- Style Manager Panel -->
    <div v-if="showStyleManager" class="style-manager">
      <div class="card">
        <div class="card-header-row">
          <h3 class="card-title">스타일 관리</h3>
          <div class="card-actions">
            <el-button type="primary" :icon="Plus" @click="openAddDialog">
              새 스타일
            </el-button>
            <el-button :icon="Refresh" @click="resetStyles">
              초기화
            </el-button>
          </div>
        </div>
        
        <div v-if="isLoadingStyles" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else class="style-list">
          <div
            v-for="style in styleList"
            :key="style.id"
            class="style-item"
            :class="{ 'is-disabled': !style.is_enabled }"
          >
            <div class="style-item-icon">{{ style.icon }}</div>
            <div class="style-item-content">
              <div class="style-item-header">
                <span class="style-item-label">{{ style.label }}</span>
                <span class="style-item-name">({{ style.name }})</span>
                <el-tag v-if="style.is_builtin" size="small" type="info">기본</el-tag>
                <el-tag v-if="!style.is_enabled" size="small" type="danger">비활성</el-tag>
              </div>
              <div class="style-item-description">{{ style.description }}</div>
              <div class="style-item-prompts">
                <div class="prompt-preview">
                  <strong>Prompt:</strong> {{ style.prompt.substring(0, 100) }}{{ style.prompt.length > 100 ? '...' : '' }}
                </div>
                <div v-if="style.negative_prompt" class="prompt-preview negative">
                  <strong>Negative:</strong> {{ style.negative_prompt.substring(0, 80) }}{{ style.negative_prompt.length > 80 ? '...' : '' }}
                </div>
              </div>
            </div>
            <div class="style-item-actions">
              <el-switch
                :model-value="style.is_enabled"
                size="small"
                @change="toggleStyleEnabled(style)"
              />
              <el-button
                size="small"
                :icon="Edit"
                @click="openEditDialog(style)"
                circle
              />
              <el-button
                v-if="!style.is_builtin"
                size="small"
                type="danger"
                :icon="Delete"
                @click="deleteStyle(style)"
                circle
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Style Transfer UI (기존) -->
    <template v-else>
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
          ref="styleSelectorRef"
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
    </template>

    <!-- Style Edit Dialog -->
    <el-dialog
      v-model="showEditDialog"
      :title="isNewStyle ? '새 스타일 추가' : '스타일 편집'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="styleForm" label-position="top">
        <div class="form-row">
          <el-form-item label="아이콘" style="width: 100px;">
            <el-select v-model="styleForm.icon" placeholder="아이콘">
              <el-option
                v-for="emoji in emojiOptions"
                :key="emoji"
                :label="emoji"
                :value="emoji"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="스타일 ID" style="flex: 1;" required>
            <el-input
              v-model="styleForm.name"
              placeholder="예: my_style (영문, 언더스코어만)"
              :disabled="editingStyle?.is_builtin"
            />
          </el-form-item>
          
          <el-form-item label="표시 이름" style="flex: 1;" required>
            <el-input
              v-model="styleForm.label"
              placeholder="예: 내 스타일"
            />
          </el-form-item>
        </div>
        
        <el-form-item label="설명">
          <el-input
            v-model="styleForm.description"
            placeholder="스타일에 대한 간단한 설명"
          />
        </el-form-item>
        
        <el-form-item label="프롬프트" required>
          <el-input
            v-model="styleForm.prompt"
            type="textarea"
            :rows="4"
            placeholder="스타일 변환에 사용할 프롬프트를 입력하세요..."
          />
          <div class="form-tip">
            이미지에 적용할 스타일을 자세히 설명하세요. 예: "Transform this image into watercolor painting style with soft, flowing colors..."
          </div>
        </el-form-item>
        
        <el-form-item label="네거티브 프롬프트">
          <el-input
            v-model="styleForm.negative_prompt"
            type="textarea"
            :rows="3"
            placeholder="제외할 요소들을 입력하세요..."
          />
          <div class="form-tip">
            결과물에서 제외하고 싶은 요소들을 입력하세요. 예: "blurry, low quality, distorted, ugly..."
          </div>
        </el-form-item>
        
        <div class="form-row">
          <el-form-item label="정렬 순서">
            <el-input-number
              v-model="styleForm.sort_order"
              :min="0"
              :max="100"
            />
          </el-form-item>
          
          <el-form-item label="활성화">
            <el-switch v-model="styleForm.is_enabled" />
          </el-form-item>
        </div>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">취소</el-button>
        <el-button type="primary" @click="saveStyle">
          {{ isNewStyle ? '추가' : '저장' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.style-view {
  max-width: 72rem;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
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

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
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

/* Style Manager Styles */
.style-manager {
  margin-bottom: 1.5rem;
}

.loading-container {
  padding: 1rem;
}

.style-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.style-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.style-item:hover {
  border-color: #d1d5db;
}

.style-item.is-disabled {
  opacity: 0.6;
  background-color: #f3f4f6;
}

.style-item-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.style-item-content {
  flex: 1;
  min-width: 0;
}

.style-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.25rem;
}

.style-item-label {
  font-weight: 600;
  color: #1f2937;
}

.style-item-name {
  font-size: 0.75rem;
  color: #6b7280;
}

.style-item-description {
  font-size: 0.875rem;
  color: #4b5563;
  margin-bottom: 0.5rem;
}

.style-item-prompts {
  font-size: 0.75rem;
  color: #6b7280;
}

.prompt-preview {
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.prompt-preview.negative {
  color: #9ca3af;
}

.style-item-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Form Styles */
.form-row {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.form-tip {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}
</style>
