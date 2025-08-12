# Solver-Verifier: RFP 비즈니스 요구사항 추출 시스템

RFP(Request for Proposal) 문서에서 정확한 비즈니스 요구사항을 추출하는 6단계 Analyzer-Verifier 파이프라인 시스템입니다. Gemini 2.5 Pro의 IMO 2025 접근법에서 영감을 받아 이중 에이전트 아키텍처를 사용합니다.

## 🎯 주요 기능

- **6단계 파이프라인**: 초안 작성 → 자체 개선 → 검증 → 리뷰 → 버그 수정 → 최종 승인/거부
- **이중 에이전트 시스템**: Analyzer(요구사항 추출) + Verifier(검증) 구조
- **다양한 문서 형식 지원**: PDF, Markdown, Text, DOCX, PPTX, XLSX
- **실시간 웹 인터페이스**: React 기반 업로드 및 진행 상황 모니터링
- **품질 메트릭**: 정확도, 재현율, 추적성 등 종합적인 품질 지표
- **인용 추적**: 모든 요구사항에 대한 출처 문서 참조

## 🏗️ 시스템 아키텍처

### 6단계 파이프라인

1. **1단계: 초기 BR 초안** - Analyzer가 인용을 포함한 요구사항 추출
2. **2단계: 자체 개선** - Analyzer가 초안을 세밀화하고 향상
3. **3단계: 검증** - Verifier가 요구사항을 검증하고 버그 리포트 생성
4. **4단계: 리뷰 (선택사항)** - 인간/AI 검토자의 검증 결과 리뷰
5. **5단계: 버그 수정** - Analyzer가 검증 이슈 해결
6. **6단계: 승인/거부** - 품질 메트릭을 기반으로 한 최종 결정

### 핵심 컴포넌트

