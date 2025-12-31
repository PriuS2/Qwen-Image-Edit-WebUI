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
  <div class="edit-form">
    <!-- Prompts -->
    <div class="prompts-section">
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
    <div class="params-grid">
      <div class="params-column">
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

      <div class="params-column">
        <ParameterSlider
          v-model="trueCfgScale"
          label="True CFG 스케일"
          :min="1"
          :max="20"
          :step="0.1"
          :disabled="disabled"
        />

        <!-- Seed -->
        <div class="seed-section">
          <div class="seed-header">
            <label class="seed-label">시드</label>
            <span class="seed-value">
              {{ seed === -1 ? '랜덤' : seed }}
            </span>
          </div>
          <div class="seed-input">
            <el-input-number
              v-model="seed"
              :min="-1"
              :max="2147483647"
              :disabled="disabled"
              class="seed-number"
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
    <div class="num-images-section">
      <label class="num-images-label">생성 이미지 수</label>
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
@reference "tailwindcss";

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.prompts-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.params-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .params-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.params-column {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.seed-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.seed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.seed-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.seed-value {
  font-size: 0.875rem;
  color: #0284c7;
  font-weight: 500;
}

.seed-input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.seed-number {
  flex: 1;
}

.num-images-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.num-images-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}
</style>
