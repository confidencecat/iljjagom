import sys
import os
sys.path.append('.')

from pdf2image import convert_from_path
from core.inform_sys import InformSystem
import tempfile

def test_korean_pdf_ocr():
    pdf_path = "korean_test_document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return
    
    print(f"=== 한국어 PDF OCR 테스트: {pdf_path} ===")
    
    try:
        # PDF를 이미지로 변환 (poppler 없이 시도)
        try:
            pages = convert_from_path(pdf_path, dpi=300)
            print(f"PDF 변환 성공: {len(pages)} 페이지")
        except Exception as e:
            print(f"PDF 변환 실패 (poppler 필요할 수 있음): {e}")
            # 대신 PIL로 직접 열어보기
            from PIL import Image
            try:
                img = Image.open(pdf_path)
                pages = [img]
                print("PIL로 직접 이미지 열기 성공")
            except:
                print("PDF 처리 실패. 수동으로 이미지 변환이 필요합니다.")
                return
        
        # 첫 번째 페이지를 임시 이미지로 저장
        temp_image_path = "temp_korean_page.png"
        pages[0].save(temp_image_path, 'PNG')
        print(f"임시 이미지 저장: {temp_image_path}")
        
        # OCR 테스트
        inform_sys = InformSystem()
        result = inform_sys.perform_ocr(temp_image_path)
        
        print(f"\n=== OCR 결과 ===")
        print(f"추출된 텍스트 길이: {len(result)} 문자")
        print(f"결과:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # 임시 파일 삭제
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
            print(f"임시 파일 삭제: {temp_image_path}")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    test_korean_pdf_ocr()