- **PipelineService**: 완전한 6단계 프로세스 오케스트레이션
- **AnalyzerService**: 비즈니스 요구사항 추출 및 세밀화 (Solver 역할)
- **VerifierService**: 소스 문서 대비 요구사항 검증 (Verifier 역할)
- **WebSocket Manager**: 실시간 진행 상황 업데이트
- **Document Parser**: 다양한 파일 형식 파싱

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.10 이상
- [uv](https://docs.astral.sh/uv/) 패키지 매니저
- OpenAI API 키

### 설치 방법

```bash
# 리포지토리 클론
git clone <repository-url>
cd solver-verifier

# 환경 변수 파일 설정
cp .env.example .env
# .env 파일에서 OPENAI_API_KEY 설정

# 의존성 설치
uv sync

# 프론트엔드 빌드 (선택사항)
./scripts/build-frontend.sh

# 애플리케이션 실행
uv run uvicorn main:app --reload
```

### 웹 인터페이스 사용

1. 브라우저에서 `http://localhost:8000` 접속
2. RFP 문서 업로드 (드래그 앤 드롭 지원)
3. 프로젝트 이름과 설명 입력
4. "요구사항 분석" 버튼 클릭
5. 실시간으로 6단계 파이프라인 진행 상황 모니터링
6. 결과에서 추출된 비즈니스 요구사항과 품질 메트릭 확인

## 🔧 설정

### 환경 변수

`.env.example` 파일을 참고하여 `.env` 파일을 생성하세요:

```bash
# 필수 설정
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# 선택적 설정
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=4000
OUTPUT_DIRECTORY=./output
```

### 에이전트 프롬프트 커스터마이징

시스템 프롬프트는 다음 방법으로 설정할 수 있습니다:

1. **자동 로드**: `prompts/analyzer_prompt.txt` 및 `prompts/verifier_prompt.txt` 파일에서 자동 로드
2. **환경 변수**: `ANALYZER_SYSTEM_PROMPT` 및 `VERIFIER_SYSTEM_PROMPT` 설정
3. **API를 통한 런타임 변경**: `/pipeline/configure/analyzer` 및 `/pipeline/configure/verifier` 엔드포인트 사용

## 📚 API 문서

### 주요 엔드포인트

- `POST /pipeline/process` - RFP 문서 업로드 및 처리 시작
- `GET /pipeline/status/{set_id}` - 처리 상태 확인 (WebSocket 지원)
- `POST /pipeline/configure/analyzer` - Analyzer 시스템 프롬프트 설정
- `POST /pipeline/configure/verifier` - Verifier 시스템 프롬프트 설정
- `GET /pipeline/stages` - 파이프라인 단계 정보 조회
- `GET /health` - 헬스 체크
- `GET /api` - API 정보 및 엔드포인트 목록

### API 사용 예시

```bash
# 문서 처리 시작
curl -X POST "http://localhost:8000/pipeline/process" \
  -F "files=@rfp_document.pdf" \
  -F "files=@requirements.md" \
  -F "set_name=프로젝트 알파" \
  -F "set_description=전자상거래 플랫폼 RFP"

# 파이프라인 단계 확인
curl http://localhost:8000/pipeline/stages

# Analyzer 프롬프트 설정
curl -X POST "http://localhost:8000/pipeline/configure/analyzer" \
  -F "system_prompt=사용자 정의 analyzer 프롬프트"
```

### WebSocket 연결

실시간 업데이트를 위한 WebSocket 연결:

```javascript
const ws = new WebSocket(`ws://localhost:8000/pipeline/status/${setId}`);
ws.onmessage = (event) => {
    const progress = JSON.parse(event.data);
    console.log('진행 상황:', progress);
};
```

## 🧪 개발 가이드

### 프로젝트 구조

```
solver-verifier/
├── solver_verifier/          # 메인 애플리케이션 패키지
│   ├── api/                  # FastAPI 라우터 및 엔드포인트
│   ├── models/               # Pydantic 모델 및 데이터 구조
│   └── services/             # 비즈니스 로직 및 서비스 구현
├── tests/                    # 테스트 파일
├── prompts/                  # 에이전트 시스템 프롬프트
├── frontend/                 # React 웹 인터페이스
├── scripts/                  # 빌드 및 유틸리티 스크립트
├── main.py                   # FastAPI 애플리케이션 진입점
└── pyproject.toml           # uv/Python 프로젝트 설정
```

### 개발 명령어

```bash
# 개발 서버 실행 (자동 재로드)
uv run uvicorn main:app --reload

# 테스트 실행
uv add --dev pytest pytest-cov pytest-asyncio httpx
uv run pytest

# 프론트엔드 개발 서버 (백엔드 프록시 포함)
cd frontend && npm start

# 프론트엔드 빌드
./scripts/build-frontend.sh

# 새 의존성 추가
uv add <package>
uv add --dev <dev-package>
```

### 테스트

```bash
# 모든 테스트 실행
uv run pytest

# 커버리지와 함께 테스트 실행
uv run pytest --cov=solver_verifier

# 특정 테스트 파일 실행
uv run pytest tests/test_specific.py

# 상세 출력과 함께 테스트 실행
uv run pytest -v
```

## 📊 지원하는 문서 형식

- **PDF**: markitdown 라이브러리를 사용한 텍스트 추출
- **Markdown (.md)**: UTF-8/CP949 인코딩 지원 직접 파싱
- **텍스트 (.txt)**: 직접 텍스트 파싱
- **Microsoft Office**: DOCX, PPTX, XLSX (markitdown 사용)

## 🔍 품질 메트릭

시스템은 다음과 같은 품질 지표를 제공합니다:

- **재현율 (Recall)**: 원본 문서의 요구사항 포함도
- **정확도 (Precision)**: 추출된 요구사항의 정확성
- **추적성 (Traceability)**: 요구사항과 출처 문서 간의 매핑
- **완성도 (Completeness)**: 비즈니스 요구사항의 상세 수준
- **검증 통과율**: Verifier 검증을 통과한 요구사항 비율

## 🛠️ 기술 스택

- **Python 3.10+**: 핵심 언어
- **FastAPI**: 비동기 웹 API 프레임워크
- **Uvicorn**: ASGI 서버
- **uv**: 고속 Python 패키지 매니저
- **Pydantic**: 데이터 검증 및 직렬화
- **OpenAI API**: LLM 서비스
- **WebSocket**: 실시간 통신
- **React**: 프론트엔드 웹 인터페이스
- **Tailwind CSS**: 스타일링

## 🤝 기여 방법

1. Fork 후 브랜치 생성
2. 변경사항 구현
3. 테스트 추가 및 실행
4. Pull Request 제출

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 🐛 문제 신고

버그나 기능 요청은 GitHub Issues를 통해 신고해 주세요.

---

**참고**: 이 시스템은 Gemini 2.5 Pro의 IMO 2025 접근법에서 영감을 받아 개발되었으며, 복잡한 비즈니스 문서에서 정확한 요구사항을 추출하기 위한 이중 검증 시스템을 구현합니다.