<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Edit, 
  MagicStick, 
  Files, 
  Timer, 
  Picture, 
  Setting,
  Fold,
  Expand
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const isCollapsed = ref(false)

const menuItems = [
  { path: '/edit', icon: Edit, label: '편집', description: '이미지 편집' },
  { path: '/style', icon: MagicStick, label: '스타일', description: '스타일 변환' },
  { path: '/batch', icon: Files, label: '배치', description: '배치 처리' },
  { path: '/history', icon: Timer, label: '히스토리', description: '편집 히스토리' },
  { path: '/gallery', icon: Picture, label: '갤러리', description: '저장된 이미지' },
  { path: '/settings', icon: Setting, label: '설정', description: '앱 설정' }
]

const currentPath = computed(() => route.path)

const navigateTo = (path: string) => {
  router.push(path)
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <aside 
    class="sidebar"
    :class="{ 'is-collapsed': isCollapsed }"
  >
    <nav class="flex-1 py-4">
      <ul class="space-y-1 px-2">
        <li v-for="item in menuItems" :key="item.path">
          <button
            @click="navigateTo(item.path)"
            class="menu-item"
            :class="{ 'is-active': currentPath === item.path }"
            :title="isCollapsed ? item.label : undefined"
          >
            <component :is="item.icon" class="menu-icon" />
            <div v-if="!isCollapsed" class="menu-text">
              <span class="menu-label">{{ item.label }}</span>
              <span 
                v-if="currentPath === item.path"
                class="menu-desc"
              >
                {{ item.description }}
              </span>
            </div>
          </button>
        </li>
      </ul>
    </nav>

    <!-- Collapse Toggle -->
    <div class="collapse-toggle">
      <button @click="toggleCollapse" class="toggle-btn">
        <Fold v-if="!isCollapsed" class="w-4 h-4" />
        <Expand v-else class="w-4 h-4" />
      </button>
    </div>

    <!-- Footer -->
    <div v-if="!isCollapsed" class="sidebar-footer">
      <div class="text-xs text-gray-400 text-center">
        Qwen Image Edit v1.0.0
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  @apply w-56 bg-white border-r border-gray-200 flex flex-col transition-all duration-300;
}

.sidebar.is-collapsed {
  @apply w-16;
}

.menu-item {
  @apply w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all text-left
         text-gray-600 hover:bg-gray-50 hover:text-gray-900;
}

.menu-item.is-active {
  @apply bg-primary-50 text-primary-600 font-medium;
}

.menu-icon {
  @apply w-5 h-5 flex-shrink-0;
}

.menu-text {
  @apply flex flex-col overflow-hidden;
}

.menu-label {
  @apply text-sm;
}

.menu-desc {
  @apply text-xs text-primary-400;
}

.sidebar.is-collapsed .menu-item {
  @apply justify-center px-0;
}

.collapse-toggle {
  @apply px-2 py-2 border-t border-gray-100;
}

.toggle-btn {
  @apply w-full p-2 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 
         flex items-center justify-center transition-colors;
}

.sidebar-footer {
  @apply p-4 border-t border-gray-100;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .sidebar {
    @apply w-16;
  }
  
  .menu-text {
    @apply hidden;
  }
  
  .menu-item {
    @apply justify-center px-0;
  }
  
  .sidebar-footer,
  .collapse-toggle {
    @apply hidden;
  }
}
</style>
