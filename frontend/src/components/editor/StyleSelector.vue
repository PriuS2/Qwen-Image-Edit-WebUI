<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { stylesApi } from '@/api'
import type { StylePreset } from '@/types'

const props = defineProps<{
  modelValue: string | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

// 동적으로 로드되는 스타일 목록
const styles = ref<StylePreset[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

const selectedStyle = computed(() => props.modelValue)

const selectStyle = (styleName: string) => {
  if (!props.disabled) {
    emit('update:modelValue', styleName)
  }
}

const loadStyles = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await stylesApi.getAll(true) // enabled_only=true
    if (response.success && response.data) {
      styles.value = response.data
    }
  } catch (err) {
    console.error('Failed to load styles:', err)
    error.value = '스타일 로드 실패'
  } finally {
    isLoading.value = false
  }
}

// 스타일 목록 새로고침 (외부에서 호출 가능)
const refresh = () => {
  loadStyles()
}

onMounted(() => {
  loadStyles()
})

// 외부에서 접근 가능하도록 expose
defineExpose({ refresh })
</script>

<template>
  <div class="style-selector">
    <label class="label">스타일 선택</label>
    
    <div v-if="isLoading" class="loading-state">
      <el-skeleton :rows="2" animated />
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <el-button size="small" @click="loadStyles">다시 시도</el-button>
    </div>
    
    <div v-else-if="styles.length === 0" class="empty-state">
      <p>등록된 스타일이 없습니다.</p>
    </div>
    
    <div v-else class="style-grid">
      <button
        v-for="style in styles"
        :key="style.id"
        class="style-card"
        :class="{ 
          'is-selected': selectedStyle === style.name,
          'is-disabled': disabled
        }"
        :disabled="disabled"
        @click="selectStyle(style.name)"
      >
        <span class="style-icon">{{ style.icon }}</span>
        <span class="style-label">{{ style.label }}</span>
        <span class="style-desc">{{ style.description }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.style-selector {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.loading-state,
.error-state,
.empty-state {
  padding: 1rem;
  text-align: center;
  color: #6b7280;
}

.error-state p,
.empty-state p {
  margin-bottom: 0.5rem;
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .style-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1024px) {
  .style-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

.style-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  border-radius: 0.75rem;
  border: 2px solid #e5e7eb;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.style-card:hover {
  border-color: #7dd3fc;
  background-color: rgba(240, 249, 255, 0.3);
}

.style-card.is-selected {
  border-color: #0ea5e9;
  background-color: #f0f9ff;
  box-shadow: 0 0 0 2px #bae6fd;
}

.style-card.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.style-card.is-disabled:hover {
  border-color: #e5e7eb;
  background-color: white;
}

.style-icon {
  font-size: 1.875rem;
  margin-bottom: 0.5rem;
}

.style-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
}

.style-desc {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.125rem;
}
</style>
