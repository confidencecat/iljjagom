

COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GRAY': (180, 180, 180),
    'LIGHT_GRAY': (212, 199, 180),
    'BLUE': (70, 130, 180),
    'GREEN': (60, 179, 113),
    'RED': (220, 80, 80),
    'YELLOW': (255, 244, 199),  # 더 진한 노란색 배경
    'BROWN': (209, 165, 100),    # 버튼용 갈색
    'LIGHT_BROWN': (222, 185, 133), # 오버레이용 연한 갈색
    'RED_BROWN': (186, 99, 71),  # 완료 버튼용 붉은 연한 갈색
    'DARK_BLUE': (0, 50, 100),
    'DARK_GREEN': (0, 100, 0),
    'DARK_RED': (150, 0, 0)
}

print(COLORS)

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800

BUTTON_FONT_SIZE = 28
INPUT_FONT_SIZE = 20

CONFIG_JUDGE_FINE_TUNING = [
    ["이 책에서 말하는 사랑의 정의는 뭐야?", "True"],
    ["이 부분의 의미를 설명해줘.", "True"],
    ["책의 저자에 대해 알려줘.", "False"],
    ["등장인물들의 관계를 요약해줄래?", "True"],
    ["오늘 날씨 어때?", "False"],
    ["이 책의 다음 장 내용을 예측해줘.", "True"],
    ["'데미안'이라는 책 알아?", "False"],
    ["이 문단에서 작가가 말하고자 하는 바가 뭐야?", "True"]
]