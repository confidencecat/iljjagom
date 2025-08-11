import pytesseract
from PIL import Image
import cv2
import numpy as np
import os

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def test_ocr_with_preprocessing(image_path):
    print(f"=== OCR 테스트: {image_path} ===")
    
    # 1. 원본 이미지로 OCR
    try:
        original_image = Image.open(image_path)
        print(f"이미지 크기: {original_image.size}")
        print(f"이미지 모드: {original_image.mode}")
        
        original_text = pytesseract.image_to_string(original_image, lang='eng')
        print(f"\n1. 원본 이미지 OCR 결과:")
        print(f"'{original_text.strip()}'")
        print(f"길이: {len(original_text.strip())} 문자")
        
    except Exception as e:
        print(f"원본 OCR 오류: {e}")
        return
    
    # 2. OpenCV로 전처리 후 OCR
    try:
        # OpenCV로 이미지 읽기
        cv_image = cv2.imread(image_path)
        if cv_image is None:
            print("OpenCV로 이미지를 읽을 수 없습니다.")
            return
            
        # 그레이스케일 변환
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # 이진화 (Thresholding)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # PIL 이미지로 변환
        pil_thresh = Image.fromarray(thresh)
        
        # 전처리된 이미지로 OCR
        processed_text = pytesseract.image_to_string(pil_thresh, lang='eng')
        print(f"\n2. 전처리 후 OCR 결과:")
        print(f"'{processed_text.strip()}'")
        print(f"길이: {len(processed_text.strip())} 문자")
        
        # 전처리된 이미지 저장 (확인용)
        cv2.imwrite('preprocessed_test.png', thresh)
        print("전처리된 이미지를 'preprocessed_test.png'로 저장했습니다.")
        
    except Exception as e:
        print(f"전처리 OCR 오류: {e}")
    
    # 3. 다양한 설정으로 OCR 시도
    try:
        print(f"\n3. 다양한 PSM 모드로 테스트:")
        
        # PSM 모드들
        psm_modes = [
            (6, "단일 텍스트 블록"),
            (7, "단일 텍스트 라인"),
            (8, "단일 단어"),
            (13, "원시 라인")
        ]
        
        for psm, desc in psm_modes:
            config = f'--psm {psm}'
            text = pytesseract.image_to_string(original_image, lang='eng', config=config)
            print(f"PSM {psm} ({desc}): '{text.strip()}'")
            
    except Exception as e:
        print(f"PSM 테스트 오류: {e}")

if __name__ == "__main__":
    test_ocr_with_preprocessing("test_book_page.png")
