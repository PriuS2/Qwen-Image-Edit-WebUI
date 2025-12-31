<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useModelStore } from '@/stores/model'
import { useSettingsStore } from '@/stores/settings'
import ParameterSlider from '@/components/editor/ParameterSlider.vue'
import ProgressBar from '@/components/common/ProgressBar.vue'
import { 
  VideoPlay, 
  Switch, 
  Download, 
  Refresh,
  Check
} from '@element-plus/icons-vue'

const modelStore = useModelStore()
const settingsStore = useSettingsStore()

// Local download tracking
const downloadPollingInterval = ref<number | null>(null)

onMounted(async () => {
  await Promise.all([
    modelStore.fetchStatus(),
    modelStore.fetchAvailableModels(),
    settingsStore.fetchSettings()
  ])
})

// Computed
const modelStatusText = computed(() => {
  if (modelStore.isLoading) return '로딩 중...'
  if (modelStore.isLoaded) return '로드됨'
  return '미로드'
})

const vramText = computed(() => {
  if (!modelStore.isLoaded) return '-'
  return `${modelStore.vramUsed.toFixed(1)} / ${modelStore.vramTotal.toFixed(1)} GB`
})

const isDownloading = computed(() => 
  modelStore.downloadStatus?.status === 'downloading'
)

// Model actions
const handleLoadModel = async () => {
  await modelStore.loadModel()
}

const handleUnloadModel = async () => {
  await modelStore.unloadModel()
}

const handleDownloadModel = async () => {
  await modelStore.startDownload()
  startDownloadPolling()
}

const startDownloadPolling = () => {
  if (downloadPollingInterval.value) return
  
  downloadPollingInterval.value = window.setInterval(async () => {
    await modelStore.fetchDownloadStatus()
    
    if (!isDownloading.value) {
      stopDownloadPolling()
    }
  }, 1000)
}

const stopDownloadPolling = () => {
  if (downloadPollingInterval.value) {
    clearInterval(downloadPollingInterval.value)
    downloadPollingInterval.value = null
  }
}

const handleCancelDownload = async () => {
  await modelStore.cancelDownload()
  stopDownloadPolling()
}

// Settings actions
const handleSaveSettings = async () => {
  await settingsStore.saveSettings()
}

const handleResetSettings = async () => {
  await settingsStore.resetSettings()
}

// Optimization toggles
const updateOptimization = (key: string, value: boolean) => {
  settingsStore.updateOptimization({ [key]: value })
}
</script>

