# Qwen Image Edit WebUI - Frontend

Vue 3 + TypeScript 기반의 Qwen Image Edit 프론트엔드 애플리케이션입니다.

## 기술 스택

- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript
- **Build Tool**: Vite
- **상태 관리**: Pinia
- **라우팅**: Vue Router
- **HTTP Client**: Axios
- **UI Framework**: Element Plus
- **스타일링**: Tailwind CSS

## 시작하기

### 필수 조건

- Node.js 18.x 이상
- npm 또는 yarn

### 설치

```bash
cd frontend
npm install
```

### 개발 서버 실행

```bash
npm run dev
```

개발 서버가 `http://localhost:3000`에서 시작됩니다.

### 프로덕션 빌드

```bash
npm run build
```

빌드 결과물은 `dist` 폴더에 생성됩니다.

### 프리뷰

```bash
npm run preview
```

## 프로젝트 구조

```
src/
├── api/                    # API 클라이언트
│   ├── client.ts          # Axios 인스턴스
│   ├── auth.ts            # 인증 API
│   ├── model.ts           # 모델 관리 API
│   ├── edit.ts            # 이미지 편집 API
│   ├── batch.ts           # 배치 처리 API
│   ├── history.ts         # 히스토리 API
│   ├── gallery.ts         # 갤러리 API
│   ├── settings.ts        # 설정 API
│   └── websocket.ts       # WebSocket 유틸리티
├── components/
│   ├── common/            # 공통 컴포넌트
│   ├── editor/            # 편집 관련 컴포넌트
│   ├── gallery/           # 갤러리 컴포넌트
│   └── settings/          # 설정 컴포넌트
├── composables/           # 재사용 로직
├── router/                # Vue Router 설정
├── stores/                # Pinia 스토어
├── types/                 # TypeScript 타입 정의
├── utils/                 # 유틸리티 함수
├── views/                 # 페이지 컴포넌트
├── App.vue                # 루트 컴포넌트
├── main.ts                # 엔트리 포인트
└── style.css              # 글로벌 스타일
```

## 주요 기능

### 이미지 편집
- 이미지 업로드 (드래그 앤 드롭 지원)
- 프롬프트 기반 이미지 편집
- 실시간 진행률 표시 (WebSocket)
- 편집 파라미터 조절

### 스타일 변환
- 8가지 프리셋 스타일 (Ghibli, Anime, Realistic 등)
- 스타일 강도 조절
- 추가 프롬프트 지원

### 배치 처리
- 다중 이미지 동시 업로드
- 공통 프롬프트 적용
- 개별 진행률 표시

### 갤러리
- 그리드 뷰
- 원본/편집 이미지 비교
- 즐겨찾기
- 다운로드

### 히스토리
- 타임라인 뷰
- Undo/Redo 지원

### 설정
- 모델 관리 (로드/언로드/다운로드)
- 최적화 설정
- 자동화 설정
- 편집 기본값

## 환경 변수

`.env` 파일을 생성하여 설정할 수 있습니다:

```env
# API 서버 URL (프록시를 사용하지 않는 경우)
VITE_API_BASE_URL=http://localhost:8000
```

## 백엔드 연동

개발 환경에서는 Vite 프록시를 통해 백엔드 서버와 연동됩니다.
`vite.config.ts`에서 프록시 설정을 확인할 수 있습니다.

백엔드 서버가 `http://localhost:8000`에서 실행 중이어야 합니다.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
