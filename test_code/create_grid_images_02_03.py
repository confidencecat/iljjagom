import cv2
import numpy as np
import os
from pathlib import Path

def apply_histogram_equalization(img):
    """히스토그램 평활화 적용"""
    if len(img.shape) == 3:
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    else:
        return cv2.equalizeHist(img)

def apply_clahe(img):
    """CLAHE 적용"""
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    if len(img.shape) == 3:
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0])
        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    else:
        return clahe.apply(img)

def apply_extreme_contrast(img):
    """극대 대조 적용"""
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img.copy()
    
    # 극대 대조 변환
    alpha = 3.0  # 대조도 증가
    beta = -100  # 밝기 감소
    enhanced = cv2.convertScaleAbs(img_gray, alpha=alpha, beta=beta)
    
    if len(img.shape) == 3:
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    else:
        return enhanced

def add_text_to_image(img, text, position=(10, 30)):
    """이미지에 텍스트 추가"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    color = (0, 0, 255)  # 빨간색
    thickness = 3
    
    # 텍스트 배경을 위한 사각형 그리기
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    cv2.rectangle(img, (position[0]-5, position[1]-text_size[1]-10), 
                  (position[0]+text_size[0]+5, position[1]+5), (255, 255, 255), -1)
    
    cv2.putText(img, text, position, font, font_scale, color, thickness)
    return img

def create_grid_image(image_path, output_dir):
    """단일 이미지에 대한 4x1 그리드 이미지 생성"""
    print(f"=== {os.path.basename(image_path)} 그리드 이미지 생성 ===")
    
    # 이미지 로드
    img = cv2.imread(image_path)
    if img is None:
        print(f"이미지를 로드할 수 없습니다: {image_path}")
        return None
    
    print(f"원본 이미지 크기: {img.shape[:2]}")
    
    # 각 전처리 방법 적용
    img_original = img.copy()
    img_hist = apply_histogram_equalization(img.copy())
    img_clahe = apply_clahe(img.copy())
    img_extreme = apply_extreme_contrast(img.copy())
    
    # 텍스트 라벨 추가
    img_original = add_text_to_image(img_original, "Original")
    img_hist = add_text_to_image(img_hist, "Histogram Eq.")
    img_clahe = add_text_to_image(img_clahe, "CLAHE")
    img_extreme = add_text_to_image(img_extreme, "Extreme Contrast")
    
    # 이미지 크기 조정 (메모리 절약을 위해)
    target_height = 800
    scale = target_height / img.shape[0]
    target_width = int(img.shape[1] * scale)
    
    img_original = cv2.resize(img_original, (target_width, target_height))
    img_hist = cv2.resize(img_hist, (target_width, target_height))
    img_clahe = cv2.resize(img_clahe, (target_width, target_height))
    img_extreme = cv2.resize(img_extreme, (target_width, target_height))
    
    # 가로로 연결하여 그리드 생성
    grid_image = np.hstack([img_original, img_hist, img_clahe, img_extreme])
    
    # 출력 파일명 생성
    base_name = Path(image_path).stem
    output_path = os.path.join(output_dir, f"{base_name}_enhancement_grid.jpg")
    
    # 저장
    cv2.imwrite(output_path, grid_image)
    print(f"그리드 이미지 저장: {output_path}")
    print(f"그리드 이미지 크기: {grid_image.shape}")
    
    return output_path

def main():
    """fortest02와 fortest03에 대한 그리드 이미지 생성"""
    
    # 입력 이미지 경로들
    images = [
        "../fortest02.jpg",
        "../fortest03.jpg"
    ]
    
    # 출력 디렉토리 생성
    output_dir = "./grid_images"
    os.makedirs(output_dir, exist_ok=True)
    
    print("fortest02, fortest03 그리드 이미지 생성 시작")
    print("=" * 60)
    
    created_grids = []
    
    for image_path in images:
        if os.path.exists(image_path):
            grid_path = create_grid_image(image_path, output_dir)
            if grid_path:
                created_grids.append(grid_path)
        else:
            print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
    
    print("\n" + "=" * 60)
    print("그리드 이미지 생성 완료!")
    print("생성된 파일들:")
    for grid_path in created_grids:
        print(f"  - {grid_path}")
    
    print("\n각 그리드는 다음 순서로 배열되어 있습니다:")
    print("  [원본] [히스토그램 평활화] [CLAHE] [극대 대조]")

if __name__ == "__main__":
    main()
