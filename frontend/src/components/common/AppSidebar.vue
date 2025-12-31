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
@reference "tailwindcss";

.sidebar {
  width: 14rem;
  background-color: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
}

.sidebar.is-collapsed {
  width: 4rem;
}

.menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
  text-align: left;
  color: #4b5563;
}

.menu-item:hover {
  background-color: #f9fafb;
  color: #111827;
}

.menu-item.is-active {
  background-color: #f0f9ff;
  color: #0284c7;
  font-weight: 500;
}

.menu-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.menu-text {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.menu-label {
  font-size: 0.875rem;
}

.menu-desc {
  font-size: 0.75rem;
  color: #38bdf8;
}

.sidebar.is-collapsed .menu-item {
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
}

.collapse-toggle {
  padding: 0.5rem;
  border-top: 1px solid #f3f4f6;
}

.toggle-btn {
  width: 100%;
  padding: 0.5rem;
  border-radius: 0.5rem;
  color: #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background-color: #f3f4f6;
  color: #4b5563;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #f3f4f6;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 4rem;
  }
  
  .menu-text {
    display: none;
  }
  
  .menu-item {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
  }
  
  .sidebar-footer,
  .collapse-toggle {
    display: none;
  }
}
</style>
