import os
import cv2
import numpy as np
from datetime import datetime
import pytesseract
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Tesseract-OCR의 설치 경로를 지정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class InformSystem:
    def __init__(self):
        self.image_dir = "conversation/image"
        self.ocr_dir = "conversation/ocr"
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.ocr_dir, exist_ok=True)

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

    def perform_ocr(self, image_path):
        try:
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
            
            # 적응적 이진화 (조명 조건에 더 강함)
            adaptive_thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # OTSU 이진화도 시도
            _, otsu_thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # PIL 이미지로 변환
            pil_adaptive = Image.fromarray(adaptive_thresh)
            pil_otsu = Image.fromarray(otsu_thresh)
            pil_original = Image.fromarray(gray)
            
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
                ('--psm 8 --oem 3', '단일 단어 + LSTM'),
            ]
            
            for config, desc in configs:
                # 1. 적응적 이진화 결과
                try:
                    text1 = pytesseract.image_to_string(pil_adaptive, lang=lang_config, config=config)
                    if text1.strip():
                        results.append((f"적응적 이진화 ({desc})", text1))
                except:
                    pass
                
                # 2. OTSU 이진화 결과
                try:
                    text2 = pytesseract.image_to_string(pil_otsu, lang=lang_config, config=config)
                    if text2.strip():
                        results.append((f"OTSU 이진화 ({desc})", text2))
                except:
                    pass
                
                # 3. 원본 그레이스케일
                try:
                    text3 = pytesseract.image_to_string(pil_original, lang=lang_config, config=config)
                    if text3.strip():
                        results.append((f"원본 그레이스케일 ({desc})", text3))
                except:
                    pass
            
            # 가장 긴 결과 선택 (일반적으로 더 정확함)
            best_result = max(results, key=lambda x: len(x[1].strip()))
            method, text = best_result
            
            print(f"OCR 방법별 결과:")
            for m, t in results:
                print(f"  {m}: {len(t.strip())}자 - '{t.strip()[:50]}...'")
            print(f"선택된 방법: {method} ({len(text.strip())}자)")
            
            return text.strip() if text.strip() else "[OCR 결과: 텍스트를 인식할 수 없습니다]"
            
        except pytesseract.TesseractNotFoundError:
            error_msg = "Tesseract가 설치되지 않았거나 경로가 설정되지 않았습니다."
            print(f"OCR 오류: {error_msg}")
            return f"[OCR 오류: {error_msg}]"
        except Exception as e:
            print(f"OCR 처리 중 오류 발생: {e}")
            return f"[OCR 오류: {e}]"
