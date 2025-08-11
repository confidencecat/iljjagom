import pygame
import sys
import os
from pathlib import Path

# --- UI 컴포넌트 ---

COLORS = {
    'WHITE': (255, 255, 255), 'BLACK': (0, 0, 0), 'GRAY': (128, 128, 128),
    'LIGHT_GRAY': (200, 200, 200), 'BLUE': (0, 100, 200), 'GREEN': (0, 150, 0),
    'RED': (200, 0, 0), 'DARK_BLUE': (0, 50, 100), 'DARK_GREEN': (0, 100, 0),
    'DARK_RED': (150, 0, 0)
}
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800

def get_korean_font(size):
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/NanumGothic.ttf",
        "C:/Windows/Fonts/gulim.ttc", "C:/Windows/Fonts/batang.ttc",
        "C:/Windows/Fonts/dotum.ttc",
    ]
    for font_path in font_paths:
        if Path(font_path).exists():
            return pygame.font.Font(font_path, size)
    print("경고: 한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
    return pygame.font.Font(None, size)

class Button:
    def __init__(self, x, y, width, height, text, color=COLORS['BLUE'], text_color=COLORS['WHITE'], font_size=28):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = get_korean_font(font_size)
        self.is_hovered = False

    def draw(self, screen):
        color = tuple(min(255, c + 30) for c in self.color) if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['BLACK'], self.rect, 2)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            return True
        return False

