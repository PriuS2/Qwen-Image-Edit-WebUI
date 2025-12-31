# Qwen Image Edit API 문서

## 개요

Qwen-Image-Edit-2511 기반 이미지 편집 API입니다.

- **Base URL**: `http://localhost:8000`
- **API 문서 (Swagger UI)**: `http://localhost:8000/docs`
- **API 문서 (ReDoc)**: `http://localhost:8000/redoc`

---

## 인증

모든 API 요청에는 인증이 필요합니다.

### 인증 방법

다음 두 가지 방법 중 하나를 사용합니다:

| 방법 | 헤더 | 값 |
|------|------|-----|
| API Key | `X-API-Key` | `your-api-key` |
| Bearer Token | `Authorization` | `Bearer your-api-key` |

### 기본 API Key

```
qwen-image-edit-default-key
```

> ⚠️ **주의**: 프로덕션 환경에서는 `.env` 파일에서 `API_KEY` 환경변수를 변경하세요.

### 예시

```bash
# X-API-Key 헤더 사용
curl -H "X-API-Key: qwen-image-edit-default-key" http://localhost:8000/api/model/status

# Authorization 헤더 사용
curl -H "Authorization: Bearer qwen-image-edit-default-key" http://localhost:8000/api/model/status
```

---

## 헬스 체크

### GET `/`

API 루트 - 기본 헬스 체크

**응답 예시:**
```json
{
  "name": "Qwen Image Edit API",
  "version": "1.0.0",
  "status": "running"
}
```

### GET `/health`

상세 헬스 체크

**응답 예시:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

---

## 인증 API

### GET `/api/auth/verify`

API Key 검증

**헤더:**
- `X-API-Key`: API 키 (필수)

**응답:**
```json
{
  "success": true,
  "message": "API Key is valid"
}
```

---

## 모델 관리 API

### GET `/api/model/status`

현재 모델 상태 조회

**응답:**
```json
{
  "success": true,
  "data": {
    "is_loaded": true,
    "model_name": "ovedrive/Qwen-Image-Edit-2511-4bit",
    "device": "cuda:0",
    "dtype": "bfloat16",
    "vram_used_gb": 8.5,
    "vram_total_gb": 24.0,
    "optimization": {
      "enable_model_cpu_offload": true,
      "enable_attention_slicing": true,
      "enable_vae_slicing": true,
      "enable_vae_tiling": false,
      "enable_xformers": false
    }
  }
}
```

### GET `/api/model/available`

사용 가능한 모델 목록 조회

**응답:**
```json
{
  "success": true,
  "models": [
    {
      "model_id": "ovedrive/Qwen-Image-Edit-2511-4bit",
      "name": "Qwen-Image-Edit 4bit",
      "description": "4비트 양자화 모델 (권장)",
      "size_gb": 8.5,
      "is_downloaded": true,
      "is_recommended": true
    }
  ]
}
```

### POST `/api/model/download`

모델 다운로드 시작 (백그라운드)

**요청 본문:**
```json
{
  "model_name": "ovedrive/Qwen-Image-Edit-2511-4bit",
  "force_download": false
}
```

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `model_name` | string | `ovedrive/Qwen-Image-Edit-2511-4bit` | Hugging Face 모델 ID |
| `force_download` | boolean | `false` | 이미 존재해도 다시 다운로드 |

**응답:**
```json
{
  "success": true,
  "message": "Download started for ovedrive/Qwen-Image-Edit-2511-4bit",
  "data": {
    "status": "downloading",
    "model_name": "ovedrive/Qwen-Image-Edit-2511-4bit",
    "progress_percent": 0,
    "downloaded_size_mb": 0,
    "total_size_mb": null,
    "current_file": null,
    "files_completed": 0,
    "files_total": 0,
    "error_message": null
  }
}
```

### GET `/api/model/download/status`

모델 다운로드 진행 상태 조회

**응답:**
```json
{
  "success": true,
  "message": "Download status: downloading",
  "data": {
    "status": "downloading",
    "model_name": "ovedrive/Qwen-Image-Edit-2511-4bit",
    "progress_percent": 45.5,
    "downloaded_size_mb": 3890.5,
    "total_size_mb": 8550.0,
    "current_file": "model-00003-of-00005.safetensors",
    "files_completed": 2,
    "files_total": 5,
    "error_message": null
  }
}
```

