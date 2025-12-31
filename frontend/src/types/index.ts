// API Response Types
export interface ApiResponse<T = unknown> {
  success: boolean
  message?: string
  data?: T
}

// Model Types
export interface ModelStatus {
  is_loaded: boolean
  model_name: string
  device: string
  dtype: string
  vram_used_gb: number
  vram_total_gb: number
  optimization: OptimizationSettings
}

export interface OptimizationSettings {
  enable_model_cpu_offload: boolean
  enable_attention_slicing: boolean
  enable_vae_slicing: boolean
  enable_vae_tiling: boolean
  enable_xformers: boolean
}

export interface AvailableModel {
  model_id: string
  name: string
  description: string
  size_gb: number
  is_downloaded: boolean
  is_recommended: boolean
}

export interface DownloadStatus {
  status: 'idle' | 'downloading' | 'completed' | 'failed' | 'cancelled'
  model_name: string
  progress_percent: number
  downloaded_size_mb: number
  total_size_mb: number | null
  current_file: string | null
  files_completed: number
  files_total: number
  error_message: string | null
}

// Edit Types
export interface EditParams {
  prompt: string
  negative_prompt?: string
  num_inference_steps?: number
  true_cfg_scale?: number
  guidance_scale?: number
  seed?: number
  num_images_per_prompt?: number
}

export interface EditRequest {
  image: string
  params: EditParams
  response_format?: 'url' | 'base64'
  session_id?: string
  save_to_gallery?: boolean
}

export interface StyleTransferRequest {
  image: string
  style: StyleType
  intensity?: number
  additional_prompt?: string
  response_format?: 'url' | 'base64'
  session_id?: string
  save_to_gallery?: boolean
}

export type StyleType = 
  | 'ghibli' 
  | 'anime' 
  | 'realistic' 
  | 'oil_painting' 
  | 'watercolor' 
  | 'sketch' 
  | 'cyberpunk' 
  | 'vintage'

export interface JobStatus {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  result: JobResult | null
  error: string | null
}

export interface JobResult {
  image: string
  format: 'url' | 'base64'
  width: number
  height: number
  seed_used: number
  gallery_id: string
  history_id: string
}

// Batch Types
export interface BatchItem {
  image: string
  params: EditParams
}

export interface BatchJob {
  id: string
  type: 'batch'
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  input_data: unknown
  output_data: unknown | null
  error_message: string | null
  session_id: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}

// History Types
export interface HistoryItem {
  id: string
  session_id: string
  original_image_path: string
  edited_image_path: string
  prompt: string
  parameters: EditParams
  parent_id: string | null
  position: number
  created_at: string
}

export interface UndoRedoResult {
  success: boolean
  message: string
  current_position: number
  image_path: string
  can_undo: boolean
  can_redo: boolean
}

// Gallery Types
export interface GalleryItem {
  id: string
  image_url: string
  thumbnail_url: string
  original_image_url?: string
  title: string
  description: string
  is_favorite: boolean
  metadata: GalleryMetadata
  history_id?: string
  created_at: string
}

export interface GalleryMetadata {
  prompt: string
  seed: number
  width: number
  height: number
}

export interface GalleryCompareData {
  original_url: string
  edited_url: string
  metadata: GalleryMetadata
}

// Settings Types
export interface AppSettings {
  auto_unload: AutoUnloadSettings
  auto_load: AutoLoadSettings
  default_model: string
  torch_dtype: string
  optimization: OptimizationSettings
  edit_defaults: EditDefaults
  gallery: GallerySettings
}

export interface AutoUnloadSettings {
  enabled: boolean
  timeout_minutes: number
}

export interface AutoLoadSettings {
  enabled: boolean
}

export interface EditDefaults {
  num_inference_steps: number
  true_cfg_scale: number
  guidance_scale: number
}

export interface GallerySettings {
  max_history_per_session: number
  auto_cleanup_days: number
  thumbnail_size: number
}

// WebSocket Types
export interface ProgressMessage {
  job_id: string
  progress: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  result: JobResult | null
  error: string | null
}
