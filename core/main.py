import sys
import os


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
    import argparse

    parser = argparse.ArgumentParser(description="일짜곰 메인 애플리케이션")
    parser.add_argument('--source', type=int, default=0, help='카메라 소스 인덱스 (기본값: 0)')
    parser.add_argument('--conf_thres', type=float, default=0.6, help='감지 신뢰도 임계값 (기본값: 0.6)')
    parser.add_argument('--iou_thres', type=float, default=0.45, help='NMS IoU 임계값 (기본값: 0.45)')
    parser.add_argument('--max_det', type=int, default=1, help='이미지당 최대 감지 개수 (기본값: 1)')
    parser.add_argument('--classes', type=int, nargs='*', default=None, help='감지할 클래스 필터: --classes 0 또는 --classes 0 2 3')
    parser.add_argument('--agnostic_nms', action='store_true', help='클래스 무관 NMS 사용')

    args = parser.parse_args()

    print(f"카메라 소스 설정: {args.source}")

    app = MainApp(camera_source=args.source)
    
    app.interface.detect_run_args = {
        'source': args.source,
        'conf_thres': args.conf_thres,
        'iou_thres': args.iou_thres,
        'max_det': args.max_det,
        'classes': args.classes,
        'agnostic_nms': args.agnostic_nms
    }
    app.interface.run()