**다운로드 상태 (status):**
| 값 | 설명 |
|-----|------|
| `idle` | 대기 중 |
| `downloading` | 다운로드 중 |
| `completed` | 완료 |
| `failed` | 실패 |
| `cancelled` | 취소됨 |

### POST `/api/model/download/cancel`

모델 다운로드 취소

**응답:**
```json
{
  "success": true,
  "message": "Download cancellation requested",
  "data": { ... }
}
```

### GET `/api/model/download/check/{model_name}`

특정 모델의 다운로드 여부 확인

**경로 파라미터:**
- `model_name`: 모델 ID (예: `ovedrive/Qwen-Image-Edit-2511-4bit`)

**응답:**
```json
{
  "success": true,
  "model_name": "ovedrive/Qwen-Image-Edit-2511-4bit",
  "is_downloaded": true
}
```

### POST `/api/model/load`

모델 로드

**요청 본문 (선택):**
```json
{
  "model_name": "ovedrive/Qwen-Image-Edit-2511-4bit",
  "optimization": {
    "enable_model_cpu_offload": true,
    "enable_attention_slicing": true,
    "enable_vae_slicing": true,
    "enable_vae_tiling": false,
    "enable_xformers": false
  },
  "force_reload": false
}
```

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `model_name` | string | null | 로드할 모델 (없으면 기본 모델 사용) |
| `optimization` | object | null | 최적화 설정 (없으면 저장된 설정 사용) |
| `force_reload` | boolean | `false` | 이미 로드된 경우에도 다시 로드 |

**응답:**
```json
{
  "success": true,
  "message": "Model loaded successfully",
  "data": {
    "is_loaded": true,
    "model_name": "ovedrive/Qwen-Image-Edit-2511-4bit",
    "device": "cuda:0",
    "dtype": "bfloat16",
    "vram_used_gb": 8.5,
    "vram_total_gb": 24.0,
    "optimization": { ... }
  }
}
```

### POST `/api/model/unload`

모델 언로드 (VRAM 해제)

**응답:**
```json
{
  "success": true,
  "message": "Model unloaded successfully",
  "vram_freed_gb": 8.5
}
```

### GET `/api/model/optimization`

현재 최적화 설정 조회

**응답:**
```json
{
  "success": true,
  "saved_settings": {
    "enable_model_cpu_offload": true,
    "enable_attention_slicing": true,
    "enable_vae_slicing": true,
    "enable_vae_tiling": false,
    "enable_xformers": false
  },
  "applied_settings": { ... },
  "is_model_loaded": true
}
```

### PUT `/api/model/optimization`

최적화 설정 변경

**요청 본문:**
```json
{
  "optimization": {
    "enable_model_cpu_offload": true,
    "enable_attention_slicing": true,
    "enable_vae_slicing": true,
    "enable_vae_tiling": true,
    "enable_xformers": false
  },
  "apply_immediately": true
}
```

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `apply_immediately` | boolean | `false` | 즉시 적용 (모델 재로드) |

---

## 이미지 편집 API

### 편집 파라미터 (EditParams)

모든 편집 API에서 공통으로 사용되는 파라미터입니다.

| 필드 | 타입 | 기본값 | 범위 | 설명 |
|------|------|--------|------|------|
| `prompt` | string | (필수) | - | 편집 지시 프롬프트 |
| `negative_prompt` | string | `" "` | - | 제외할 요소 |
| `num_inference_steps` | integer | `20` | 1-100 | 추론 스텝 수 |
| `true_cfg_scale` | float | `4.0` | 1.0-20.0 | True CFG 스케일 |
| `guidance_scale` | float | `1.0` | 0.0-20.0 | 가이던스 스케일 |
| `seed` | integer | `-1` | - | 시드 (-1: 랜덤) |
| `num_images_per_prompt` | integer | `1` | 1-4 | 생성할 이미지 수 |

### POST `/api/edit/single`

단일 이미지 편집 (JSON 방식)

