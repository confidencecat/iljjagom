import requests
import os

# 다른 미러에서 한국어 언어팩 다운로드 시도
urls = [
    "https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/kor.traineddata",
    "https://github.com/tesseract-ocr/tessdata/raw/4.00/kor.traineddata",
]

target_path = r'C:\Program Files\Tesseract-OCR\tessdata\kor.traineddata'

for i, url in enumerate(urls):
    try:
        print(f'시도 {i+1}: {url}')
        response = requests.get(url, verify=False, timeout=30)
        if response.status_code == 200:
            with open(target_path, 'wb') as f:
                f.write(response.content)
            print(f'다운로드 성공: {target_path}')
            print(f'파일 크기: {len(response.content)} bytes')
            break
    except Exception as e:
        print(f'실패: {e}')
        continue
else:
    print('모든 다운로드 시도가 실패했습니다.')
