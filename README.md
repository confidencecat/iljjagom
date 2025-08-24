# 일짜곰 (iljjagom) - AI 도서 인식 및 질문 답변 시스템

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**일짜곰**은 책의 내용을 카메라로 인식하고, 인식된 내용이나 일반적인 주제에 대해 음성 또는 텍스트로 자유롭게 질문하며 AI의 답변을 받을 수 있는 파이썬 기반의 데스크톱 애플리케이션입니다.

## 주요 기능

- **실시간 도서 인식**: YOLOv5 모델을 사용하여 카메라 영상에서 책(문서)을 실시간으로 탐지합니다.
- **자동 OCR 캡처**: 책이 5초 이상 안정적으로 감지되면 자동으로 해당 부분을 캡처하여 Clova OCR로 텍스트를 추출합니다.
- **다양한 질문 방식**: 텍스트 또는 음성으로 자유롭게 질문할 수 있습니다.
- **AI 답변**: Google Gemini의 언어 모델을 통해 사용자의 질문에 대한 답변을 생성합니다.
- **음성 답변 (TTS)**: 생성된 AI의 답변을 음성으로 들을 수 있습니다.

## 시스템 요구사항

- Python 3.9 이상
- Pygame 및 기타 라이브러리 (requirements.txt 참조)
- 웹캠 및 마이크

## 설치 방법

1.  **저장소 복제**
    ```bash
    git clone https://github.com/your-username/iljjagom.git
    cd iljjagom
    ```

2.  **가상 환경 생성 및 활성화**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **의존성 설치**
    ```bash
    pip install -r requirements.txt
    ```

## `.env` 환경 변수 설정

프로젝트를 실행하려면 API 키 설정이 필요합니다. 프로젝트 루트 디렉터리에 `.env` 파일을 생성하고 아래 내용을 채우세요.

```env
# Naver Cloud Platform의 Clova OCR API 정보
CLOVA_API_URL=YOUR_CLOVA_OCR_API_URL
CLOVA_SECRET_KEY=YOUR_CLOVA_OCR_SECRET_KEY

# Google AI Studio에서 발급받은 Gemini API 키
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

-   `CLOVA_API_URL`, `CLOVA_SECRET_KEY`: [Naver Cloud Platform](https://www.ncloud.com/)에서 Clova OCR 서비스를 신청하고 발급받은 API Gateway URL과 Secret Key를 입력합니다.
-   `GEMINI_API_KEY`: [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급받은 API 키를 입력합니다.

## 실행 방법

프로젝트 루트 디렉터리에서 아래 명령어를 실행하여 애플리케이션을 시작합니다.

```bash
python core/main.py
```

### 실행 옵션 (Arguments)

-   `--source INDEX`: 사용할 카메라의 인덱스 번호를 지정합니다. (기본값: `0`)
    ```bash
    python core/main.py --source 1
    ```
-   `--mic INDEX`: 사용할 마이크의 인덱스 번호를 지정합니다. (기본값: 시스템 기본 마이크)
-   `--tts`: AI의 답변을 자동으로 음성(TTS)으로 재생합니다.

## 인터페이스 설명

| 시작 화면 | 질문 방법 선택 |
| :---: | :---: |
| ![시작 화면](readme_data/Version02_인터페이스_시작-화면.png) | ![질문 방법 선택](readme_data/Version02_인터페이스_질문-선택-화면.png) |
| **질문하기**를 눌러 시작합니다. | **책 인식, 텍스트, 음성** 중 원하는 질문 방식을 선택합니다. |

| 책 인식 (OCR) | 텍스트 입력 |
| :---: | :---: |
| ![OCR 대기](readme_data/Version02_인터페이스_캡처-대기%20화면.png) | ![텍스트 입력](readme_data/Version02_인터페이스_텍스브-입력-화면.png) |
| 카메라에 책을 비추면 5초 후 자동 캡처됩니다. | 키보드로 자유롭게 질문을 입력합니다. |

| 음성 입력 | AI 응답 |
| :---: | :---: |
| ![음성 입력](readme_data/Version02_인터페이스_음성-입력-화면.png) | ![AI 응답](readme_data/Version02_인터페이스_AI-응답-화면.png) |
| **녹음 시작/중지**로 질문을 녹음하고 **질문 완료**를 누릅니다. | AI가 생성한 답변을 확인하고, **듣기** 버튼으로 음성 재생이 가능합니다. |

## 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.