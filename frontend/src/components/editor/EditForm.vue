<script setup lang="ts">
import { computed } from 'vue'
import type { EditParams } from '@/types'
import PromptInput from './PromptInput.vue'
import ParameterSlider from './ParameterSlider.vue'
import { RefreshRight } from '@element-plus/icons-vue'

const props = defineProps<{
  params: EditParams
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:params', params: EditParams): void
  (e: 'randomSeed'): void
}>()

const updateParam = <K extends keyof EditParams>(key: K, value: EditParams[K]) => {
  emit('update:params', { ...props.params, [key]: value })
}

const prompt = computed({
  get: () => props.params.prompt,
  set: (value: string) => updateParam('prompt', value)
})

const negativePrompt = computed({
  get: () => props.params.negative_prompt || '',
  set: (value: string) => updateParam('negative_prompt', value)
})

const numInferenceSteps = computed({
  get: () => props.params.num_inference_steps || 20,
  set: (value: number) => updateParam('num_inference_steps', value)
})

const trueCfgScale = computed({
  get: () => props.params.true_cfg_scale || 4.0,
  set: (value: number) => updateParam('true_cfg_scale', value)
})

const guidanceScale = computed({
  get: () => props.params.guidance_scale || 1.0,
  set: (value: number) => updateParam('guidance_scale', value)
})

const seed = computed({
  get: () => props.params.seed ?? -1,
  set: (value: number) => updateParam('seed', value)
})

const numImages = computed({
  get: () => props.params.num_images_per_prompt || 1,
  set: (value: number) => updateParam('num_images_per_prompt', value)
})

const randomizeSeed = () => {
  updateParam('seed', -1)
  emit('randomSeed')
}
</script>

<template>
  <div class="edit-form space-y-6">
    <!-- Prompts -->
    <div class="space-y-4">
      <PromptInput
        v-model="prompt"
        label="프롬프트"
        placeholder="이미지를 어떻게 편집할지 설명하세요..."
        :rows="3"
        :disabled="disabled"
      />
      
      <PromptInput
        v-model="negativePrompt"
        label="네거티브 프롬프트"
        placeholder="원하지 않는 요소를 입력하세요 (선택사항)"
        :rows="2"
        :disabled="disabled"
      />
    </div>

    <!-- Parameters Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="space-y-4">
        <ParameterSlider
          v-model="numInferenceSteps"
          label="추론 스텝"
          :min="1"
          :max="100"
          :step="1"
          :disabled="disabled"
        />
        
        <ParameterSlider
          v-model="guidanceScale"
          label="가이던스 스케일"
          :min="0"
          :max="20"
          :step="0.1"
          :disabled="disabled"
        />
      </div>

      <div class="space-y-4">
        <ParameterSlider
          v-model="trueCfgScale"
          label="True CFG 스케일"
          :min="1"
          :max="20"
          :step="0.1"
          :disabled="disabled"
        />

        <!-- Seed -->
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <label class="text-sm font-medium text-gray-700">시드</label>
            <span class="text-sm text-primary-600 font-medium">
              {{ seed === -1 ? '랜덤' : seed }}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <el-input-number
              v-model="seed"
              :min="-1"
              :max="2147483647"
              :disabled="disabled"
              class="flex-1"
              controls-position="right"
            />
            <el-button
              :icon="RefreshRight"
              :disabled="disabled"
              @click="randomizeSeed"
              title="랜덤 시드"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Number of images -->
    <div class="space-y-2">
      <label class="text-sm font-medium text-gray-700">생성 이미지 수</label>
      <el-radio-group v-model="numImages" :disabled="disabled">
        <el-radio-button :value="1">1장</el-radio-button>
        <el-radio-button :value="2">2장</el-radio-button>
        <el-radio-button :value="3">3장</el-radio-button>
        <el-radio-button :value="4">4장</el-radio-button>
      </el-radio-group>
    </div>
  </div>
</template>

<style scoped>
</style>