class TextInputBox:
    def __init__(self, x, y, width, height, font_size=20, editable=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text_lines = ['']
        self.font = get_korean_font(font_size)
        self.scroll_y = 0
        self.cursor_line, self.cursor_pos = 0, 0
        self.line_height = font_size + 10
        self.max_visible_lines = (height - 20) // self.line_height
        self.active = False
        self.editable = editable
        self.scrollbar_width = 20
        self.text_area_width = width - self.scrollbar_width - 20
        self.cursor_visible, self.cursor_timer = True, 0

    def _handle_keydown(self, event):
        if event.key == pygame.K_RETURN:
            current_line = self.text_lines[self.cursor_line]
            self.text_lines[self.cursor_line] = current_line[:self.cursor_pos]
            self.text_lines.insert(self.cursor_line + 1, current_line[self.cursor_pos:])
            self.cursor_line += 1
            self.cursor_pos = 0
        elif event.key == pygame.K_BACKSPACE:
            if self.cursor_pos > 0:
                current_line = self.text_lines[self.cursor_line]
                self.text_lines[self.cursor_line] = current_line[:self.cursor_pos-1] + current_line[self.cursor_pos:]
                self.cursor_pos -= 1
            elif self.cursor_line > 0:
                prev_line_len = len(self.text_lines[self.cursor_line - 1])
                self.text_lines[self.cursor_line - 1] += self.text_lines.pop(self.cursor_line)
                self.cursor_line -= 1
                self.cursor_pos = prev_line_len
        elif event.key == pygame.K_UP:
            if self.cursor_line > 0: self.cursor_line -= 1
        elif event.key == pygame.K_DOWN:
            if self.cursor_line < len(self.text_lines) - 1: self.cursor_line += 1
        self.cursor_pos = min(self.cursor_pos, len(self.text_lines[self.cursor_line]))

    def _handle_text_input(self, text):
        current_line = self.text_lines[self.cursor_line]
        new_line = current_line[:self.cursor_pos] + text + current_line[self.cursor_pos:]
        
        # 텍스트 너비 체크하여 자동 줄바꿈
        if self.font.size(new_line)[0] > self.text_area_width:
            # 현재 줄을 단어 단위로 분할하여 줄바꿈
            words = new_line.split(' ')
            lines = []
            current_line_text = ''
            
            for word in words:
                test_line = current_line_text + (' ' + word if current_line_text else word)
                if self.font.size(test_line)[0] <= self.text_area_width:
                    current_line_text = test_line
                else:
                    if current_line_text:
                        lines.append(current_line_text)
                        current_line_text = word
                    else:
                        # 단일 단어가 너무 긴 경우 강제 분할
                        while word and self.font.size(word)[0] > self.text_area_width:
                            split_pos = len(word) // 2
                            lines.append(word[:split_pos])
                            word = word[split_pos:]
                        current_line_text = word
            
            if current_line_text:
                lines.append(current_line_text)
            
            # 새로운 줄들로 교체
            self.text_lines[self.cursor_line:self.cursor_line+1] = lines
            self.cursor_line += len(lines) - 1
            self.cursor_pos = len(self.text_lines[self.cursor_line])
        else:
            self.text_lines[self.cursor_line] = new_line
            self.cursor_pos += len(text)
        
        # 커서가 화면 밖으로 나가면 스크롤
        if self.cursor_line >= self.scroll_y + self.max_visible_lines:
            self.scroll_y = self.cursor_line - self.max_visible_lines + 1

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = self.editable
                
                # 스크롤바 클릭 체크
                if (event.pos[0] >= self.rect.right - self.scrollbar_width and 
                    len(self.text_lines) > self.max_visible_lines):
                    # 스크롤바 영역 클릭
                    relative_y = event.pos[1] - self.rect.y
                    scroll_ratio = relative_y / self.rect.height
                    max_scroll = max(0, len(self.text_lines) - self.max_visible_lines)
                    self.scroll_y = int(scroll_ratio * max_scroll)
                    self.scroll_y = max(0, min(max_scroll, self.scroll_y))
                    return
                    
                # 텍스트 영역 클릭 시 커서 위치 설정
                if self.editable:
                    click_y = event.pos[1] - self.rect.y - 10
                    line_index = self.scroll_y + click_y // self.line_height
                    if 0 <= line_index < len(self.text_lines):
                        self.cursor_line = line_index
                        # 클릭한 위치에 가장 가까운 문자 위치 찾기
                        click_x = event.pos[0] - self.rect.x - 10
                        line_text = self.text_lines[self.cursor_line]
                        self.cursor_pos = 0
                        for i in range(len(line_text) + 1):
                            if self.font.size(line_text[:i])[0] >= click_x:
                                self.cursor_pos = max(0, i - 1) if i > 0 else 0
                                break
                        else:
                            self.cursor_pos = len(line_text)
            else:
                self.active = False
                
        if not self.active or not self.editable: 
            return

        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.TEXTINPUT:
            self._handle_text_input(event.text)
        elif event.type == pygame.MOUSEWHEEL:
            # 마우스 휠로 스크롤
            old_scroll = self.scroll_y
            self.scroll_y = max(0, min(len(self.text_lines) - self.max_visible_lines, 
                                     self.scroll_y - event.y * 3))  # 3줄씩 스크롤

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        # 텍스트 영역 그리기
        text_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width - self.scrollbar_width, self.rect.height)
        pygame.draw.rect(screen, COLORS['WHITE'], text_rect)
        pygame.draw.rect(screen, COLORS['BLACK'], text_rect, 2)
        
        # 텍스트 렌더링
        visible_lines = self.text_lines[self.scroll_y:self.scroll_y + self.max_visible_lines]
        for i, line in enumerate(visible_lines):
            y = self.rect.y + 10 + i * self.line_height
            if y + self.line_height <= self.rect.bottom - 10:  # 영역 내에서만 그리기
                text_surface = self.font.render(line, True, COLORS['BLACK'])
                screen.blit(text_surface, (self.rect.x + 10, y))
                
                # 커서 그리기
                if (self.active and self.cursor_visible and 
                    i + self.scroll_y == self.cursor_line):
                    cursor_x = self.rect.x + 10 + self.font.size(line[:self.cursor_pos])[0]
                    pygame.draw.line(screen, COLORS['BLACK'], 
                                   (cursor_x, y), (cursor_x, y + self.line_height - 2), 2)
        
        # 스크롤바 그리기 (필요한 경우에만)
        if len(self.text_lines) > self.max_visible_lines:
            scrollbar_rect = pygame.Rect(self.rect.right - self.scrollbar_width, self.rect.y, 
                                       self.scrollbar_width, self.rect.height)
            pygame.draw.rect(screen, COLORS['LIGHT_GRAY'], scrollbar_rect)
            pygame.draw.rect(screen, COLORS['BLACK'], scrollbar_rect, 1)
            
            # 스크롤 핸들
            total_lines = len(self.text_lines)
            handle_height = max(20, int(self.rect.height * self.max_visible_lines / total_lines))
            handle_y = (self.rect.y + 
                       int((self.rect.height - handle_height) * self.scroll_y / max(1, total_lines - self.max_visible_lines)))
            
            handle_rect = pygame.Rect(scrollbar_rect.x + 2, handle_y, 
                                    self.scrollbar_width - 4, handle_height)
            pygame.draw.rect(screen, COLORS['GRAY'], handle_rect)
            pygame.draw.rect(screen, COLORS['BLACK'], handle_rect, 1)

    def get_text(self): 
        return '\n'.join(self.text_lines)
    
    def set_text(self, text): 
        if not text:
            self.text_lines = ['']
            return
            
        # 텍스트를 줄바꿈으로 분할
        raw_lines = text.split('\n')
        self.text_lines = []
        
        for line in raw_lines:
            if not line:
                self.text_lines.append('')
                continue
                
            # 각 줄이 너무 길면 자동으로 줄바꿈
            words = line.split(' ')
            current_line = ''
            
            for word in words:
                test_line = current_line + (' ' + word if current_line else word)
                if self.font.size(test_line)[0] <= self.text_area_width:
                    current_line = test_line
                else:
                    if current_line:
                        self.text_lines.append(current_line)
                        current_line = word
                    else:
                        # 단일 단어가 너무 긴 경우 강제 분할
                        while word and self.font.size(word)[0] > self.text_area_width:
                            split_pos = max(1, len(word) * self.text_area_width // self.font.size(word)[0])
                            self.text_lines.append(word[:split_pos])
                            word = word[split_pos:]
                        if word:
                            current_line = word
            
            if current_line:
                self.text_lines.append(current_line)
        
        # 빈 리스트 방지
        if not self.text_lines:
            self.text_lines = ['']
            
        # 스크롤을 맨 위로 초기화
        self.scroll_y = 0
        self.cursor_line = 0
        self.cursor_pos = 0

# --- 메인 인터페이스 ---

class ReadAIInterface:
    def __init__(self, ai_system, book_detector, voice_system, main_app):
        pygame.init()
        os.environ['SDL_IME_SHOW_UI'] = '1'
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("일짜곰 - 도서 도움이")
        self.clock = pygame.time.Clock()
        self.font_large = get_korean_font(36)
        self.font_medium = get_korean_font(28)
        self.font_small = get_korean_font(20)
        self.ai_system, self.book_detector, self.voice_system, self.main_app = ai_system, book_detector, voice_system, main_app
        self.current_screen = "start"
        self.user_question, self.ai_response = "", ""
        self.setup_ui()

    def setup_ui(self):
        self.buttons = {
            'ask': Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "질문하기"),
            'exit': Button(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 40, "종료", COLORS['RED']),
            'text': Button(SCREEN_WIDTH//2 - 220, SCREEN_HEIGHT//2, 180, 50, "텍스트"),
            'voice': Button(SCREEN_WIDTH//2 + 40, SCREEN_HEIGHT//2, 180, 50, "음성", COLORS['GREEN']),
            'submit': Button(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT - 80, 100, 40, "완료"),
            'back': Button(50, SCREEN_HEIGHT - 80, 100, 40, "뒤로", COLORS['GRAY']),
            'v_start': Button(SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2, 100, 50, "시작", COLORS['GREEN']),
            'v_stop': Button(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2, 100, 50, "정지", COLORS['RED']),
            'v_complete': Button(SCREEN_WIDTH//2 + 80, SCREEN_HEIGHT//2, 100, 50, "완료"),
            'resp_ok': Button(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 40, "완료")
        }
        self.text_input = TextInputBox(50, 150, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 250)
        self.response_display = TextInputBox(50, 150, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 250, editable=False)

    def run(self):
        pygame.key.start_text_input()
        running = True
        while running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                self.handle_events(event)
            
            # 음성 녹음 중일 때 오디오 데이터 수집
            if (self.current_screen == "voice_input" and self.voice_system and 
                hasattr(self.voice_system, 'is_recording') and self.voice_system.is_recording):
                self.voice_system.record_chunk()
            
            if self.current_screen == "text_input": 
                self.text_input.update(dt)
            if self.current_screen == "response": 
                self.response_display.update(dt)
            
            self.draw_screen()
        pygame.quit()
        sys.exit()

    def handle_events(self, event):
        screen_handlers = {
            "start": self.handle_start, "question_method": self.handle_method,
            "text_input": self.handle_text, "voice_input": self.handle_voice,
            "response": self.handle_response
        }
        if self.current_screen in screen_handlers:
            screen_handlers[self.current_screen](event)

    def handle_start(self, event):
        if self.buttons['ask'].handle_event(event): self.current_screen = "question_method"
        if self.buttons['exit'].handle_event(event): pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_method(self, event):
        if self.buttons['text'].handle_event(event): self.current_screen = "text_input"
        if self.buttons['voice'].handle_event(event): self.current_screen = "voice_input"
        if self.buttons['back'].handle_event(event): self.current_screen = "start"

    def handle_text(self, event):
        self.text_input.handle_event(event)
        if self.buttons['submit'].handle_event(event):
            self.user_question = self.text_input.get_text()
            self.process_question()
        if self.buttons['back'].handle_event(event): self.current_screen = "question_method"

    def handle_voice(self, event):
        if self.buttons['v_start'].handle_event(event): self.voice_system.start_recording()
        if self.buttons['v_stop'].handle_event(event): self.voice_system.stop_recording()
        if self.buttons['v_complete'].handle_event(event):
            result = self.voice_system.finish_recording()
            if isinstance(result, tuple):
                self.user_question, self.voice_file_path = result
            else:
                self.user_question = result
                self.voice_file_path = None
            
            # STT 오류 검증
            if (self.user_question.startswith("[STT 오류:") or 
                self.user_question.startswith("STT 오류:") or
                self.user_question.startswith("음성") or
                "오류" in self.user_question):
                # 오류 메시지를 UI에 표시하고 다시 녹음 화면으로
                print(f"STT 오류 감지: {self.user_question}")
                return
            
            self.process_question()
        if self.buttons['back'].handle_event(event): self.current_screen = "question_method"

    def handle_response(self, event):
        # 응답 화면에서도 스크롤 가능하도록
        self.response_display.handle_event(event)
        if self.buttons['resp_ok'].handle_event(event): 
            # 화면 전환 시 초기화
            self.user_question = ""
            self.ai_response = ""
            if hasattr(self, 'voice_file_path'):
                self.voice_file_path = None
            # 텍스트 입력창 초기화
            self.text_input.set_text("")
            self.current_screen = "start"

    def process_question(self):
        needs_book = self.ai_system.judge_question(self.user_question)
        ocr_text, image_path, ocr_path = None, None, None
        
        if needs_book:
            self.current_screen = "ocr_guide"
            self.draw_screen()
            pygame.display.flip()
            
            capture_info = self.book_detector.run()
            if capture_info is None:
                # 카메라 감지가 실패하거나 중단된 경우
                print("책 감지가 중단되었습니다. 시작 화면으로 돌아갑니다.")
                self.current_screen = "start"
                return
            
            ocr_text, image_path, ocr_path = self.main_app.inform_system.process_capture(capture_info)
        
        edited_prompt = self.ai_system.create_prompt(self.user_question, ocr_text)
        self.ai_response = self.ai_system.get_response(edited_prompt)
        
        # 음성 파일 경로가 있는 경우 저장에 포함
        voice_path = getattr(self, 'voice_file_path', None)
        self.main_app.save_conversation(self.user_question, edited_prompt, self.ai_response, 
                                      image_path, ocr_path, voice_path)
        
        self.response_display.set_text(self.ai_response)
        self.current_screen = "response"

    def draw_screen(self):
        self.screen.fill(COLORS['WHITE'])
        draw_funcs = {
            "start": self.draw_start, "question_method": self.draw_method,
            "text_input": self.draw_text, "voice_input": self.draw_voice,
            "ocr_guide": self.draw_ocr, "response": self.draw_response
        }
        if self.current_screen in draw_funcs:
            draw_funcs[self.current_screen]()
        pygame.display.flip()

    def draw_title(self, text, y_pos):
        title = self.font_large.render(text, True, COLORS['BLACK'])
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, y_pos)))

    def draw_start(self):
        self.draw_title("일짜곰 - 도서 도움이", 200)
        self.buttons['ask'].draw(self.screen)
        self.buttons['exit'].draw(self.screen)

    def draw_method(self):
        self.draw_title("질문할 방법을 선택하세요", 200)
        self.buttons['text'].draw(self.screen)
        self.buttons['voice'].draw(self.screen)
        self.buttons['back'].draw(self.screen)

    def draw_text(self):
        self.draw_title("질문을 입력하세요", 100)
        self.text_input.draw(self.screen)
        self.buttons['submit'].draw(self.screen)
        self.buttons['back'].draw(self.screen)

    def draw_voice(self):
        self.draw_title("음성으로 질문하세요", 150)
        
        # 녹음 상태 표시
        if self.voice_system:
            status = self.voice_system.get_recording_status()
            
            if status['is_recording']:
                status_text = f"🎤 녹음 중... ({status['duration']:.1f}초)"
                status_color = COLORS['RED']
            else:
                status_text = "🎙️ 녹음 대기"
                status_color = COLORS['BLACK']
            
            status_surface = self.font_small.render(status_text, True, status_color)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(status_surface, status_rect)
            
            # 안내 문구
            guide_text = "최소 0.5초 이상 녹음해주세요"
            guide_surface = self.font_small.render(guide_text, True, COLORS['GRAY'])
            guide_rect = guide_surface.get_rect(center=(SCREEN_WIDTH//2, 230))
            self.screen.blit(guide_surface, guide_rect)
        
        self.buttons['v_start'].draw(self.screen)
        self.buttons['v_stop'].draw(self.screen)
        self.buttons['v_complete'].draw(self.screen)
        self.buttons['back'].draw(self.screen)

    def draw_ocr(self):
        self.draw_title("카메라에 책의 내용이 뜨도록 해주십시오", SCREEN_HEIGHT//2)
        text = self.font_small.render("5초 이상 감지되면 자동으로 캡처됩니다.", True, COLORS['GRAY'])
        self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))

    def draw_response(self):
        self.draw_title("AI 응답", 100)
        self.response_display.draw(self.screen)
        self.buttons['resp_ok'].draw(self.screen)
