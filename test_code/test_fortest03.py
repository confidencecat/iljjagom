import sys
import os
sys.path.append('..')

import cv2
import numpy as np
from PIL import Image
import pytesseract

# Tesseract 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def enhance_contrast_for_ocr_simple(image_path, output_dir="./fortest03"):
    """
    4가지 대조 향상 방법만 적용하는 간소화된 함수
    """
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 이미지 읽기
    image = cv2.imread(image_path)
    if image is None:
        print(f"이미지를 읽을 수 없습니다: {image_path}")
        return None
    
    # 그레이스케일 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    print(f"원본 이미지 크기: {gray.shape}")
    print(f"원본 이미지 픽셀 값 범위: {gray.min()} ~ {gray.max()}")
    
    # 4가지 방법만 적용
    methods = {}
    
    # 1. 원본
    methods['original'] = gray
    
    # 2. 히스토그램 평활화 (Histogram Equalization)
    hist_eq = cv2.equalizeHist(gray)
    methods['histogram_equalization'] = hist_eq
    
    # 3. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    clahe_result = clahe.apply(gray)
    methods['clahe'] = clahe_result
    
    # 4. 극단적 대조 (Extreme Contrast)
    mean_val = gray.mean()
    extreme_contrast = np.where(gray > mean_val, 255, 0).astype(np.uint8)
    methods['extreme_contrast'] = extreme_contrast
    
    # 결과 이미지들 저장
    saved_paths = {}
    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    for method_name, result_image in methods.items():
        output_path = os.path.join(output_dir, f"{base_filename}_{method_name}.png")
        cv2.imwrite(output_path, result_image)
        saved_paths[method_name] = output_path
        print(f"저장 완료: {output_path}")
    
    return saved_paths, methods

def perform_korean_ocr_only(image_path):
    """
    한국어만 인식하는 간소화된 OCR 함수
    """
    try:
        # 이미지 읽기
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 이미지 크기 확인 및 리사이징
        height, width = gray.shape
        if height < 100 or width < 100:
            gray = cv2.resize(gray, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
        
        # 노이즈 제거
        denoised = cv2.medianBlur(gray, 3)
        
        # PIL 이미지로 변환
        pil_image = Image.fromarray(denoised)
        
        # 한국어만 OCR 수행 (빠른 설정)
        text = pytesseract.image_to_string(pil_image, lang='kor', config='--psm 6')
        
        return text.strip()
        
    except Exception as e:
        print(f"OCR 오류: {e}")
        return f"[OCR 오류: {e}]"

def test_fortest03():
    """
    fortest03 이미지에 대한 간소화된 OCR 테스트
    """
    # fortest03.jpg 파일 찾기
    possible_paths = [
        "fortest03.jpg",
        "./fortest03.jpg", 
        "../fortest03.jpg",
        "./test_code/fortest03.jpg"
    ]
    
    image_path = None
    for path in possible_paths:
        if os.path.exists(path):
            image_path = path
            break
    
    if image_path is None:
        print("fortest03.jpg 파일을 찾을 수 없습니다.")
        print("현재 디렉토리:", os.getcwd())
        return
    
    print(f"=== fortest03 대조 향상 OCR 테스트: {image_path} ===")
    
    # 대조 향상 이미지들 생성
    saved_paths, enhanced_images = enhance_contrast_for_ocr_simple(image_path)
    
    if not saved_paths:
        print("이미지 처리 실패")
        return
    
    # 각 향상된 이미지에 대해 OCR 수행
    results = {}
    
    for method_name, image_path in saved_paths.items():
        print(f"\n--- {method_name} 한국어 OCR 테스트 ---")
        try:
            ocr_result = perform_korean_ocr_only(image_path)
            results[method_name] = {
                'text': ocr_result,
                'length': len(ocr_result.strip()),
                'path': image_path
            }
            print(f"추출된 텍스트 길이: {len(ocr_result.strip())} 문자")
            print(f"텍스트 미리보기: {ocr_result.strip()[:100]}...")
        except Exception as e:
            print(f"OCR 오류: {e}")
            results[method_name] = {
                'text': f"[오류: {e}]",
                'length': 0,
                'path': image_path
            }
    
    # 결과 분석 및 출력
    print(f"\n{'='*80}")
    print("fortest03 OCR 성능 비교 결과")
    print(f"{'='*80}")
    
    # 텍스트 길이 기준으로 정렬
    sorted_results = sorted(results.items(), key=lambda x: x[1]['length'], reverse=True)
    
    for i, (method, result) in enumerate(sorted_results, 1):
        print(f"{i:2d}. {method:20s} | {result['length']:4d}자 | {result['path']}")
    
    # 가장 좋은 결과 상세 출력
    best_method, best_result = sorted_results[0]
    print(f"\n{'='*80}")
    print(f"최고 성능: {best_method} ({best_result['length']}자)")
    print(f"{'='*80}")
    print(best_result['text'])
    print(f"{'='*80}")
    
    # 결과를 텍스트 파일로 저장
    result_file = "./fortest03/fortest03_ocr_results.txt"
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write("fortest03 OCR 성능 비교 결과\n")
        f.write("="*80 + "\n\n")
        
        for i, (method, result) in enumerate(sorted_results, 1):
            f.write(f"{i:2d}. {method:20s} | {result['length']:4d}자\n")
        
        f.write(f"\n최고 성능: {best_method} ({best_result['length']}자)\n")
        f.write("="*80 + "\n")
        f.write(best_result['text'])
        f.write("\n" + "="*80 + "\n\n")
        
        # 각 방법별 상세 결과
        for method, result in sorted_results:
            f.write(f"\n--- {method} ---\n")
            f.write(f"길이: {result['length']}자\n")
            f.write(f"파일: {result['path']}\n")
            f.write("내용:\n")
            f.write(result['text'])
            f.write("\n" + "-"*40 + "\n")
    
    print(f"\n결과 파일 저장: {result_file}")
    print(f"처리된 이미지들: ./fortest03/")
    
    return results, sorted_results

if __name__ == "__main__":
    test_fortest03()