**요청 본문:**
```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "params": {
    "prompt": "Make the sky purple",
    "negative_prompt": " ",
    "num_inference_steps": 20,
    "true_cfg_scale": 4.0,
    "guidance_scale": 1.0,
    "seed": -1,
    "num_images_per_prompt": 1
  },
  "response_format": "url",
  "session_id": "my-session-001",
  "save_to_gallery": true
}
```

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `image` | string | (필수) | Base64 인코딩된 이미지 또는 URL |
| `params` | EditParams | (필수) | 편집 파라미터 |
| `response_format` | string | `"url"` | `"url"` 또는 `"base64"` |
| `session_id` | string | null | 세션 ID (히스토리용) |
| `save_to_gallery` | boolean | `true` | 갤러리에 저장 |

**응답:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Job submitted successfully"
}
```

### POST `/api/edit/upload/single`

단일 이미지 편집 (파일 업로드 방식)

**Content-Type:** `multipart/form-data`

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `image` | file | (필수) | 편집할 이미지 파일 |
| `prompt` | string | (필수) | 편집 지시 프롬프트 |
| `negative_prompt` | string | `" "` | 제외할 요소 |
| `num_inference_steps` | integer | `20` | 추론 스텝 수 (1-100) |
| `true_cfg_scale` | float | `4.0` | True CFG 스케일 (1.0-20.0) |
| `guidance_scale` | float | `1.0` | 가이던스 스케일 (0.0-20.0) |
| `seed` | integer | `-1` | 시드 (-1: 랜덤) |
| `num_images_per_prompt` | integer | `1` | 생성할 이미지 수 (1-4) |
| `response_format` | string | `"url"` | 응답 형식 |
| `session_id` | string | null | 세션 ID |
| `save_to_gallery` | boolean | `true` | 갤러리에 저장 |

**예시 (curl):**
```bash
curl -X POST "http://localhost:8000/api/edit/upload/single" \
  -H "X-API-Key: qwen-image-edit-default-key" \
  -F "image=@photo.jpg" \
  -F "prompt=Make it look like a painting"
```

### POST `/api/edit/multi`

다중 이미지 편집 (합성) - JSON 방식

최대 3개의 이미지를 합성합니다.

**요청 본문:**
```json
{
  "images": [
    "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "data:image/png;base64,iVBORw0KGgoAAAANS..."
  ],
  "params": {
    "prompt": "Combine these images into a collage",
    "num_inference_steps": 20
  },
  "response_format": "url",
  "session_id": null,
  "save_to_gallery": true
}
```

### POST `/api/edit/upload/multi`

다중 이미지 편집 (파일 업로드 방식)

**Content-Type:** `multipart/form-data`

최대 3개의 이미지 파일을 업로드하여 합성합니다.

**예시 (curl):**
```bash
curl -X POST "http://localhost:8000/api/edit/upload/multi" \
  -H "X-API-Key: qwen-image-edit-default-key" \
  -F "images=@photo1.jpg" \
  -F "images=@photo2.jpg" \
  -F "prompt=Merge these photos together"
```

### POST `/api/edit/style-transfer`

스타일 변환 (JSON 방식)

**요청 본문:**
```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "style": "ghibli",
  "intensity": 1.0,
  "additional_prompt": "add cherry blossoms",
  "response_format": "url",
  "session_id": null,
  "save_to_gallery": true
}
```

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `image` | string | (필수) | Base64 인코딩된 이미지 또는 URL |
| `style` | string | (필수) | 스타일 이름 (아래 표 참조) |
| `intensity` | float | `1.0` | 스타일 강도 (0.1-2.0) |
| `additional_prompt` | string | null | 추가 프롬프트 |
| `response_format` | string | `"url"` | 응답 형식 |
| `session_id` | string | null | 세션 ID |
| `save_to_gallery` | boolean | `true` | 갤러리에 저장 |

**사용 가능한 스타일:**

| 스타일 | 설명 |
|--------|------|
| `ghibli` | 지브리 스타일 |
| `anime` | 애니메이션 스타일 |
| `realistic` | 사실적 스타일 |
| `oil_painting` | 유화 스타일 |
| `watercolor` | 수채화 스타일 |
| `sketch` | 스케치 스타일 |
| `cyberpunk` | 사이버펑크 스타일 |
| `vintage` | 빈티지 스타일 |

### POST `/api/edit/upload/style-transfer`

스타일 변환 (파일 업로드 방식)

**Content-Type:** `multipart/form-data`

**예시 (curl):**
```bash
curl -X POST "http://localhost:8000/api/edit/upload/style-transfer" \
  -H "X-API-Key: qwen-image-edit-default-key" \
  -F "image=@photo.jpg" \
  -F "style=ghibli" \
  -F "intensity=1.5"
