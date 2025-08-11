from PIL import Image, ImageDraw, ImageFont
import os

def create_korean_image():
    # 이미지 크기 설정
    width, height = 800, 1200
    
    # 흰 배경 이미지 생성
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 폰트 설정 시도
    font_size = 16
    title_font_size = 24
    
    try:
        # Windows 기본 한글 폰트 시도
        font_paths = [
            "C:/Windows/Fonts/malgun.ttf",  # 맑은 고딕
            "C:/Windows/Fonts/gulim.ttc",   # 굴림  
            "C:/Windows/Fonts/batang.ttc",  # 바탕
        ]
        
        font = None
        title_font = None
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    title_font = ImageFont.truetype(font_path, title_font_size)
                    print(f"한글 폰트 로드 성공: {font_path}")
                    break
                except:
                    continue
        
        if font is None:
            print("기본 폰트 사용")
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            
    except Exception as e:
        print(f"폰트 로드 오류: {e}")
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # 텍스트 내용
    y_position = 50
    
    # 제목
    draw.text((50, y_position), "한국어 문서 OCR 테스트", fill='black', font=title_font)
    y_position += 60
    
    # 본문
    korean_text = [
        "안녕하세요. 이것은 한국어 OCR 테스트를 위한 문서입니다.",
        "",
        "이 문서의 목적:",
        "• 한국어 텍스트 인식 정확도 측정",
        "• 다양한 한글 문장 구조 테스트", 
        "• 숫자와 한글의 혼합 텍스트 처리",
        "",
        "테스트 문장들:",
        "1. 가나다라마바사아자차카타파하",
        "2. 컴퓨터 과학과 인공지능 기술의 발전",
        "3. 2024년 현재 OCR 기술은 매우 발달했습니다.",
        "4. 특수문자: !@#$%^&*()_+-={}[]",
        "",
        "긴 문장 테스트:",
        "광화문 광장에서 열린 문화 행사에 많은 시민들이 참여했습니다.",
        "한국의 전통 음식인 김치, 불고기, 비빔밥은 세계적으로 유명합니다.",
        "교육과 기술의 융합으로 새로운 학습 방법이 개발되고 있습니다.",
        "",
        "숫자와 한글:",
        "서울특별시 인구: 약 970만명",
        "한국의 면적: 100,210 제곱킬로미터",
        "연도: 2024년 8월 11일",
        "",
        "혼합 문장:",
        "Python과 AI를 활용한 한국어 처리 기술 개발",
        "GitHub에서 오픈소스 프로젝트 contribute하기",
        "Machine Learning과 딥러닝의 차이점 분석",
        "",
        "끝."
    ]
    
    for line in korean_text:
        if y_position > height - 100:  # 페이지 하단 근처
            break
        draw.text((50, y_position), line, fill='black', font=font)
        y_position += 25
    
    # 이미지 저장
    filename = "korean_test_image.png"
    img.save(filename)
    print(f"한국어 테스트 이미지 생성 완료: {filename}")
    return filename

if __name__ == "__main__":
    create_korean_image()
