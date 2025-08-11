import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
import json
from datetime import datetime
from core.interface import ReadAIInterface
from core.ai_system import AISystem
from core.detect_sys import BookDetector
from core.inform_sys import InformSystem
from core.voice_sys import VoiceSystem

class MainApp:
    def __init__(self, camera_source=0):
        self.conversation_file = "conversation/record.json"
        self.camera_source = camera_source
        self.initialize_records()

        # Initialize systems
        self.ai_system = AISystem()
        self.inform_system = InformSystem()
        self.book_detector = BookDetector(inform_system=self.inform_system, camera_source=camera_source)
        self.voice_system = VoiceSystem()
        
        self.interface = ReadAIInterface(
            ai_system=self.ai_system,
            book_detector=self.book_detector,
            voice_system=self.voice_system,
            main_app=self
        )

    def initialize_records(self):
        if not os.path.exists(self.conversation_file):
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump({"total_conversations": 0, "records": []}, f, indent=4)

    def run(self):
        self.interface.run()

    def save_conversation(self, user_prompt, edited_prompt, ai_response, image_path=None, ocr_path=None, voice_path=None):
        try:
            with open(self.conversation_file, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                
                new_record = {
                    "id": data["total_conversations"] + 1,
                    "timestamp": datetime.now().isoformat(),
                    "user_prompt": user_prompt,
                    "edited_prompt": edited_prompt,
                    "ai_response": ai_response,
                    "image_path": image_path,
                    "ocr_text_path": ocr_path,
                    "voice_path": voice_path
                }
                
                data["records"].append(new_record)
                data["total_conversations"] += 1
                
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.truncate()
        except Exception as e:
            print(f"대화 저장 오류 발생: {e}")


if __name__ == '__main__':
    import sys
    
    # 카메라 소스를 명령줄 인자로 받을 수 있도록 설정
    camera_source = 0
    if len(sys.argv) > 1:
        try:
            camera_source = int(sys.argv[1])
            print(f"카메라 소스 설정: {camera_source}")
        except ValueError:
            print(f"잘못된 카메라 소스: {sys.argv[1]}, 기본값 0 사용")
    
    app = MainApp(camera_source=camera_source)
    app.run()