```

### GET `/api/edit/job/{job_id}`

작업 상태 조회

**경로 파라미터:**
- `job_id`: 작업 ID

**응답:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "result": {
    "image": "/storage/images/20240101_120000_abc123.png",
    "format": "url",
    "width": 1024,
    "height": 1024,
    "seed_used": 12345,
    "gallery_id": "gallery-001",
    "history_id": "history-001"
  },
  "error": null
}
```

**작업 상태 (status):**
| 값 | 설명 |
|-----|------|
| `pending` | 대기 중 |
| `processing` | 처리 중 |
| `completed` | 완료 |
| `failed` | 실패 |
| `cancelled` | 취소됨 |

---

## 배치 처리 API

### POST `/api/batch/submit`

배치 작업 제출

**요청 본문:**
```json
{
  "items": [
    {
      "image": "data:image/png;base64,iVBORw0KGgo...",
      "params": {
        "prompt": "Make it sunny",
        "num_inference_steps": 20
      }
    },
    {
      "image": "data:image/png;base64,iVBORw0KGgo...",
      "params": {
        "prompt": "Add snow",
        "num_inference_steps": 25
      }
    }
  ],
  "response_format": "url",
  "session_id": "batch-session-001",
  "save_to_gallery": true
}
```

**응답:**
```json
{
  "success": true,
  "job_id": "batch-550e8400-e29b-41d4-a716-446655440000",
  "total_items": 2,
  "message": "Batch job submitted with 2 items"
}
```

### GET `/api/batch/{job_id}`

배치 작업 상태 조회

**응답:**
```json
{
  "success": true,
  "data": {
    "id": "batch-550e8400-e29b-41d4-a716-446655440000",
    "type": "batch",
    "status": "processing",
    "progress": 50,
    "input_data": { ... },
    "output_data": null,
    "error_message": null,
    "session_id": "batch-session-001",
    "created_at": "2024-01-01T12:00:00Z",
    "started_at": "2024-01-01T12:00:05Z",
    "completed_at": null
  }
}
```

### DELETE `/api/batch/{job_id}`

배치 작업 취소

**응답:**
```json
{
  "success": true,
  "message": "Batch job batch-550e8400-e29b-41d4-a716-446655440000 cancelled"
}
```

### GET `/api/batch/list`

진행 중인 배치 작업 목록

**쿼리 파라미터:**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `session_id` | string | null | 세션 ID로 필터 |
| `limit` | integer | `50` | 최대 조회 수 |

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": "batch-001",
      "type": "batch",
      "status": "processing",
      "progress": 50,
      "session_id": "my-session",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1
}
```

---

## 히스토리 API

### GET `/api/history`

작업 히스토리 목록

**쿼리 파라미터:**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `session_id` | string | null | 세션 ID로 필터 |
| `limit` | integer | `50` | 최대 조회 수 (1-100) |
| `offset` | integer | `0` | 오프셋 |

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": "history-001",
      "session_id": "my-session",
      "original_image_path": "uploads/original_001.png",
      "edited_image_path": "images/edited_001.png",
      "prompt": "Make the sky blue",
      "parameters": {
        "num_inference_steps": 20,
        "true_cfg_scale": 4.0
      },
      "parent_id": null,
      "position": 0,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1
}
```

### GET `/api/history/{history_id}`

특정 히스토리 상세 조회

