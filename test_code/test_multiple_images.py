import sys
import os
sys.path.append('..')

import cv2
import numpy as np
from PIL import Image
from core.inform_sys import InformSystem
import shutil

def enhance_contrast_for_ocr(image_path, output_dir):
    """
    이미지의 대조를 강화하여 OCR 성능을 향상시키는 함수
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
    
    # 다양한 대조 향상 방법들
    methods = {}
    
    # 1. 히스토그램 평활화 (Histogram Equalization)
    hist_eq = cv2.equalizeHist(gray)
    methods['histogram_equalization'] = hist_eq
    
    # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    clahe_result = clahe.apply(gray)
    methods['clahe'] = clahe_result
    
    # 3. 감마 보정 (Gamma Correction) - 밝게
    gamma_bright = 0.5  # 낮은 값으로 밝게
    gamma_table_bright = np.array([((i / 255.0) ** gamma_bright) * 255 for i in np.arange(0, 256)]).astype("uint8")
    gamma_bright_result = cv2.LUT(gray, gamma_table_bright)
    methods['gamma_bright'] = gamma_bright_result
    
    # 4. 감마 보정 (Gamma Correction) - 어둡게
    gamma_dark = 1.5  # 높은 값으로 어둡게
    gamma_table_dark = np.array([((i / 255.0) ** gamma_dark) * 255 for i in np.arange(0, 256)]).astype("uint8")
    gamma_dark_result = cv2.LUT(gray, gamma_table_dark)
    methods['gamma_dark'] = gamma_dark_result
    
    # 5. 대조 스트레칭 (Contrast Stretching)
    min_val, max_val = gray.min(), gray.max()
    contrast_stretched = ((gray - min_val) / (max_val - min_val) * 255).astype(np.uint8)
    methods['contrast_stretching'] = contrast_stretched
    
    # 6. 적응적 이진화 (Adaptive Thresholding)
    adaptive_mean = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    methods['adaptive_mean'] = adaptive_mean
    
    adaptive_gaussian = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    methods['adaptive_gaussian'] = adaptive_gaussian
    
    # 7. OTSU 이진화
    _, otsu_binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    methods['otsu_binary'] = otsu_binary
    
    # 8. 모폴로지 연산 후 대조 향상
    kernel = np.ones((2,2), np.uint8)
    morph_close = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    morph_enhanced = cv2.equalizeHist(morph_close)
    methods['morphology_enhanced'] = morph_enhanced
    
    # 9. 언샤프 마스킹 (Unsharp Masking)
    gaussian_blur = cv2.GaussianBlur(gray, (0, 0), 2.0)
    unsharp_mask = cv2.addWeighted(gray, 1.5, gaussian_blur, -0.5, 0)
    methods['unsharp_mask'] = unsharp_mask
    
    # 10. 극단적 대조 (Extreme Contrast)
    mean_val = gray.mean()
    extreme_contrast = np.where(gray > mean_val, 255, 0).astype(np.uint8)
    methods['extreme_contrast'] = extreme_contrast
    
    # 결과 이미지들 저장
    saved_paths = {}
    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # 원본도 저장
    original_path = os.path.join(output_dir, f"{base_filename}_original.png")
    cv2.imwrite(original_path, gray)
    saved_paths['original'] = original_path
    
    for method_name, result_image in methods.items():
        output_path = os.path.join(output_dir, f"{base_filename}_{method_name}.png")
        cv2.imwrite(output_path, result_image)
        saved_paths[method_name] = output_path
        print(f"저장 완료: {output_path}")
    
    return saved_paths, methods

def test_enhanced_ocr_with_results_folder(image_path, results_folder):
    """
    대조 향상된 이미지들로 OCR 테스트 수행하고 결과를 특정 폴더에 저장
    """
    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    enhanced_images_dir = os.path.join(results_folder, "enhanced_images")
    
    print(f"=== {base_filename} 대조 향상 OCR 테스트 ===")
    
    # 대조 향상 이미지들 생성
    saved_paths, enhanced_images = enhance_contrast_for_ocr(image_path, enhanced_images_dir)
    
    if not saved_paths:
        print("이미지 처리 실패")
        return
    
    # OCR 시스템 초기화
    inform_sys = InformSystem()
    
    # 각 향상된 이미지에 대해 OCR 수행
    results = {}
    
    print(f"\n{base_filename} OCR 테스트 시작...")
    for method_name, image_path in saved_paths.items():
        print(f"\n--- {method_name} OCR 테스트 ---")
        try:
            ocr_result = inform_sys.perform_ocr(image_path)
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
    
    # 결과 분석 및 저장
    sorted_results = sorted(results.items(), key=lambda x: x[1]['length'], reverse=True)
    
    # 결과를 텍스트 파일로 저장
    results_file = os.path.join(results_folder, f"{base_filename}_ocr_results.txt")
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write(f"{'='*80}\n")
        f.write(f"{base_filename} OCR 성능 비교 결과\n")
        f.write(f"{'='*80}\n\n")
        
        # 성능 순위
        for i, (method, result) in enumerate(sorted_results, 1):
            f.write(f"{i:2d}. {method:20s} | {result['length']:4d}자 | {result['path']}\n")
        
        # 가장 좋은 결과 상세 출력
        best_method, best_result = sorted_results[0]
        f.write(f"\n{'='*80}\n")
        f.write(f"최고 성능: {best_method} ({best_result['length']}자)\n")
        f.write(f"{'='*80}\n")
        f.write(best_result['text'])
        f.write(f"\n{'='*80}\n")
    
    print(f"결과 저장 완료: {results_file}")
    
    # 비교 격자 이미지 생성
    comparison_path = create_comparison_image(enhanced_images, 
                                            os.path.join(results_folder, f"{base_filename}_comparison_grid.png"))
    
    # 콘솔에도 출력
    print(f"\n{'='*80}")
    print(f"{base_filename} OCR 성능 비교 결과")
    print(f"{'='*80}")
    
    for i, (method, result) in enumerate(sorted_results, 1):
        print(f"{i:2d}. {method:20s} | {result['length']:4d}자")
    
    best_method, best_result = sorted_results[0]
    print(f"\n최고 성능: {best_method} ({best_result['length']}자)")
    
    return results, sorted_results

def create_comparison_image(enhanced_images, output_path):
    """
    처리된 이미지들을 격자로 배열한 비교 이미지 생성
    """
    if not enhanced_images:
        return None
        
    # 이미지 크기 확인
    sample_image = list(enhanced_images.values())[0]
    h, w = sample_image.shape
    
    # 격자 크기 계산 (4x3 격자)
    rows, cols = 3, 4
    grid_h, grid_w = h * rows, w * cols
    
    # 빈 격자 이미지 생성
    grid_image = np.ones((grid_h, grid_w), dtype=np.uint8) * 255
    
    # 이미지들을 격자에 배치
    methods = list(enhanced_images.keys())
    for i, method in enumerate(methods[:12]):  # 최대 12개
        row = i // cols
        col = i % cols
        
        y1, y2 = row * h, (row + 1) * h
        x1, x2 = col * w, (col + 1) * w
        
        grid_image[y1:y2, x1:x2] = enhanced_images[method]
        
        # 메서드 이름을 이미지에 추가
        cv2.putText(grid_image, method[:15], (x1 + 10, y1 + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    
    # 비교 이미지 저장
    cv2.imwrite(output_path, grid_image)
    print(f"비교 이미지 저장: {output_path}")
    
    return output_path

def test_multiple_images():
    """
    fortest01, fortest02 이미지들에 대해 테스트 수행
    """
    # 테스트할 이미지들
    test_images = [
        ("fortest01.png", "./test_code/fortest01"),
        ("fortest01.jpg", "./test_code/fortest01"),
        ("fortest02.png", "./test_code/fortest02"),
        ("fortest02.jpg", "./test_code/fortest02"),
    ]
    
    base_dir = "./test_code"
    
    for image_name, results_folder in test_images:
        image_path = os.path.join(base_dir, image_name)
        
        # 이미지 파일 존재 확인
        if not os.path.exists(image_path):
            print(f"이미지를 찾을 수 없습니다: {image_path}")
            # 상위 디렉토리에서도 찾아보기
            parent_image_path = os.path.join("..", image_name)
            if os.path.exists(parent_image_path):
                image_path = parent_image_path
                print(f"상위 디렉토리에서 발견: {image_path}")
            else:
                print(f"상위 디렉토리에도 없음: {parent_image_path}")
                continue
        
        # 결과 폴더 생성
        os.makedirs(results_folder, exist_ok=True)
        
        print(f"\n{'#'*100}")
        print(f"테스트 시작: {image_name}")
        print(f"결과 저장 위치: {results_folder}")
        print(f"{'#'*100}")
        
        try:
            # 대조 향상 OCR 테스트 실행
            results, sorted_results = test_enhanced_ocr_with_results_folder(image_path, results_folder)
            
            print(f"\n{image_name} 테스트 완료!")
            print(f"결과 파일들:")
            print(f"  - 향상된 이미지들: {results_folder}/enhanced_images/")
            print(f"  - OCR 결과: {results_folder}/*_ocr_results.txt")
            print(f"  - 비교 격자: {results_folder}/*_comparison_grid.png")
            
        except Exception as e:
            print(f"테스트 실패: {image_name} - {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 현재 디렉토리 확인
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    print(f"test_code 폴더 내용:")
    
    try:
        for item in os.listdir("./test_code"):
            print(f"  {item}")
    except:
        print("  test_code 폴더에 접근할 수 없습니다.")
    
    # 상위 디렉토리 확인
    print(f"\n상위 디렉토리 내용:")
    try:
        for item in os.listdir(".."):
            if item.lower().startswith('fortest'):
                print(f"  {item}")
    except:
        print("  상위 디렉토리에 접근할 수 없습니다.")
    
    # 다중 이미지 테스트 실행
    test_multiple_images()
