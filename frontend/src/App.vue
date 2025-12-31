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
  <div class="min-h-screen flex flex-col bg-gray-50">
    <AppHeader />
    <div class="flex flex-1">
      <AppSidebar />
      <main class="flex-1 p-6 overflow-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Layout specific styles */
</style>
