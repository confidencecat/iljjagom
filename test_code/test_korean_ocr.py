import sys
import os
sys.path.append('.')

from core.inform_sys import InformSystem

# 개선된 OCR 시스템으로 test_book_page.png 테스트
inform_sys = InformSystem()

print("=== test_book_page.png로 한국어 OCR 테스트 ===")
result = inform_sys.perform_ocr("test_book_page.png")
print(f"\n최종 OCR 결과:")
print(f"'{result}'")
print(f"길이: {len(result)} 문자")