**응답:**
```json
{
  "success": true,
  "data": {
    "id": "history-001",
    "session_id": "my-session",
    "original_image_path": "uploads/original_001.png",
    "edited_image_path": "images/edited_001.png",
    "prompt": "Make the sky blue",
    "parameters": { ... },
    "parent_id": null,
    "position": 0,
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### POST `/api/history/{history_id}/undo`

이전 상태로 복원 (Undo)

**응답:**
```json
{
  "success": true,
  "message": "Undo successful",
  "current_position": 0,
  "image_path": "/storage/images/original_001.png",
  "can_undo": false,
  "can_redo": true
}
```

### POST `/api/history/{history_id}/redo`

다음 상태로 복원 (Redo)

**응답:**
```json
{
  "success": true,
  "message": "Redo successful",
  "current_position": 1,
  "image_path": "/storage/images/edited_001.png",
  "can_undo": true,
  "can_redo": false
}
```

### DELETE `/api/history/{history_id}`

히스토리 항목 삭제

**응답:**
```json
{
  "success": true,
  "message": "History history-001 deleted"
}
```

---

## 갤러리 API

### GET `/api/gallery`

갤러리 이미지 목록

**쿼리 파라미터:**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `limit` | integer | `50` | 최대 조회 수 (1-100) |
| `offset` | integer | `0` | 오프셋 |
| `favorites_only` | boolean | `false` | 즐겨찾기만 조회 |

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": "gallery-001",
      "image_url": "/storage/images/edited_001.png",
      "thumbnail_url": "/storage/thumbnails/edited_001_thumb.png",
      "title": "Blue Sky Image",
      "description": "Made the sky blue",
      "is_favorite": false,
      "metadata": {
        "prompt": "Make the sky blue",
        "seed": 12345,
        "width": 1024,
        "height": 1024
      },
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### GET `/api/gallery/{gallery_id}`

갤러리 이미지 상세

**응답:**
```json
{
  "success": true,
  "data": {
    "id": "gallery-001",
    "image_url": "/storage/images/edited_001.png",
    "thumbnail_url": "/storage/thumbnails/edited_001_thumb.png",
    "original_image_url": "/storage/uploads/original_001.png",
    "title": "Blue Sky Image",
    "description": "Made the sky blue",
    "is_favorite": false,
    "metadata": { ... },
    "history_id": "history-001",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

### GET `/api/gallery/{gallery_id}/compare`

원본/편집 이미지 비교 데이터

**응답:**
```json
{
  "success": true,
  "data": {
    "original_url": "/storage/uploads/original_001.png",
    "edited_url": "/storage/images/edited_001.png",
    "metadata": { ... }
  }
}
```

### GET `/api/gallery/{gallery_id}/download`

이미지 다운로드

**응답:** 이미지 파일 (Content-Type: image/png)

### PATCH `/api/gallery/{gallery_id}`

갤러리 아이템 업데이트

**쿼리 파라미터:**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `title` | string | null | 제목 |
| `description` | string | null | 설명 |
| `is_favorite` | boolean | null | 즐겨찾기 여부 |

**예시:**
```bash
curl -X PATCH "http://localhost:8000/api/gallery/gallery-001?is_favorite=true" \
  -H "X-API-Key: qwen-image-edit-default-key"
```

**응답:**
```json
{
  "success": true,
  "message": "Gallery item updated"
}
```

### DELETE `/api/gallery/{gallery_id}`

갤러리 아이템 삭제

**쿼리 파라미터:**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `delete_files` | boolean | `true` | 파일도 함께 삭제 |

**응답:**
```json
{
  "success": true,
  "message": "Gallery item gallery-001 deleted"
}
```

---

## 설정 API

### GET `/api/settings`

전체 설정 조회

**응답:**
```json
{
  "success": true,
  "data": {
    "auto_unload": {
      "enabled": true,
      "timeout_minutes": 30
    },
    "auto_load": {
      "enabled": true
    },
    "default_model": "ovedrive/Qwen-Image-Edit-2511-4bit",
    "torch_dtype": "bfloat16",
    "optimization": {
      "enable_model_cpu_offload": true,
      "enable_attention_slicing": true,
      "enable_vae_slicing": true,
      "enable_vae_tiling": false,
      "enable_xformers": false
    },
    "edit_defaults": {
      "num_inference_steps": 20,
      "true_cfg_scale": 4.0,
      "guidance_scale": 1.0
    },
    "gallery": {
      "max_history_per_session": 10,
      "auto_cleanup_days": 7,
      "thumbnail_size": 256
    }
  }
}
```

### PUT `/api/settings`

전체 설정 업데이트

**요청 본문:**
```json
{
  "auto_unload": {
    "enabled": true,
    "timeout_minutes": 60
  },
  "auto_load": {
    "enabled": true
  },
  "default_model": "ovedrive/Qwen-Image-Edit-2511-4bit",
  "torch_dtype": "bfloat16",
  "optimization": {
    "enable_model_cpu_offload": true,
    "enable_attention_slicing": true,
    "enable_vae_slicing": true,
    "enable_vae_tiling": false,
    "enable_xformers": false
  },
  "edit_defaults": {
    "num_inference_steps": 25,
    "true_cfg_scale": 4.0,
    "guidance_scale": 1.0
  },
  "gallery": {
    "max_history_per_session": 20,
    "auto_cleanup_days": 14,
    "thumbnail_size": 256
  }
}
```

### GET `/api/settings/auto-unload`

자동 언로드 설정 조회

**응답:**
```json
{
  "success": true,
  "data": {
    "enabled": true,
    "timeout_minutes": 30
  },
  "idle_minutes": 15
}
```

### PUT `/api/settings/auto-unload`

자동 언로드 설정 변경

**요청 본문:**
```json
{
  "enabled": true,
  "timeout_minutes": 60
}
```

### GET `/api/settings/auto-load`

자동 로드 설정 조회

**응답:**
```json
{
  "success": true,
  "data": {
    "enabled": true
  }
}
```

### PUT `/api/settings/auto-load`

자동 로드 설정 변경

**요청 본문:**
```json
{
  "enabled": false
}
```

### POST `/api/settings/reset`

설정 초기화 (기본값으로 리셋)

**응답:**
```json
{
  "success": true,
  "data": { ... }
}
```

---

## WebSocket API

### WS `/ws/progress/{job_id}`

작업 진행률 실시간 수신

**연결 예시 (JavaScript):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/progress/550e8400-e29b-41d4-a716-446655440000');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress, '%');
  
  if (data.status === 'completed') {
    console.log('Result:', data.result);
    ws.close();
  }
  
  if (data.error) {
    console.error('Error:', data.error);
    ws.close();
  }
};

// 연결 유지를 위한 ping
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send('ping');
  }
}, 25000);
```

**수신 메시지 형식:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": 75,
  "status": "processing",
  "result": null,
  "error": null
}
```

