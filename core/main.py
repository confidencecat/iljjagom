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
    def __init__(self, camera_source=0, mic=None, tts_enabled=False, tts_voice=None):
        self.conversation_file = "conversation/record.json"
        self.camera_source = camera_source
        self.initialize_records()
        

        self.ai_system = AISystem()
        self.inform_system = InformSystem()
        self.book_detector = BookDetector(inform_system=self.inform_system, camera_source=camera_source)

        # TTS flags
        self.tts_enabled = tts_enabled
        self.tts_voice = tts_voice

        # 전달받은 mic 값(None 또는 정수)을 VoiceSystem에 전달
        self.voice_system = VoiceSystem(input_device_index=mic)
        # propagate default voice to voice_system if provided
        if self.tts_voice:
            try:
                setattr(self.voice_system, 'default_tts_voice', self.tts_voice)
            except Exception:
                pass

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
    parser.add_argument('--conf_thres', type=float, default=0.7, help='감지 신뢰도 임계값 (기본값: 0.7)')
    parser.add_argument('--iou_thres', type=float, default=0.45, help='NMS IoU 임계값 (기본값: 0.45)')
    parser.add_argument('--max_det', type=int, default=1, help='이미지당 최대 감지 개수 (기본값: 1)')
    parser.add_argument('--classes', type=int, nargs='*', default=None, help='감지할 클래스 필터: --classes 0 또는 --classes 0 2 3')
    parser.add_argument('--agnostic_nms', action='store_true', help='클래스 무관 NMS 사용')
    parser.add_argument('--mic', type=int, default=-1, help='사용할 마이크 장치 번호 (기본값: -1, 시스템 기본 장치)')
    parser.add_argument('--tts', action='store_true', help='AI 응답이 생성되면 자동으로 TTS로 재생합니다')
    parser.add_argument('--tts-v', type=str, default=None, help='TTS 재생에 사용할 목소리 이름(예: alloy)')

    args = parser.parse_args()

    print(f"카메라 소스 설정: {args.source}")
    # mic: -1이면 시스템 기본 장치 사용 -> None 전달
    selected_mic = args.mic if args.mic is not None and args.mic >= 0 else None
    print(f"선택된 마이크 장치 번호: {args.mic} (내부 전달 값: {selected_mic})")

    app = MainApp(camera_source=args.source, mic=selected_mic)
    # propagate tts flags to app and voice system
    app.tts_enabled = args.tts
    app.tts_voice = args.tts_v
    if getattr(app, 'voice_system', None) and app.tts_voice:
        try:
            setattr(app.voice_system, 'default_tts_voice', app.tts_voice)
        except Exception:
            pass
    
    app.interface.detect_run_args = {
        'source': args.source,
        'conf_thres': args.conf_thres,
        'iou_thres': args.iou_thres,
        'max_det': args.max_det,
        'classes': args.classes,
        'agnostic_nms': args.agnostic_nms
    }
    app.interface.run()
