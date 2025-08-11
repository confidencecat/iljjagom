import urllib.request
import ssl
import os

# SSL 인증서 확인 비활성화
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

url = 'https://github.com/tesseract-ocr/tessdata/raw/main/kor.traineddata'
target_path = r'C:\Program Files\Tesseract-OCR\tessdata\kor.traineddata'

try:
    print('한국어 언어팩 다운로드 중...')
    urllib.request.urlretrieve(url, target_path)
    print(f'다운로드 완료: {target_path}')
    print(f'파일 크기: {os.path.getsize(target_path)} bytes')
except Exception as e:
    print(f'다운로드 실패: {e}')
