import sys
import os
sys.path.append('.')

from core.inform_sys import InformSystem

def test_pure_korean_ocr():
    image_path = "korean_test_image.png"
    
    if not os.path.exists(image_path):
        print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        return
    
    print(f"=== 순수 한국어 OCR 테스트: {image_path} ===")
    
    # OCR 테스트
    inform_sys = InformSystem()
    result = inform_sys.perform_ocr(image_path)
    
    print(f"\n=== OCR 결과 ===")
    print(f"추출된 텍스트 길이: {len(result)} 문자")
    print(f"결과:")
    print("-" * 80)
    print(result)
    print("-" * 80)
    
    # 원본 텍스트와 비교
    original_text = """한국어 문서 OCR 테스트

안녕하세요. 이것은 한국어 OCR 테스트를 위한 문서입니다.

이 문서의 목적:
• 한국어 텍스트 인식 정확도 측정
• 다양한 한글 문장 구조 테스트
• 숫자와 한글의 혼합 텍스트 처리

테스트 문장들:
1. 가나다라마바사아자차카타파하
2. 컴퓨터 과학과 인공지능 기술의 발전
3. 2024년 현재 OCR 기술은 매우 발달했습니다.
4. 특수문자: !@#$%^&*()_+-={}[]

긴 문장 테스트:
광화문 광장에서 열린 문화 행사에 많은 시민들이 참여했습니다.
한국의 전통 음식인 김치, 불고기, 비빔밥은 세계적으로 유명합니다.
교육과 기술의 융합으로 새로운 학습 방법이 개발되고 있습니다.

숫자와 한글:
서울특별시 인구: 약 970만명
한국의 면적: 100,210 제곱킬로미터
연도: 2024년 8월 11일

혼합 문장:
Python과 AI를 활용한 한국어 처리 기술 개발
GitHub에서 오픈소스 프로젝트 contribute하기
Machine Learning과 딥러닝의 차이점 분석

끝."""
    
    print(f"\n=== 원본 텍스트 (비교용) ===")
    print(f"원본 텍스트 길이: {len(original_text)} 문자")
    print("-" * 80)
    print(original_text)
    print("-" * 80)
    
    # 간단한 정확도 분석
    original_lines = [line.strip() for line in original_text.split('\n') if line.strip()]
    result_lines = [line.strip() for line in result.split('\n') if line.strip()]
    
    print(f"\n=== 간단 분석 ===")
    print(f"원본 줄 수: {len(original_lines)}")
    print(f"인식된 줄 수: {len(result_lines)}")
    print(f"텍스트 길이 비교: 원본 {len(original_text)}자 vs 인식 {len(result)}자")

if __name__ == "__main__":
    test_pure_korean_ocr()
