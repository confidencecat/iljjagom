import pygame
import time
import sys
import os
from pathlib import Path
from datetime import datetime
import threading
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, BUTTON_FONT_SIZE, INPUT_FONT_SIZE


def get_korean_font(size):
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/NanumGothic.ttf",
        "C:/Windows/Fonts/gulim.ttc", "C:/Windows/Fonts/batang.ttc",
    ]
    for font_path in font_paths:
        if Path(font_path).exists():
            return pygame.font.Font(font_path, size)
    print("한글 폰트를 찾을 수 없어 기본 폰트를 사용.")
    return pygame.font.Font(None, size)

class Button:
    def __init__(self, x, y, width, height, text, color=COLORS['BLUE'], text_color=COLORS['WHITE'], font_size=BUTTON_FONT_SIZE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = get_korean_font(font_size)
        self.is_hovered = False
        self.color = color
        self.text_color = text_color

    def draw(self, screen):
        color = tuple(min(255, c + 30) for c in self.color) if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=24)
        pygame.draw.rect(screen, COLORS['BLACK'], self.rect, 2, border_radius=24)
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
    def __init__(self, x, y, width, height, font_size=INPUT_FONT_SIZE, editable=True):
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
        if not hasattr(self, '_desired_cursor_x'):
            self._desired_cursor_x = None

        if event.key == pygame.K_RETURN:
            current_line = self.text_lines[self.cursor_line]
            self.text_lines[self.cursor_line] = current_line[:self.cursor_pos]
            self.text_lines.insert(self.cursor_line + 1, current_line[self.cursor_pos:])
            self.cursor_line += 1
            self.cursor_pos = 0
            self._desired_cursor_x = None
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
            self._desired_cursor_x = None
        elif event.key == pygame.K_LEFT:
            if self.cursor_pos > 0: self.cursor_pos -= 1
            elif self.cursor_line > 0:
                self.cursor_line -= 1
                self.cursor_pos = len(self.text_lines[self.cursor_line])
            self._desired_cursor_x = None
        elif event.key == pygame.K_RIGHT:
            if self.cursor_pos < len(self.text_lines[self.cursor_line]): self.cursor_pos += 1
            elif self.cursor_line < len(self.text_lines) - 1:
                self.cursor_line += 1
                self.cursor_pos = 0
            self._desired_cursor_x = None
        elif event.key == pygame.K_UP:
            if self.cursor_line > 0:
                if self._desired_cursor_x is None:
                    line_text = self.text_lines[self.cursor_line][:self.cursor_pos]
                    self._desired_cursor_x = self.font.size(line_text)[0]
                self.cursor_line -= 1
                prev_line = self.text_lines[self.cursor_line]
                min_dist, best_pos = float('inf'), 0
                for i in range(len(prev_line)+1):
                    dist = abs(self.font.size(prev_line[:i])[0] - self._desired_cursor_x)
                    if dist < min_dist: min_dist, best_pos = dist, i
                self.cursor_pos = best_pos
        elif event.key == pygame.K_DOWN:
            if self.cursor_line < len(self.text_lines) - 1:
                if self._desired_cursor_x is None:
                    line_text = self.text_lines[self.cursor_line][:self.cursor_pos]
                    self._desired_cursor_x = self.font.size(line_text)[0]
                self.cursor_line += 1
                next_line = self.text_lines[self.cursor_line]
                min_dist, best_pos = float('inf'), 0
                for i in range(len(next_line)+1):
                    dist = abs(self.font.size(next_line[:i])[0] - self._desired_cursor_x)
                    if dist < min_dist: min_dist, best_pos = dist, i
                self.cursor_pos = best_pos
        else:
            self._desired_cursor_x = None

        if event.key not in (pygame.K_UP, pygame.K_DOWN):
            self._desired_cursor_x = None

    def _handle_text_input(self, text):
        # IndexError 방지: 커서가 줄 개수보다 크면 빈 줄 추가
        while self.cursor_line >= len(self.text_lines):
            self.text_lines.append('')
        current_line = self.text_lines[self.cursor_line]
        new_line = current_line[:self.cursor_pos] + text + current_line[self.cursor_pos:]
        if self.font.size(new_line)[0] > self.text_area_width:
            words, lines, current_line_text = new_line.split(' '), [], ''
            for word in words:
                test_line = current_line_text + (' ' + word if current_line_text else word)
                if self.font.size(test_line)[0] <= self.text_area_width:
                    current_line_text = test_line
                else:
                    if current_line_text: lines.append(current_line_text)
                    current_line_text = word
            if current_line_text: lines.append(current_line_text)
            self.text_lines[self.cursor_line:self.cursor_line+1] = lines
            self.cursor_line += len(lines) - 1
            self.cursor_pos = len(self.text_lines[self.cursor_line])
        else:
            self.text_lines[self.cursor_line] = new_line
            self.cursor_pos += len(text)
        if self.cursor_line >= self.scroll_y + self.max_visible_lines:
            self.scroll_y = self.cursor_line - self.max_visible_lines + 1

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = self.editable
                if (event.pos[0] >= self.rect.right - self.scrollbar_width and 
                    len(self.text_lines) > self.max_visible_lines):
                    relative_y = event.pos[1] - self.rect.y
                    scroll_ratio = relative_y / self.rect.height
                    max_scroll = max(0, len(self.text_lines) - self.max_visible_lines)
                    self.scroll_y = int(scroll_ratio * max_scroll)
                    self.scroll_y = max(0, min(max_scroll, self.scroll_y))
                    return
                click_y = event.pos[1] - self.rect.y - 10
                line_index = self.scroll_y + click_y // self.line_height
                if 0 <= line_index < len(self.text_lines):
                    self.cursor_line = line_index
                    click_x = event.pos[0] - self.rect.x - 10
                    line_text = self.text_lines[self.cursor_line]
                    min_dist, self.cursor_pos = float('inf'), 0
                    for i in range(len(line_text) + 1):
                        dist = abs(self.font.size(line_text[:i])[0] - click_x)
                        if dist < min_dist: min_dist, self.cursor_pos = dist, i
                else:
                    self.cursor_line = len(self.text_lines) - 1
                    self.cursor_pos = len(self.text_lines[self.cursor_line])
            else:
                self.active = False

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, min(len(self.text_lines) - self.max_visible_lines, self.scroll_y - event.y * 3))

        if not self.active or not self.editable: return
        if event.type == pygame.KEYDOWN: self._handle_keydown(event)
        elif event.type == pygame.TEXTINPUT: self._handle_text_input(event.text)

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        text_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width - self.scrollbar_width, self.rect.height)
        pygame.draw.rect(screen, COLORS['WHITE'], text_rect, border_radius=20)
        pygame.draw.rect(screen, COLORS['BLACK'], text_rect, 2, border_radius=20)

        visible_lines = self.text_lines[self.scroll_y:self.scroll_y + self.max_visible_lines]
        for i, line in enumerate(visible_lines):
            y = self.rect.y + 10 + i * self.line_height
            if y + self.line_height <= self.rect.bottom - 10:
                text_surface = self.font.render(line, True, COLORS['BLACK'])
                screen.blit(text_surface, (self.rect.x + 10, y))
                if (self.active and self.cursor_visible and i + self.scroll_y == self.cursor_line):
                    cursor_x = self.rect.x + 10 + self.font.size(line[:self.cursor_pos])[0]
                    pygame.draw.line(screen, COLORS['BLACK'], (cursor_x, y), (cursor_x, y + self.line_height - 2), 2)

        if len(self.text_lines) > self.max_visible_lines:
            scrollbar_rect = pygame.Rect(self.rect.right - self.scrollbar_width, self.rect.y, self.scrollbar_width, self.rect.height)
            pygame.draw.rect(screen, COLORS['LIGHT_GRAY'], scrollbar_rect, border_radius=12)
            pygame.draw.rect(screen, COLORS['BLACK'], scrollbar_rect, 1, border_radius=12)
            total_lines = len(self.text_lines)
            handle_height = max(20, int(self.rect.height * self.max_visible_lines / total_lines))
            max_scroll = max(1, total_lines - self.max_visible_lines)
            handle_y = (self.rect.y + int((self.rect.height - handle_height) * self.scroll_y / max_scroll))
            handle_rect = pygame.Rect(scrollbar_rect.x + 2, handle_y, self.scrollbar_width - 4, handle_height)
            pygame.draw.rect(screen, COLORS['GRAY'], handle_rect, border_radius=8)
            pygame.draw.rect(screen, COLORS['BLACK'], handle_rect, 1, border_radius=8)

    def get_text(self): return '\n'.join(self.text_lines)
    
    def set_text(self, text):
        if not text: self.text_lines = ['']; return
        raw_lines, self.text_lines = text.split('\n'), []
        for line in raw_lines:
            if not line: self.text_lines.append(''); continue
            words, current_line = line.split(' '), ''
            for word in words:
                test_line = current_line + (' ' + word if current_line else word)
                if self.font.size(test_line)[0] <= self.text_area_width:
                    current_line = test_line
                else:
                    if current_line: self.text_lines.append(current_line)
                    current_line = word
            if current_line: self.text_lines.append(current_line)
        if not self.text_lines: self.text_lines = ['']
        self.scroll_y, self.cursor_line, self.cursor_pos = 0, 0, 0

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
        self.current_screen, self.user_question, self.ai_response = "start", "", ""
        self.accumulated_stt_text = ""
        self._last_tts_path, self._auto_played = None, False
        self._tts_lock, self._tts_name_lock = threading.Lock(), threading.Lock()
        self._tts_counters = {}
        self.is_loading, self.loading_message, self._loading_tick = False, "", 0
        self.setup_ui()

    def _play_file(self, path):
        try:
            with self._tts_lock:
                pygame.mixer.init()
                for i in range(5):
                    try:
                        pygame.mixer.music.load(path)
                        pygame.mixer.music.play()
                        break
                    except Exception as e:
                        if i == 4: raise
                        time.sleep(0.2)
        except Exception as e: print(f"TTS 재생 오류(스레드): {e}")

    def _ensure_conversation_dir(self): os.makedirs('conversation/voice', exist_ok=True)

    def _reserve_next_tts_path(self):
        self._ensure_conversation_dir()
        today = datetime.now().strftime('%Y%m%d')
        prefix = f"tts_{today}_"
        with self._tts_name_lock:
            if today not in self._tts_counters:
                max_id = 0
                try:
                    for fname in os.listdir('conversation/voice'):
                        if fname.startswith(prefix) and fname.lower().endswith('.mp3'):
                            try: max_id = max(max_id, int(fname.replace(prefix, '').replace('.mp3', '')))
                            except Exception: continue
                except Exception: max_id = 0
                self._tts_counters[today] = max_id
            self._tts_counters[today] += 1
            return os.path.join('conversation/voice', f"{prefix}{self._tts_counters[today]:04d}.mp3")

    def _tts_worker(self, text, out_path):
        try:
            self.is_loading, self.loading_message = True, "TTS 생성중"
            tmp_path = out_path + ".tmp"
            if os.path.exists(out_path): self._last_tts_path = out_path; self._play_file(out_path); return
            generated = self.voice_system.text_to_speech(text, output_path=tmp_path)
            if not generated: return
            if generated != tmp_path: tmp_path = generated
            os.replace(tmp_path, out_path)
            self._last_tts_path = out_path
            self._play_file(out_path)
        except Exception as e: print(f"TTS 스레드 오류: {e}")
        finally: self.is_loading, self.loading_message = False, ""

    def start_process_question(self):
        if self.is_loading: return
        threading.Thread(target=self._process_question_worker, daemon=True).start()

    def _process_question_worker(self):
        try:
            needs_book = self.ai_system.judge_question(self.user_question)
            ocr_text, image_path, ocr_path = None, None, None
            if needs_book:
                self.current_screen = "ocr_guide"
                self.is_loading = False
                capture_info = self.book_detector.run()
                if capture_info is None: self.current_screen = "start"; return
                ocr_text, image_path, ocr_path = self.main_app.inform_system.process_capture(capture_info)
            self.is_loading, self.loading_message = True, "AI 응답 생성 중"
            edited_prompt = self.ai_system.create_prompt(self.user_question, ocr_text)
            self.ai_response = self.ai_system.get_response(edited_prompt)
            voice_path = getattr(self, 'voice_file_path', None)
            self.main_app.save_conversation(self.user_question, edited_prompt, self.ai_response, image_path, ocr_path, voice_path)
            self.response_display.set_text(self.ai_response)
            self.current_screen = "response"
            if getattr(self.main_app, 'tts_enabled', False) and self.ai_response and self.voice_system:
                threading.Thread(target=self._tts_worker, args=(self.ai_response, self._reserve_next_tts_path()), daemon=True).start()
        except Exception as e: 
            print(f"process_question 오류(스레드): {e}")
            self.ai_response = f"[AI 오류: {e}]"
            self.response_display.set_text(self.ai_response)
            self.current_screen = "response"
        finally: self.is_loading, self.loading_message = False, ""

    def start_finish_recording(self):
        if self.is_loading: return
        self.is_loading, self.loading_message = True, "STT 처리 중"
        threading.Thread(target=self._finish_recording_worker, daemon=True).start()

    def _finish_recording_worker(self):
        try:
            stt_result, self.voice_file_path = self.voice_system.finish_recording()
            if stt_result and not stt_result.startswith("[STT 오류:"):
                self.accumulated_stt_text += (" " + stt_result if self.accumulated_stt_text else stt_result)
                self.voice_stt_display.set_text(self.accumulated_stt_text)
            else:
                print(f"STT 오류 또는 빈 결과: {stt_result}")
        except Exception as e: print(f"finish_recording 오류(스레드): {e}")
        finally: self.is_loading, self.loading_message = False, ""

    def draw_loading(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLORS['LIGHT_BROWN'])
        self.screen.blit(overlay, (0,0))
        dots = "." * ((self._loading_tick // 10) % 4)
        msg = self.loading_message + dots
        surf = self.font_medium.render(msg, True, COLORS['WHITE'])
        rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(surf, rect)

    def setup_ui(self):
        self.buttons = {
            'ask': Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "질문하기", COLORS['BROWN']),
            'exit': Button(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 40, "종료", COLORS['RED_BROWN']),
            'text': Button(SCREEN_WIDTH//2 - 220, SCREEN_HEIGHT//2, 180, 50, "텍스트", COLORS['BROWN']),
            'voice': Button(SCREEN_WIDTH//2 + 40, SCREEN_HEIGHT//2, 180, 50, "음성", COLORS['BROWN']),
            'submit': Button(SCREEN_WIDTH - 160, SCREEN_HEIGHT - 80, 100, 40, "완료", COLORS['RED_BROWN']),
            'back': Button(60, SCREEN_HEIGHT - 80, 100, 40, "뒤로", COLORS['GRAY']),
            'v_start': Button(SCREEN_WIDTH//2 - 160, 150, 140, 50, "녹음 시작", COLORS['BROWN']),
            'v_stop': Button(SCREEN_WIDTH//2 + 20, 150, 140, 50, "녹음 중지", COLORS['BROWN']),
            'v_complete': Button(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 140, 40, "질문 완료", COLORS['RED_BROWN']),
            'resp_ok': Button(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 60, 100, 40, "완료", COLORS['RED_BROWN']),
            'tts_play': Button(SCREEN_WIDTH - 110, SCREEN_HEIGHT - 60, 100, 40, "듣기", COLORS['BROWN'])
        }
        self.text_input = TextInputBox(50, 150, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 250)
        self.response_display = TextInputBox(50, 150, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 250, editable=False)
        self.voice_stt_display = TextInputBox(50, 220, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 320, editable=False)

    def run(self):
        pygame.key.start_text_input()
        running = True
        while running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                self.handle_events(event)
            if (self.current_screen == "voice_input" and self.voice_system and self.voice_system.is_recording):
                self.voice_system.record_chunk()
            if self.current_screen == "text_input": self.text_input.update(dt)
            if self.current_screen == "response": self.response_display.update(dt)
            if self.is_loading: self._loading_tick = (self._loading_tick + 1) % 40
            self.draw_screen()
        pygame.quit()
        sys.exit()

    def handle_events(self, event):
        handlers = {"start": self.handle_start, "question_method": self.handle_method, "text_input": self.handle_text, "voice_input": self.handle_voice, "response": self.handle_response}
        if self.current_screen in handlers: handlers[self.current_screen](event)

    def handle_start(self, event):
        if self.buttons['ask'].handle_event(event): self.current_screen = "question_method"
        if self.buttons['exit'].handle_event(event): pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_method(self, event):
        if self.buttons['text'].handle_event(event): self.current_screen = "text_input"
        if self.buttons['voice'].handle_event(event): self.current_screen = "voice_input"; self.accumulated_stt_text = ""; self.voice_stt_display.set_text("")
        if self.buttons['back'].handle_event(event): self.current_screen = "start"

    def handle_text(self, event):
        self.text_input.handle_event(event)
        if self.buttons['submit'].handle_event(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            self.user_question = self.text_input.get_text()
            self.start_process_question()
        if self.buttons['back'].handle_event(event): self.current_screen = "question_method"

    def handle_voice(self, event):
        if self.buttons['v_start'].handle_event(event): self.voice_system.start_recording()
        if self.buttons['v_stop'].handle_event(event): self.start_finish_recording()
        if self.buttons['v_complete'].handle_event(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            if self.accumulated_stt_text:
                self.user_question = self.accumulated_stt_text
                self.start_process_question()
        if self.buttons['back'].handle_event(event): self.current_screen = "question_method"

    def handle_response(self, event):
        self.response_display.handle_event(event)
        if self.buttons['resp_ok'].handle_event(event):
            try: pygame.mixer.music.stop()
            except Exception: pass
            self.user_question, self.ai_response, self.accumulated_stt_text = "", "", ""
            if hasattr(self, 'voice_file_path'): self.voice_file_path = None
            self.text_input.set_text(""), self.voice_stt_display.set_text("")
            self.current_screen = "start"
        if 'tts_play' in self.buttons and self.buttons['tts_play'].handle_event(event):
            if self.ai_response and self.voice_system:
                if self._last_tts_path and os.path.exists(self._last_tts_path):
                    threading.Thread(target=self._play_file, args=(self._last_tts_path,), daemon=True).start()
                else:
                    threading.Thread(target=self._tts_worker, args=(self.ai_response, self._reserve_next_tts_path()), daemon=True).start()

    def draw_screen(self):
        self.screen.fill(COLORS['YELLOW'])
        draw_funcs = {"start": self.draw_start, "question_method": self.draw_method, "text_input": self.draw_text, "voice_input": self.draw_voice, "ocr_guide": self.draw_ocr, "response": self.draw_response}
        if self.current_screen in draw_funcs: draw_funcs[self.current_screen]()
        if getattr(self, 'is_loading', False): self.draw_loading()
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
        self.draw_title("음성으로 질문하세요", 100)
        status = self.voice_system.get_recording_status()
        status_text = f"🎤 녹음 중... ({status['duration']:.1f}초)" if status['is_recording'] else "🎙️ 녹음 대기"
        status_color = COLORS['RED'] if status['is_recording'] else COLORS['BLACK']
        status_surface = self.font_small.render(status_text, True, status_color)
        self.screen.blit(status_surface, status_surface.get_rect(center=(SCREEN_WIDTH//2, 205)))
        self.buttons['v_start'].draw(self.screen)
        self.buttons['v_stop'].draw(self.screen)
        
        self.voice_stt_display.draw(self.screen)

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
        if 'tts_play' in self.buttons: self.buttons['tts_play'].draw(self.screen)