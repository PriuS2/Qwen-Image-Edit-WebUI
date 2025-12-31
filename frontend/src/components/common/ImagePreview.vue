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
            <el-skeleton-item variant="image" class="w-full h-full" />
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
        <Picture class="w-12 h-12 text-gray-300 mb-2" />
        <p class="text-gray-400 text-sm">{{ placeholder || '이미지가 없습니다' }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.image-preview {
  @apply relative w-full aspect-square border border-gray-200 rounded-xl 
         flex items-center justify-center overflow-hidden bg-gray-50;
}

.preview-image {
  @apply w-full h-full object-contain;
}

.placeholder {
  @apply flex flex-col items-center justify-center w-full h-full;
}
</style>
