import os
import cv2
import numpy as np
from datetime import datetime
import pytesseract
from PIL import Image
from dotenv import load_dotenv
import requests
import uuid
import json
import time

load_dotenv()

# Tesseract-OCR의 설치 경로를 지정
import os
import cv2
import numpy as np
from datetime import datetime
import pytesseract
from PIL import Image
from dotenv import load_dotenv
import requests
import uuid
import json
import time

load_dotenv()

# Tesseract-OCR의 설치 경로를 지정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class InformSystem:
    def __init__(self):
        self.image_dir = "conversation/image"
        self.ocr_dir = "conversation/ocr"
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.ocr_dir, exist_ok=True)
        
        # Clova OCR 설정
        self.clova_api_url = os.getenv("CLOVA_API_URL")
        self.clova_secret = os.getenv("CLOVA_SECRET_KEY")
        self.use_clova = bool(self.clova_api_url and self.clova_secret)
        
        # Clova OCR 설정
        self.clova_api_url = os.getenv("CLOVA_API_URL")
        self.clova_secret = os.getenv("CLOVA_SECRET_KEY")
        self.use_clova = bool(self.clova_api_url and self.clova_secret)
        
        print(f"Clova OCR 사용 가능: {self.use_clova}")

    def process_capture(self, capture_info):
        frame = capture_info['frame']
        bbox = capture_info['bbox']

        # 1. 바운딩 박스 캡처 (이미지 자르기)
        x1, y1, x2, y2 = bbox
        
        # 바운딩 박스에 여백 추가 (텍스트 잘림 방지)
        padding = 10
        height, width = frame.shape[:2]
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(width, x2 + padding)
        y2 = min(height, y2 + padding)
        
        cropped_image = frame[y1:y2, x1:x2]
        
        # 이미지 품질 개선
        # 1. 크기가 너무 작으면 확대
        crop_height, crop_width = cropped_image.shape[:2]
        if crop_height < 200 or crop_width < 200:
            scale_factor = max(200 / crop_height, 200 / crop_width)
            new_width = int(crop_width * scale_factor)
            new_height = int(crop_height * scale_factor)
            cropped_image = cv2.resize(cropped_image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            print(f"이미지 확대: {crop_width}x{crop_height} -> {new_width}x{new_height}")

        # 2. 이미지 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"capture_{timestamp}.jpg"
        image_path = os.path.join(self.image_dir, image_filename)
        
        # 고품질로 저장
        cv2.imwrite(image_path, cropped_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"이미지 저장 완료: {image_path}")

        # 3. OCR 진행
        ocr_text = self.perform_ocr(image_path)
        if ocr_text is None:
            return None, image_path, None

        # 4. OCR 결과 저장
        ocr_filename = f"ocr_{timestamp}.txt"
        ocr_path = os.path.join(self.ocr_dir, ocr_filename)
        with open(ocr_path, 'w', encoding='utf-8') as f:
            f.write(ocr_text)
        print(f"OCR 결과 저장 완료: {ocr_path}")

        return ocr_text, image_path, ocr_path

    def apply_clahe(self, img):
        """CLAHE (Contrast Limited Adaptive Histogram Equalization) 적용"""
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        if len(img.shape) == 3:
            img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
            img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0])
            return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        else:
            return clahe.apply(img)

    def apply_histogram_equalization(self, img):
        """히스토그램 평활화 적용"""
        if len(img.shape) == 3:
            img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
            img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
            return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        else:
            return cv2.equalizeHist(img)

    def clova_ocr(self, image_path):
        """Clova OCR API를 사용한 텍스트 인식"""
        if not self.use_clova:
            return None
            
        try:
            headers = {"X-OCR-SECRET": self.clova_secret}
            payload = {
                "version": "V2",
                "requestId": str(uuid.uuid4()),
                "timestamp": int(time.time() * 1000),
                "images": [{"format": "jpg", "name": "document"}]
            }
            
            with open(image_path, "rb") as f:
                files = [
                    ("file", f),
                    ("message", (None, json.dumps(payload), "application/json"))
                ]
                
                response = requests.post(self.clova_api_url, headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                texts = []
                for image in data.get("images", []):
                    for field in image.get("fields", []):
                        text = field.get("inferText", "")
                        if text.strip():
                            texts.append(text.strip())
                
                result = " ".join(texts)
                print(f"Clova OCR 결과: {len(result)}자")
                return result if result.strip() else None
            else:
                print(f"Clova OCR API 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Clova OCR 처리 중 오류: {e}")
            return None

    def apply_clahe(self, img):
        """CLAHE (Contrast Limited Adaptive Histogram Equalization) 적용"""
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        if len(img.shape) == 3:
            img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
            img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0])
            return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        else:
            return clahe.apply(img)

    def perform_clova_ocr(self, image_path):
        """Clova OCR을 사용한 텍스트 추출"""
        try:
            headers = {"X-OCR-SECRET": self.clova_secret}
            payload = {
                "version": "V2",
                "requestId": str(uuid.uuid4()),
                "timestamp": int(time.time() * 1000),
                "images": [{"format": "jpg", "name": "document"}]
            }
            
            with open(image_path, "rb") as image_file:
                files = [
                    ("file", image_file),
                    ("message", (None, json.dumps(payload), "application/json"))
                ]
                
                response = requests.post(self.clova_api_url, headers=headers, files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    texts = []
                    for image in data.get("images", []):
                        for field in image.get("fields", []):
                            texts.append(field.get("inferText", ""))
                    
                    result_text = " ".join(texts)
                    print(f"Clova OCR 성공: {len(result_text)}자 추출")
                    return result_text
                else:
                    print(f"Clova OCR 실패: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"Clova OCR 오류: {e}")
            return None

    def perform_ocr(self, image_path):
        try:
            # 1. 먼저 Clova OCR 시도 (더 정확한 결과)
            clova_result = self.clova_ocr(image_path)
            if clova_result and len(clova_result.strip()) > 10:  # 충분한 텍스트가 인식되면
                print(f"Clova OCR 사용: {len(clova_result)}자")
                return clova_result
            
            print("Tesseract OCR로 대체 처리...")
            
            # 2. Tesseract OCR로 대체 처리
            # 이미지 전처리 및 OCR 수행
            import cv2
            import numpy as np
            
            # OpenCV로 이미지 읽기
            cv_image = cv2.imread(image_path)
            if cv_image is None:
                return "[OCR 오류: 이미지를 읽을 수 없습니다]"
            
            # 그레이스케일 변환
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # 이미지 크기 확인 및 리사이징 (너무 작으면 확대)
            height, width = gray.shape
            if height < 100 or width < 100:
                # 이미지가 너무 작으면 2배 확대
                gray = cv2.resize(gray, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
                print(f"이미지 크기 조정: {width}x{height} -> {width*2}x{height*2}")
            
            # 노이즈 제거
            denoised = cv2.medianBlur(gray, 3)
            
            # 다양한 전처리 방법 적용
            processed_images = []
            
            # 1. CLAHE 적용 (최고 성능 방법 중 하나)
            clahe_img = self.apply_clahe(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))
            clahe_gray = cv2.cvtColor(clahe_img, cv2.COLOR_BGR2GRAY)
            processed_images.append(("CLAHE", clahe_gray))
            
            # 2. 히스토그램 평활화 적용 (최고 성능 방법)
            hist_img = self.apply_histogram_equalization(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))
            hist_gray = cv2.cvtColor(hist_img, cv2.COLOR_BGR2GRAY)
            processed_images.append(("히스토그램 평활화", hist_gray))
            
            # 3. 적응적 이진화
            adaptive_thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            processed_images.append(("적응적 이진화", adaptive_thresh))
            
            # 4. OTSU 이진화
            _, otsu_thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(("OTSU 이진화", otsu_thresh))
            
            # 5. 원본 그레이스케일
            processed_images.append(("원본 그레이스케일", gray))
            
            # 사용 가능한 언어 확인
            available_langs = pytesseract.get_languages()
            print(f"사용 가능한 언어: {available_langs}")
            
            # 언어 설정 결정
            if 'kor' in available_langs:
                lang_config = 'kor+eng'  # 한국어+영어 조합으로 더 나은 결과
                print("한국어+영어 OCR 사용")
            elif 'kor+eng' in available_langs:
                lang_config = 'kor+eng'
                print("한국어+영어 OCR 사용")
            else:
                lang_config = 'eng'
                print("영어 OCR 사용 (한국어 언어팩 없음)")
            
            # 여러 방법으로 OCR 시도
            results = []
            
            # 다양한 PSM 모드와 OEM 모드로 시도
            configs = [
                ('--psm 6 --oem 3', '단일 텍스트 블록 + LSTM'),
                ('--psm 4 --oem 3', '가변 크기 텍스트 + LSTM'),
                ('--psm 3 --oem 3', '자동 페이지 분할 + LSTM'),
                ('--psm 6 --oem 1', '단일 텍스트 블록 + Tesseract'),
            ]
            
            for method_name, processed_img in processed_images:
                for config, desc in configs:
                    try:
                        pil_img = Image.fromarray(processed_img)
                        text = pytesseract.image_to_string(pil_img, lang=lang_config, config=config)
                        if text.strip():
                            results.append((f"{method_name} ({desc})", text.strip()))
                    except Exception as e:
                        print(f"OCR 시도 실패 - {method_name} {desc}: {e}")
                        continue
            
            if not results:
                return "[OCR 결과: 텍스트를 인식할 수 없습니다]"
            
            # 가장 긴 결과 선택 (일반적으로 더 정확함)
            best_result = max(results, key=lambda x: len(x[1]))
            method, text = best_result
            
            print(f"OCR 방법별 결과:")
            for m, t in results[:5]:  # 상위 5개만 표시
                print(f"  {m}: {len(t)}자 - '{t[:50]}...'")
            print(f"선택된 방법: {method} ({len(text)}자)")
            
            return text if text else "[OCR 결과: 텍스트를 인식할 수 없습니다]"
            
        except pytesseract.TesseractNotFoundError:
            error_msg = "Tesseract가 설치되지 않았거나 경로가 설정되지 않았습니다."
            print(f"OCR 오류: {error_msg}")
            return f"[OCR 오류: {error_msg}]"
        except Exception as e:
            print(f"OCR 처리 중 오류 발생: {e}")
            return f"[OCR 오류: {e}]"
