<script setup lang="ts">
import { computed } from 'vue'
import { Picture } from '@element-plus/icons-vue'

const props = defineProps<{
  src?: string | null
  alt?: string
  placeholder?: string
  loading?: boolean
}>()

const hasImage = computed(() => !!props.src)
</script>

<template>
  <div class="image-preview">
    <!-- Loading state -->
    <template v-if="loading">
      <div class="placeholder">
        <el-skeleton animated>
          <template #template>
            <el-skeleton-item variant="image" style="width: 100%; height: 100%;" />
          </template>
        </el-skeleton>
      </div>
    </template>

    <!-- Image -->
    <template v-else-if="hasImage">
      <img :src="src!" :alt="alt || 'Image'" class="preview-image" />
    </template>

    <!-- Placeholder -->
    <template v-else>
      <div class="placeholder">
        <Picture class="placeholder-icon" />
        <p class="placeholder-text">{{ placeholder || '이미지가 없습니다' }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.image-preview {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-color: #f9fafb;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.placeholder-icon {
  width: 3rem;
  height: 3rem;
  color: #d1d5db;
  margin-bottom: 0.5rem;
}

.placeholder-text {
  color: #9ca3af;
  font-size: 0.875rem;
}
</style>
