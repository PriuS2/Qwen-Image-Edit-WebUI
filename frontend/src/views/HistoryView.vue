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
    <div class="page-header">
      <h2 class="page-title">히스토리</h2>
      <div class="header-actions">
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
      <div class="empty-content">
        <div class="empty-icon">📜</div>
        <h3 class="empty-title">히스토리가 없습니다</h3>
        <p class="empty-desc">이미지를 편집하면 여기에 기록됩니다.</p>
      </div>
    </div>

    <template v-else>
      <!-- Timeline -->
      <div class="card timeline-card">
        <h3 class="card-title">타임라인</h3>
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
      <div v-if="selectedItem" class="details-grid">
        <!-- Image Preview -->
        <div class="card">
          <h3 class="card-title">이미지</h3>
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
          <h3 class="card-title">편집 정보</h3>
          
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
          <div class="detail-actions">
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
      <div v-else class="card no-selection">
        <p>타임라인에서 항목을 선택하세요</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.history-view {
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

.header-actions {
  display: flex;
  gap: 0.5rem;
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

.empty-state {
  padding: 4rem 1rem;
}

.empty-content {
  text-align: center;
}

.empty-icon {
  font-size: 3.75rem;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.empty-desc {
  color: #6b7280;
}

.timeline-card {
  margin-bottom: 1.5rem;
}

.timeline-container {
  overflow-x: auto;
  padding-bottom: 1rem;
}

.timeline-scroll {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: max-content;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.timeline-thumbnail {
  width: 5rem;
  height: 5rem;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.timeline-thumbnail:hover {
  border-color: #7dd3fc;
}

.timeline-item.is-selected .timeline-thumbnail {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 2px #bae6fd;
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.timeline-info {
  text-align: center;
}

.timeline-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.timeline-arrow {
  width: 1rem;
  height: 1rem;
  color: #9ca3af;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .details-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.image-preview {
  aspect-ratio: 1;
  background-color: #f3f4f6;
  border-radius: 0.5rem;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.details-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
}

.detail-label {
  font-size: 0.875rem;
  color: #6b7280;
  width: 6rem;
  flex-shrink: 0;
}

.detail-value {
  font-size: 0.875rem;
  color: #1f2937;
}

.detail-actions {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.no-selection {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}
</style>