<template>
  <div class="settings-view">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">설정</h2>

    <!-- Model Management -->
    <div class="card mb-6">
      <h3 class="section-title">모델 관리</h3>
      <div class="section-divider"></div>

      <div class="space-y-4">
        <!-- Model Status -->
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">현재 모델</p>
            <p class="font-medium">{{ modelStore.currentModel || '없음' }}</p>
          </div>
          <div class="text-right">
            <p class="text-sm text-gray-600">상태</p>
            <div class="flex items-center gap-2">
              <span 
                class="w-2.5 h-2.5 rounded-full"
                :class="modelStore.isLoaded ? 'bg-green-500' : 'bg-gray-400'"
              ></span>
              <span class="font-medium">{{ modelStatusText }}</span>
            </div>
          </div>
        </div>

        <!-- VRAM Usage -->
        <div v-if="modelStore.isLoaded" class="flex items-center justify-between">
          <span class="text-sm text-gray-600">VRAM 사용량</span>
          <span class="font-medium">{{ vramText }}</span>
        </div>

        <!-- Model Actions -->
        <div class="flex flex-wrap gap-2">
          <el-button
            v-if="!modelStore.isLoaded"
            type="primary"
            :icon="VideoPlay"
            :loading="modelStore.isLoading"
            @click="handleLoadModel"
          >
            모델 로드
          </el-button>
          <el-button
            v-else
            :icon="Switch"
            :loading="modelStore.isLoading"
            @click="handleUnloadModel"
          >
            모델 언로드
          </el-button>
          <el-button
            v-if="!isDownloading"
            :icon="Download"
            @click="handleDownloadModel"
          >
            모델 다운로드
          </el-button>
          <el-button
            v-else
            type="danger"
            @click="handleCancelDownload"
          >
            다운로드 취소
          </el-button>
        </div>

        <!-- Download Progress -->
        <div v-if="isDownloading && modelStore.downloadStatus" class="space-y-2">
          <p class="text-sm text-gray-600">
            다운로드 중: {{ modelStore.downloadStatus.current_file || '...' }}
          </p>
          <ProgressBar
            :progress="modelStore.downloadStatus.progress_percent"
            show-text
          />
          <p class="text-xs text-gray-500">
            {{ modelStore.downloadStatus.files_completed }} / {{ modelStore.downloadStatus.files_total }} 파일
          </p>
        </div>
      </div>
    </div>

    <!-- Optimization Settings -->
    <div class="card mb-6">
      <h3 class="section-title">최적화 설정</h3>
      <div class="section-divider"></div>

      <div class="space-y-3">
        <el-checkbox
          :model-value="settingsStore.optimization.enable_model_cpu_offload"
          @update:model-value="updateOptimization('enable_model_cpu_offload', $event)"
        >
          CPU 오프로딩 활성화
          <span class="text-gray-400 text-xs ml-2">VRAM 사용량 감소</span>
        </el-checkbox>

        <el-checkbox
          :model-value="settingsStore.optimization.enable_attention_slicing"
          @update:model-value="updateOptimization('enable_attention_slicing', $event)"
        >
          Attention 슬라이싱
          <span class="text-gray-400 text-xs ml-2">메모리 효율 개선</span>
        </el-checkbox>

        <el-checkbox
          :model-value="settingsStore.optimization.enable_vae_slicing"
          @update:model-value="updateOptimization('enable_vae_slicing', $event)"
        >
          VAE 슬라이싱
          <span class="text-gray-400 text-xs ml-2">VAE 메모리 최적화</span>
        </el-checkbox>

        <el-checkbox
          :model-value="settingsStore.optimization.enable_vae_tiling"
          @update:model-value="updateOptimization('enable_vae_tiling', $event)"
        >
          VAE 타일링
          <span class="text-gray-400 text-xs ml-2">대용량 이미지 지원</span>
        </el-checkbox>

        <el-checkbox
          :model-value="settingsStore.optimization.enable_xformers"
          @update:model-value="updateOptimization('enable_xformers', $event)"
        >
          xFormers 활성화
          <span class="text-gray-400 text-xs ml-2">추가 속도 향상</span>
        </el-checkbox>
      </div>
    </div>

    <!-- Automation Settings -->
    <div class="card mb-6">
      <h3 class="section-title">자동화 설정</h3>
      <div class="section-divider"></div>

      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium">자동 로드</p>
            <p class="text-sm text-gray-500">요청 시 자동으로 모델 로드</p>
          </div>
          <el-switch
            :model-value="settingsStore.autoLoad.enabled"
            @update:model-value="settingsStore.updateAutoLoad($event)"
          />
        </div>

        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium">자동 언로드</p>
            <p class="text-sm text-gray-500">유휴 시 자동으로 모델 언로드</p>
          </div>
          <el-switch
            :model-value="settingsStore.autoUnload.enabled"
            @update:model-value="settingsStore.updateAutoUnload($event)"
          />
        </div>

        <div v-if="settingsStore.autoUnload.enabled">
          <ParameterSlider
            :model-value="settingsStore.autoUnload.timeout_minutes"
            @update:model-value="settingsStore.updateAutoUnload(true, $event)"
            label="자동 언로드 타임아웃 (분)"
            :min="5"
            :max="120"
            :step="5"
          />
        </div>
      </div>
    </div>

    <!-- Edit Defaults -->
    <div class="card mb-6">
      <h3 class="section-title">편집 기본값</h3>
      <div class="section-divider"></div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ParameterSlider
          :model-value="settingsStore.editDefaults.num_inference_steps"
          @update:model-value="settingsStore.updateEditDefaults({ num_inference_steps: $event })"
          label="추론 스텝"
          :min="1"
          :max="100"
        />
        <ParameterSlider
          :model-value="settingsStore.editDefaults.true_cfg_scale"
          @update:model-value="settingsStore.updateEditDefaults({ true_cfg_scale: $event })"
          label="True CFG 스케일"
          :min="1"
          :max="20"
          :step="0.1"
        />
        <ParameterSlider
          :model-value="settingsStore.editDefaults.guidance_scale"
          @update:model-value="settingsStore.updateEditDefaults({ guidance_scale: $event })"
          label="가이던스 스케일"
          :min="0"
          :max="20"
          :step="0.1"
        />
      </div>
    </div>

    <!-- Gallery Settings -->
    <div class="card mb-6">
      <h3 class="section-title">갤러리 설정</h3>
      <div class="section-divider"></div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ParameterSlider
          :model-value="settingsStore.gallerySettings.max_history_per_session"
          @update:model-value="settingsStore.updateGallerySettings({ max_history_per_session: $event })"
          label="세션당 최대 히스토리"
          :min="1"
          :max="50"
        />
        <ParameterSlider
          :model-value="settingsStore.gallerySettings.auto_cleanup_days"
          @update:model-value="settingsStore.updateGallerySettings({ auto_cleanup_days: $event })"
          label="자동 정리 (일)"
          :min="1"
          :max="30"
        />
        <ParameterSlider
          :model-value="settingsStore.gallerySettings.thumbnail_size"
          @update:model-value="settingsStore.updateGallerySettings({ thumbnail_size: $event })"
          label="썸네일 크기"
          :min="64"
          :max="512"
          :step="32"
        />
      </div>
    </div>

    <!-- Save Actions -->
    <div class="card">
      <div class="flex justify-center gap-4">
        <el-button
          type="primary"
          size="large"
          :icon="Check"
          :loading="settingsStore.isLoading"
          :disabled="!settingsStore.isDirty"
          @click="handleSaveSettings"
        >
          설정 저장
        </el-button>
        <el-button
          size="large"
          :icon="Refresh"
          :loading="settingsStore.isLoading"
          @click="handleResetSettings"
        >
          초기화
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-view {
  @apply max-w-4xl mx-auto;
}

.section-title {
  @apply text-lg font-medium text-gray-800 mb-2;
}

.section-divider {
  @apply border-b border-gray-200 mb-4;
}
</style>
