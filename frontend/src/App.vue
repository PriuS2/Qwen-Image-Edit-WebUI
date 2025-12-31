<script setup lang="ts">
import { onMounted } from 'vue'
import AppHeader from './components/common/AppHeader.vue'
import AppSidebar from './components/common/AppSidebar.vue'
import { useModelStore } from './stores/model'
import { useSettingsStore } from './stores/settings'

const modelStore = useModelStore()
const settingsStore = useSettingsStore()

onMounted(async () => {
  // Load initial data
  await Promise.all([
    modelStore.fetchStatus(),
    settingsStore.fetchSettings()
  ])
})
</script>

<template>
  <div class="app-container">
    <AppHeader />
    <div class="app-body">
      <AppSidebar />
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f9fafb;
}

.app-body {
  display: flex;
  flex: 1;
}

.app-main {
  flex: 1;
  padding: 1.5rem;
  overflow: auto;
}
</style>
