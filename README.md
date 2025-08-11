# 일짜곰 (Iljjagom) - AI 기반 문서 인식 및 질의응답 시스템

## 프로젝트 개요

일짜곰은 카메라를 통해 책이나 문서를 실시간으로 감지하고, OCR을 통해 텍스트를 추출한 후 AI를 활용하여 사용자의 질문에 답변하는 통합 시스템입니다. YOLOv5 기반의 커스텀 문서 감지 모델, Tesseract OCR, OpenAI STT/TTS, Google Gemini AI를 조합하여 구현되었습니다.

## 시스템 아키텍처

```
사용자 입력 (텍스트/음성) → 문서 감지 → 이미지 캡처 → OCR 처리 → AI 분석 → 응답 생성 → 음성/텍스트 출력
```

## 파일 구조

```
iljjagom/
├── core/                           # 핵심 시스템 모듈
│   ├── main.py                     # 메인 애플리케이션 컨트롤러
│   ├── interface.py                # Pygame 기반 사용자 인터페이스
│   ├── detect_sys.py               # YOLOv5 문서 감지 시스템
│   ├── inform_sys.py               # 이미지 캡처 및 OCR 처리
│   ├── ai_system.py                # Gemini AI 통합 시스템
│   └── voice_sys.py                # OpenAI 음성 인식/합성 시스템
├── conversation/                   # 대화 기록 저장소
│   ├── record.json                 # 대화 세션 메타데이터
│   ├── image/                      # 캡처된 이미지들
│   ├── ocr/                        # OCR 결과 텍스트 파일들
│   └── voice/                      # 녹음된 음성 파일들
├── models/                         # YOLOv5 모델 정의
├── utils/                          # YOLOv5 유틸리티 함수들
├── data/                           # 데이터셋 설정 파일들
├── runs/train/document_yolov5s_results/weights/
│   └── best.pt                     # 커스텀 훈련된 문서 감지 모델
├── test_code/                      # 테스트 및 검증 스크립트들
└── requirements.txt                # 의존성 패키지 목록
```

## 핵심 모듈 설명

### 1. main.py - 메인 애플리케이션 컨트롤러

```python
class MainApp:
    def __init__(self, camera_source=0):
        # 모든 핵심 시스템 초기화
        self.interface = ReadAIInterface()
        self.detect_system = BookDetector(inform_system, camera_source=camera_source)
        self.inform_system = InformSystem()
        self.ai_system = AISystem()
        self.voice_system = VoiceSystem()
```

**주요 기능:**
- 모든 서브시스템 초기화 및 통합
- 사용자 입력 방식 (텍스트/음성) 결정
- 대화 세션 기록 관리 (JSON 형태)
- 시스템 간 데이터 플로우 제어

### 2. interface.py - 사용자 인터페이스

```python
class ReadAIInterface:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        self.font = pygame.font.Font("fonts/NanumGothic.ttf", 20)
```

**주요 기능:**
- Pygame 기반 GUI 구현
- 한국어 폰트 지원 (나눔고딕)
- 4개 화면: 시작화면, 텍스트입력, 음성입력, 응답표시
- 텍스트 자동 줄바꿈 및 스크롤 기능
- 실시간 음성 녹음 시각적 피드백

### 3. detect_sys.py - 문서 감지 시스템

```python
class BookDetector:
    def __init__(self, inform_system, weights=None, camera_source=0):
        self.model = DetectMultiBackend(weights, device=self.device)
        self.names = self.model.names  # 클래스 이름: {0: 'document'}
```

**주요 기능:**
- YOLOv5 기반 실시간 문서 감지
- 커스텀 훈련 모델 사용 (document 클래스, 신뢰도 0.6 이상)
- 5초간 안정적 감지 후 자동 캡처
- OpenCV 기반 카메라 제어 및 바운딩 박스 표시
- ESC 키로 감지 중단 가능

**감지 로직:**
1. 카메라에서 프레임 읽기
2. YOLOv5 모델로 추론
3. 'document' 클래스 감지 시 바운딩 박스 표시
4. 동일 위치에서 5초간 안정적 감지 확인
5. 조건 만족 시 자동 캡처 및 OCR 진행

### 4. inform_sys.py - 이미지 처리 및 OCR

```python
class InformSystem:
    def perform_ocr(self, image_path):
        # 다중 전처리 방법 적용
        # 1. 적응적 이진화
        # 2. OTSU 이진화  
        # 3. 원본 그레이스케일
        # 가장 긴 결과 선택
```

**주요 기능:**
- 바운딩 박스 기반 이미지 자르기 (여백 추가)
- 이미지 품질 향상 (크기 조정, 노이즈 제거)
- Tesseract OCR 다중 처리 방법
- 한국어+영어 언어팩 사용 (kor+eng)
- 다양한 PSM/OEM 모드로 최적 결과 선택

