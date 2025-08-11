import sys
import os
sys.path.append('.')

from core.inform_sys import InformSystem

# 개선된 OCR 시스템 테스트
inform_sys = InformSystem()

# 가장 최근 캡처 이미지로 테스트
image_path = "conversation/image/capture_20250811_134311.jpg"

print(f"=== 개선된 OCR 테스트: {image_path} ===")
result = inform_sys.perform_ocr(image_path)
print(f"\n최종 OCR 결과:")
print(f"'{result}'")
print(f"길이: {len(result)} 문자")
