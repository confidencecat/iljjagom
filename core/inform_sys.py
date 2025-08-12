import os
import cv2
import sys
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
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class InformSystem:
    def __init__(self):
        self.image_dir = "conversation/image"
        self.ocr_dir = "conversation/ocr"
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.ocr_dir, exist_ok=True)
        
        self.clova_api_url = os.getenv("CLOVA_API_URL")
        self.clova_secret = os.getenv("CLOVA_SECRET_KEY")
        self.use_clova = bool(self.clova_api_url and self.clova_secret)
        
        if self.use_clova:
            print("Clova OCR 설정이 감지되었습니다.")
        else:
            #print("Clova OCR 설정이 없음. Tesseract OCR만 사용.")
            print("Clova OCR 설정이 없음. 프로그램을 종료.")
            sys.exit()

    def process_capture(self, capture_info):
        frame = capture_info['frame']
        bbox = capture_info['bbox']
        
        x1, y1, x2, y2 = bbox

        padding = 10#여백
        height, width = frame.shape[:2]
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(width, x2 + padding)
        y2 = min(height, y2 + padding)
        
        cropped_image = frame[y1:y2, x1:x2]
        
        crop_height, crop_width = cropped_image.shape[:2]
        if crop_height < 200 or crop_width < 200:
            print("이미지가 너무 작음.")
            # 다시 detect 시작하도록 설정 필요
            return None, None, None
                
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"capture_{timestamp}.jpg"
        image_path = os.path.join(self.image_dir, image_filename)
        
        cv2.imwrite(image_path, cropped_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"이미지 저장 완료: {image_path}")

        #ocr_text = self.perform_ocr(image_path)
        ocr_text = self.perform_clova_ocr(image_path)
        if ocr_text is None:
            return None, image_path, None

        ocr_filename = f"ocr_{timestamp}.txt"
        ocr_path = os.path.join(self.ocr_dir, ocr_filename)
        with open(ocr_path, 'w', encoding='utf-8') as f:
            f.write(ocr_text)
        print(f"OCR 결과 저장 완료: {ocr_path}")

        return ocr_text, image_path, ocr_path


    def perform_clova_ocr(self, image_path):
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
                            text = field.get("inferText", "")
                            if text.strip():
                                texts.append(text.strip())
                    
                    result_text = " ".join(texts)
                    print(f"Clova OCR 성공:\n{len(result_text)}자 추출")
                    return result_text if result_text.strip() else None
                else:
                    print(f"Clova OCR 실패:\n{response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"Clova OCR 오류:\n{e}")
            return None

    def perform_ocr(self, image_path):
        """
        # Clova OCR 시도
        if self.use_clova:
            print("Clova OCR 시도 중...")
            clova_result = self.perform_clova_ocr(image_path)
            if clova_result and len(clova_result.strip()) > 10:  # 충분한 텍스트가 인식되면
                return clova_result
            else:
                print("Clova OCR 결과가 부족합니다. Tesseract OCR로 전환...")
        
        # Tesseract OCR로 대체 처리
        print("Tesseract OCR 시도 중...")
        return self.perform_tesseract_ocr(image_path)
        """
        if self.use_clova:
            clova_result = self.perform_clova_ocr(image_path)
            if clova_result:
                return clova_result
            else:
                print("[No contents]")
                return None
        else:
            print(f"Clova OCR 사용 가능 : {self.use_clova}")
            return None



#================================안씀
"""def perform_tesseract_ocr(self, image_path):
        try:
            cv_image = cv2.imread(image_path)
            if cv_image is None:
                return "[OCR 오류: 이미지를 읽을 수 없습니다]"
            
            height, width = cv_image.shape[:2]
            if height < 100 or width < 100:
                scale_factor = max(100 / height, 100 / width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                cv_image = cv2.resize(cv_image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                print(f"이미지 크기 조정: {width}x{height} -> {new_width}x{new_height}")
            
            clahe_img = self.apply_clahe(cv_image)
            clahe_gray = cv2.cvtColor(clahe_img, cv2.COLOR_BGR2GRAY)
            
            pil_img = Image.fromarray(clahe_gray)
            
            available_langs = pytesseract.get_languages()
            lang_config = 'kor+eng' if 'kor' in available_langs else 'eng'
            print(f"Tesseract 언어 설정: {lang_config}")
            
            text = pytesseract.image_to_string(pil_img, lang=lang_config, config='--psm 6 --oem 3')
            
            if not text.strip():
                return "[OCR 결과: 텍스트를 인식할 수 없습니다]"
            
            print(f"Tesseract OCR 성공: {len(text.strip())}자 추출")
            return text.strip()
            
        except pytesseract.TesseractNotFoundError:
            error_msg = "Tesseract가 설치되지 않았거나 경로가 설정되지 않았습니다."
            print(f"OCR 오류: {error_msg}")
            return f"[OCR 오류: {error_msg}]"
        except Exception as e:
            print(f"OCR 처리 중 오류 발생: {e}")
            return f"[OCR 오류: {e}]"
"""

"""def apply_clahe(self, img):
        #CLAHE (Contrast Limited Adaptive Histogram Equalization) 적용
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        if len(img.shape) == 3:
            img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
            img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0])
            return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        else:
            return clahe.apply(img)"""