**OCR 전처리 과정:**
1. 바운딩 박스에 10px 여백 추가
2. 200px 미만 이미지 자동 확대
3. 그레이스케일 변환 및 노이즈 제거
4. 적응적 이진화/OTSU 이진화 적용
5. 5가지 PSM 모드로 OCR 수행
6. 가장 긴 결과를 최종 선택

### 5. ai_system.py - AI 분석 및 응답

```python
class AISystem:
    def __init__(self):
        self.client = genai.GenerativeModel('gemini-1.5-flash')
        self.system_instruction = "당신은 한국어로 답변하는 도서 도우미..."
```

**주요 기능:**
- Google Gemini 1.5 Flash 모델 사용
- 한국어 도서 도우미 시스템 지시문 적용
- 질문 유형 분석 (book_related, general, unclear)
- Few-shot learning 예시 포함
- OCR 텍스트와 사용자 질문 통합 분석

**AI 응답 프로세스:**
1. 사용자 질문 유형 분석
2. OCR 텍스트와 질문 결합한 프롬프트 생성
3. Gemini API 호출로 응답 생성
4. 한국어 자연어 응답 반환

### 6. voice_sys.py - 음성 처리

```python
class VoiceSystem:
    def __init__(self):
        self.client = OpenAI()
        self.is_recording = False
        self.audio_data = []
```

**주요 기능:**
- OpenAI Whisper API 기반 STT
- 실시간 음성 녹음 (16kHz, 16bit, mono)
- 최소 1초 이상 녹음 검증
- 녹음 파일 자동 저장 (conversation/voice/)
- pyaudio 기반 오디오 스트림 제어

**음성 처리 플로우:**
1. 사용자가 녹음 시작/중지
2. 실시간으로 오디오 데이터 수집
3. WAV 형태로 임시 저장
4. OpenAI Whisper API로 텍스트 변환
5. 원본 음성 파일 영구 보존

## 대화 기록 시스템

### conversation/record.json 구조
```json
{
    "conversations": [
        {
            "id": 1,
            "timestamp": "2024-08-11 13:45:23",
            "input_method": "voice",
            "user_question": "이 책의 주제가 뭐야?",
            "ai_response": "이 문서는 OCR 테스트에 관한 내용입니다...",
            "image_path": "conversation/image/capture_20240811_134523.jpg",
            "ocr_path": "conversation/ocr/ocr_20240811_134523.txt", 
            "voice_path": "conversation/voice/recording_20240811_134523.wav"
        }
    ]
}
```

## 환경 설정

### 필요한 API 키
```bash
# .env 파일에 설정
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 주요 의존성
- **YOLOv5**: 문서 감지
- **OpenCV**: 이미지 처리 및 카메라 제어  
- **Tesseract OCR**: 텍스트 추출 (한국어 언어팩 필요)
- **Pygame**: GUI 인터페이스
- **PyTorch**: YOLOv5 모델 실행
- **OpenAI**: 음성 인식/합성
- **Google Generative AI**: 텍스트 분석 및 응답

### Tesseract 설정
```python
# Windows 환경
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# 한국어 언어팩 설치 필요: kor.traineddata
```

## 실행 방법

### 기본 실행
```bash
python core/main.py
```

### 카메라 소스 지정
```bash
python core/main.py 1  # 1번 카메라 사용
```

## 시스템 플로우

1. **시작**: 메인 애플리케이션 실행
2. **입력 선택**: 사용자가 텍스트/음성 입력 방식 선택
3. **문서 감지**: 카메라로 문서 실시간 감지 (5초 안정화)
4. **이미지 처리**: 자동 캡처 및 OCR 텍스트 추출
5. **AI 분석**: Gemini AI로 질문 분석 및 응답 생성
6. **결과 출력**: 텍스트 또는 음성으로 응답 제공
7. **기록 저장**: 모든 대화 내역 자동 저장

## 성능 특징

### OCR 성능
- **영어 텍스트**: 95% 이상 정확도
- **한국어 텍스트**: 85% 이상 정확도 (글자 간격 이슈)
- **혼합 텍스트**: 영어와 한국어 동시 인식 가능
- **숫자/특수문자**: 높은 인식률

### 문서 감지 성능
- **감지 속도**: 실시간 (30fps)
- **정확도**: 신뢰도 0.6 이상 필터링
- **안정성**: 5초 연속 감지로 오감지 방지

### AI 응답 품질
- **한국어 자연어 처리**: 높은 품질
- **문맥 이해**: OCR 텍스트 기반 정확한 분석
- **응답 속도**: 2-5초 내 응답 생성

## 향후 개선 사항

1. **OCR 정확도 향상**: 한국어 글자 간격 문제 해결
2. **인터페이스 수정**: 설정 기능 및 깔끔한 인터페이스
3. **기억 능력, 검색 능력**: 기억력을 추가하여 이어지는 대화 가능하도록 수정