**완료 시:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": 100,
  "status": "completed",
  "result": {
    "image": "/storage/images/edited_001.png",
    "format": "url",
    "width": 1024,
    "height": 1024,
    "seed_used": 12345,
    "gallery_id": "gallery-001",
    "history_id": "history-001"
  },
  "error": null
}
```

**실패 시:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": 0,
  "status": "failed",
  "result": null,
  "error": "Out of memory"
}
```

---

## 정적 파일

### GET `/storage/{path}`

저장된 이미지 파일 접근

- **이미지**: `/storage/images/{filename}`
- **썸네일**: `/storage/thumbnails/{filename}`
- **업로드**: `/storage/uploads/{filename}`

**예시:**
```
http://localhost:8000/storage/images/20240101_120000_abc123.png
```

---

## 에러 응답

### 표준 에러 형식

```json
{
  "detail": "Error message here"
}
```

### HTTP 상태 코드

| 코드 | 설명 |
|------|------|
| `400` | Bad Request - 잘못된 요청 |
| `401` | Unauthorized - 인증 실패 |
| `403` | Forbidden - 접근 거부 |
| `404` | Not Found - 리소스 없음 |
| `409` | Conflict - 충돌 (예: 모델 로딩 중) |
| `422` | Unprocessable Entity - 유효성 검증 실패 |
| `500` | Internal Server Error - 서버 오류 |
| `503` | Service Unavailable - 서비스 불가 (모델 미로드) |

### 인증 실패 (401)
```json
{
  "detail": "Invalid API key"
}
```

### 모델 미로드 (503)
```json
{
  "detail": "Model not loaded. Please load the model first or enable auto_load."
}
```

