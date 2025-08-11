from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
import os

# 한국어 PDF 생성
def create_korean_pdf():
    filename = "korean_test_document.pdf"
    
    # PDF 캔버스 생성
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # 기본 폰트 사용 (한국어 지원)
    try:
        # Windows 기본 한글 폰트 시도
        font_paths = [
            "C:/Windows/Fonts/malgun.ttf",  # 맑은 고딕
            "C:/Windows/Fonts/gulim.ttc",   # 굴림
            "C:/Windows/Fonts/batang.ttc",  # 바탕
        ]
        
        font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('Korean', font_path))
                    c.setFont('Korean', 12)
                    font_registered = True
                    print(f"한글 폰트 등록 성공: {font_path}")
                    break
                except:
                    continue
        
        if not font_registered:
            print("한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
            c.setFont('Helvetica', 12)
    except:
        c.setFont('Helvetica', 12)
    
    # 제목
    c.setFont('Korean' if font_registered else 'Helvetica', 18)
    c.drawString(50, height - 50, "한국어 문서 OCR 테스트")
    
    # 본문 내용
    c.setFont('Korean' if font_registered else 'Helvetica', 12)
    y_position = height - 100
    
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
        "4. 특수문자: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
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
        "끝."
    ]
    
    for line in korean_text:
        c.drawString(50, y_position, line)
        y_position -= 20
        if y_position < 50:  # 페이지 하단에 도달하면 새 페이지
            c.showPage()
            c.setFont('Korean' if font_registered else 'Helvetica', 12)
            y_position = height - 50
    
    c.save()
    print(f"한국어 PDF 생성 완료: {filename}")
    return filename

if __name__ == "__main__":
    create_korean_pdf()
