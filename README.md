# Logos-pipe-ocr
LLM 기반 OCR 모델을 쉽게 사용하고 평가할 수 있는 라이브러리입니다.

## 📦 설치 및 실행

### Run CLI

```bash
########################
# 만약 직접 소스 실행 시
########################
# 가상 환경 활성화
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 패키지 설치
pip install -e .
```

### CLI 실행
```bash
# 자세한 실행방식은 help 참조
# 실행하는 모델에 따라 환경변수 설정 필요 (아래 참고)
logos -h
```

## 🌍 환경변수 설정
- OpenAI API 또는 Gemini API 호출 시 환경변수 설정 필요
- .env 파일 생성하거나 환경변수 직접 설정

```bash
########################
# .env 파일 사용 시     
########################
# .env.template을 .env로 복사
cp .env.template .env

########################
# 환경변수 설정 예시
########################
export OPENAI_API_KEY=<openai API 호출을 위한 API KEY>
export GEMINI_API_KEY=<gemini API 호출을 위한 API KEY>
# 설명:
#   OPENAI_API_KEY:  <openai API 호출을 위한 API KEY>
#   GEMINI_API_KEY:  <gemini API 호출을 위한 API KEY>
```

## 📚 라이브러리 사용법

### 모델 사용방법
- 모델 사용 시 모델명 형식: `<플랫폼>::<모델명>`
- 모델은 코드를 통해 실행하거나 CLI 명령어를 통해 실행할 수 있음 (아래 참고)
- 모델명 예시
    - `openai::gpt-4o-mini`
    - `gemini::gemini-1.5-pro`
- 지원하는 모델은 `logos_pipe_ocr.core.model` 참고

```python
# 모델 사용 예시
from logos_pipe_ocr.core import load_model
model = load_model("openai::gpt-4o-mini")
model = load_model("google::gemini-1.5-pro")
```

## 🛠️ 개발

```bash
# 의존성 설치
pip install -r requirements.txt

# 패키지 설치
pip install -e .

# 테스트 실행
./scripts/dev/unit_test.sh

# (선택 사항) 코드 개발 시 포맷 체크 실행
./scripts/dev/format.sh

# 개발 시작!
```