### 유효성 검증 실패 (422)
```json
{
  "detail": [
    {
      "loc": ["body", "params", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 환경 변수

`.env` 파일에서 설정 가능한 환경 변수:

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `DEBUG` | `false` | 디버그 모드 |
| `HOST` | `0.0.0.0` | 서버 호스트 |
| `PORT` | `8000` | 서버 포트 |
| `API_KEY` | `qwen-image-edit-default-key` | API 인증 키 |
| `DEFAULT_MODEL` | `ovedrive/Qwen-Image-Edit-2511-4bit` | 기본 모델 |
| `TORCH_DTYPE` | `bfloat16` | PyTorch 데이터 타입 |
| `AUTO_UNLOAD_ENABLED` | `true` | 자동 언로드 활성화 |
| `AUTO_UNLOAD_TIMEOUT_MINUTES` | `30` | 자동 언로드 타임아웃 (분) |
| `AUTO_LOAD_ON_REQUEST` | `true` | 요청 시 자동 로드 |
| `ENABLE_MODEL_CPU_OFFLOAD` | `true` | CPU 오프로딩 |
| `ENABLE_ATTENTION_SLICING` | `true` | Attention 슬라이싱 |
| `ENABLE_VAE_SLICING` | `true` | VAE 슬라이싱 |
| `ENABLE_VAE_TILING` | `false` | VAE 타일링 |
| `ENABLE_XFORMERS` | `false` | xFormers 활성화 |

---

## 사용 예시

### Python 클라이언트 예시

```python
import requests
import base64
from pathlib import Path

API_URL = "http://localhost:8000"
API_KEY = "qwen-image-edit-default-key"

headers = {"X-API-Key": API_KEY}

# 1. 모델 상태 확인
response = requests.get(f"{API_URL}/api/model/status", headers=headers)
status = response.json()
print(f"Model loaded: {status['data']['is_loaded']}")

# 2. 모델 로드 (필요시)
if not status['data']['is_loaded']:
    response = requests.post(f"{API_URL}/api/model/load", headers=headers)
    print(response.json()['message'])

# 3. 이미지 편집 (파일 업로드 방식)
with open("photo.jpg", "rb") as f:
    files = {"image": ("photo.jpg", f, "image/jpeg")}
    data = {
        "prompt": "Make the sky purple and add stars",
        "num_inference_steps": 25
    }
    response = requests.post(
        f"{API_URL}/api/edit/upload/single",
        headers=headers,
        files=files,
        data=data
    )

job_id = response.json()["job_id"]
print(f"Job submitted: {job_id}")

# 4. 작업 상태 폴링
import time

while True:
    response = requests.get(f"{API_URL}/api/edit/job/{job_id}", headers=headers)
    job_status = response.json()
    
    print(f"Progress: {job_status['progress']}%")
    
    if job_status['status'] == 'completed':
        result = job_status['result']
        print(f"Done! Image URL: {API_URL}{result['image']}")
        break
    elif job_status['status'] == 'failed':
        print(f"Failed: {job_status['error']}")
        break
    
    time.sleep(1)
```

### JavaScript/TypeScript 클라이언트 예시

```typescript
const API_URL = "http://localhost:8000";
const API_KEY = "qwen-image-edit-default-key";

async function editImage(file: File, prompt: string): Promise<string> {
  const formData = new FormData();
  formData.append("image", file);
  formData.append("prompt", prompt);
  
  // 작업 제출
  const submitResponse = await fetch(`${API_URL}/api/edit/upload/single`, {
    method: "POST",
    headers: { "X-API-Key": API_KEY },
    body: formData
  });
  
  const { job_id } = await submitResponse.json();
  
  // WebSocket으로 진행률 수신
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/progress/${job_id}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(`Progress: ${data.progress}%`);
      
      if (data.status === "completed") {
        resolve(`${API_URL}${data.result.image}`);
        ws.close();
      }
      
      if (data.error) {
        reject(new Error(data.error));
        ws.close();
      }
    };
    
    // Keep-alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
      }
    }, 25000);
    
    ws.onclose = () => clearInterval(pingInterval);
  });
}

// 사용 예시
const fileInput = document.querySelector<HTMLInputElement>("#fileInput");
fileInput?.addEventListener("change", async (e) => {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (file) {
    try {
      const resultUrl = await editImage(file, "Make it look like anime style");
      console.log("Result:", resultUrl);
    } catch (error) {
      console.error("Error:", error);
    }
  }
});
```

---

## 변경 이력

| 버전 | 날짜 | 변경 사항 |
|------|------|-----------|
| 1.0.0 | 2024-01-01 | 초기 버전 |
