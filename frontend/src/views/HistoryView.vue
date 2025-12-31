<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useHistoryStore } from '@/stores/history'
import { useEditStore } from '@/stores/edit'
import { Back, Right, Delete, Refresh, ArrowRight } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const historyStore = useHistoryStore()
const editStore = useEditStore()

const selectedItemId = ref<string | null>(null)

onMounted(() => {
  historyStore.setSessionId(editStore.sessionId)
})

// Computed
const selectedItem = computed(() => 
  historyStore.items.find(item => item.id === selectedItemId.value)
)

// Handlers
const selectItem = async (itemId: string) => {
  selectedItemId.value = itemId
  await historyStore.fetchItem(itemId)
}

const handleUndo = async () => {
  if (selectedItemId.value) {
    await historyStore.undo(selectedItemId.value)
  }
}

const handleRedo = async () => {
  if (selectedItemId.value) {
    await historyStore.redo(selectedItemId.value)
  }
}

const handleDelete = async (itemId: string) => {
  try {
    await ElMessageBox.confirm(
      '이 히스토리 항목을 삭제하시겠습니까?',
      '삭제 확인',
      {
        confirmButtonText: '삭제',
        cancelButtonText: '취소',
        type: 'warning'
      }
    )
    
    await historyStore.deleteItem(itemId)
    if (selectedItemId.value === itemId) {
      selectedItemId.value = null
    }
  } catch {
    // Cancelled
  }
}

const handleRefresh = () => {
  historyStore.fetchItems(true)
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('ko-KR')
}

const getImageUrl = (path: string) => {
  if (path.startsWith('/')) return path
  return `/storage/${path}`
}
</script>

<template>
  <div class="history-view">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">히스토리</h2>
      <div class="flex gap-2">
        <el-select 
          :model-value="historyStore.sessionId" 
          placeholder="세션 선택"
          @change="historyStore.setSessionId"
          clearable
          style="width: 200px"
        >
          <el-option 
            v-for="item in historyStore.items" 
            :key="item.session_id"
            :label="item.session_id"
            :value="item.session_id"
          />
        </el-select>
        <el-button :icon="Refresh" @click="handleRefresh" :loading="historyStore.isLoading">
          새로고침
        </el-button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!historyStore.hasItems && !historyStore.isLoading" class="empty-state card">
      <div class="text-center py-16">
        <div class="text-6xl mb-4">📜</div>
        <h3 class="text-xl font-medium text-gray-700 mb-2">히스토리가 없습니다</h3>
        <p class="text-gray-500">이미지를 편집하면 여기에 기록됩니다.</p>
      </div>
    </div>

    <template v-else>
      <!-- Timeline -->
      <div class="card mb-6">
        <h3 class="text-sm font-medium text-gray-600 mb-4">타임라인</h3>
        <div class="timeline-container">
          <div class="timeline-scroll">
            <div 
              v-for="(item, index) in historyStore.items" 
              :key="item.id"
              class="timeline-item"
              :class="{ 'is-selected': selectedItemId === item.id }"
              @click="selectItem(item.id)"
            >
              <div class="timeline-thumbnail">
                <img 
                  :src="getImageUrl(item.edited_image_path)" 
                  :alt="`편집 ${index + 1}`"
                  class="thumbnail-image"
                />
              </div>
              <div class="timeline-info">
                <span class="timeline-label">{{ index === 0 ? '원본' : `편집 ${index}` }}</span>
              </div>
              <ArrowRight 
                v-if="index < historyStore.items.length - 1" 
                class="timeline-arrow"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Selected Item Details -->
      <div v-if="selectedItem" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Image Preview -->
        <div class="card">
          <h3 class="text-sm font-medium text-gray-600 mb-3">이미지</h3>
          <div class="image-preview">
            <img 
              :src="getImageUrl(selectedItem.edited_image_path)" 
              :alt="selectedItem.prompt"
              class="preview-image"
            />
          </div>
        </div>

        <!-- Details -->
        <div class="card">
          <h3 class="text-sm font-medium text-gray-600 mb-3">편집 정보</h3>
          
          <div class="details-list">
            <div class="detail-item">
              <span class="detail-label">위치:</span>
              <span class="detail-value">{{ selectedItem.position + 1 }} / {{ historyStore.items.length }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">프롬프트:</span>
              <span class="detail-value">{{ selectedItem.prompt || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">추론 스텝:</span>
              <span class="detail-value">{{ selectedItem.parameters?.num_inference_steps ?? '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">True CFG:</span>
              <span class="detail-value">{{ selectedItem.parameters?.true_cfg_scale ?? '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">시드:</span>
              <span class="detail-value">{{ selectedItem.parameters?.seed ?? '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">시간:</span>
              <span class="detail-value">{{ formatDate(selectedItem.created_at) }}</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-center gap-3 mt-6">
            <el-button
              :icon="Back"
              :disabled="!historyStore.canUndo || historyStore.isLoading"
              @click="handleUndo"
            >
              Undo
            </el-button>
            <el-button
              :icon="Right"
              :disabled="!historyStore.canRedo || historyStore.isLoading"
              @click="handleRedo"
            >
              Redo
            </el-button>
            <el-button
              type="danger"
              :icon="Delete"
              @click="handleDelete(selectedItem.id)"
            >
              삭제
            </el-button>
          </div>
        </div>
      </div>

      <!-- No Selection -->
      <div v-else class="card">
        <div class="text-center py-8 text-gray-500">
          타임라인에서 항목을 선택하세요
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.history-view {
  @apply max-w-6xl mx-auto;
}

.timeline-container {
  @apply overflow-x-auto pb-4;
}

.timeline-scroll {
  @apply flex items-center gap-2 min-w-max;
}

.timeline-item {
  @apply flex items-center gap-2 cursor-pointer;
}

.timeline-thumbnail {
  @apply w-20 h-20 rounded-lg overflow-hidden border-2 border-transparent 
         hover:border-primary-300 transition-all;
}

.timeline-item.is-selected .timeline-thumbnail {
  @apply border-primary-500 ring-2 ring-primary-200;
}

.thumbnail-image {
  @apply w-full h-full object-cover;
}

.timeline-info {
  @apply text-center;
}

.timeline-label {
  @apply text-xs text-gray-500;
}

.timeline-arrow {
  @apply w-4 h-4 text-gray-400;
}

.image-preview {
  @apply aspect-square bg-gray-100 rounded-lg overflow-hidden;
}

.preview-image {
  @apply w-full h-full object-contain;
}

.details-list {
  @apply space-y-3;
}

.detail-item {
  @apply flex;
}

.detail-label {
  @apply text-sm text-gray-500 w-24 flex-shrink-0;
}

.detail-value {
  @apply text-sm text-gray-800;
}
</style>
