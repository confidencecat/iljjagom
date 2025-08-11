import pytesseract
from PIL import Image
import os

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 설치된 언어 확인
try:
    languages = pytesseract.get_languages()
    print('사용 가능한 언어:', languages)
    print('✅ Tesseract OCR이 정상적으로 설정되었습니다.')
except Exception as e:
    print(f'❌ 오류: {e}')
