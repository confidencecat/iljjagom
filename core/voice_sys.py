import os
import time
import pyaudio
import wave
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class VoiceSystem:
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1, rate=44100):
        try:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            print(f"OpenAI 클라이언트 초기화 오류: {e}")
            self.client = None
        
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.start_time = None
        
        # 음성 파일 저장 디렉토리
        self.voice_dir = "conversation/voice"
        os.makedirs(self.voice_dir, exist_ok=True)

    def start_recording(self):
        if self.is_recording: 
            return
        
        try:
            self.frames = []
            self.stream = self.p.open(format=self.format, 
                                    channels=self.channels,
                                    rate=self.rate, 
                                    input=True,
                                    frames_per_buffer=self.chunk)
            self.is_recording = True
            self.start_time = time.time()
            print("녹음 시작.")
        except Exception as e:
            print(f"녹음 시작 오류: {e}")
            self.is_recording = False

    def record_chunk(self):
        """실시간으로 오디오 데이터를 수집"""
        if self.is_recording and self.stream:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"오디오 데이터 수집 오류: {e}")

    def stop_recording(self):
        if not self.is_recording: 
            return
        
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        print("녹음 정지.")

    def get_recording_status(self):
        """녹음 상태 정보 반환"""
        duration = time.time() - self.start_time if self.start_time else 0
        return {
            'is_recording': self.is_recording,
            'duration': duration,
            'frame_count': len(self.frames)
        }

    def finish_recording(self):
        """녹음 완료 및 STT 처리"""
        self.stop_recording()
        
        # 최소 녹음 시간 체크 (0.5초 이상)
        if len(self.frames) == 0:
            print("녹음된 데이터가 없습니다.")
            return "녹음된 데이터가 없습니다.", None
        
        duration = len(self.frames) * self.chunk / self.rate
        if duration < 0.5:
            print(f"녹음 시간이 너무 짧습니다: {duration:.2f}초")
            return "녹음 시간이 너무 짧습니다. 최소 0.5초 이상 녹음해주세요.", None
        
        # 타임스탬프로 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        voice_filename = f"voice_{timestamp}.wav"
        voice_path = os.path.join(self.voice_dir, voice_filename)
        
        try:
            # 음성 파일 저장
            wf = wave.open(voice_path, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            
            print(f"음성 파일 저장 완료: {voice_path} ({duration:.2f}초)")
            
            # STT 처리
            stt_result = self.speech_to_text(voice_path)
            return stt_result, voice_path
            
        except Exception as e:
            print(f"음성 파일 생성 오류: {e}")
            return f"음성 파일 생성 오류: {e}", None

    def speech_to_text(self, audio_path):
        if not self.client:
            return "STT 오류: OpenAI 클라이언트가 없습니다."
        
        try:
            # 파일 크기 확인
            file_size = os.path.getsize(audio_path)
            if file_size < 1000:  # 1KB 미만이면 너무 작음
                return "음성 파일이 너무 작습니다."
            
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ko"  # 한국어 지정
                )
            
            # 원본 파일은 삭제하지 않고 보존
            result = transcript.text.strip()
            print(f"STT 결과: {result}")
            return result if result else "음성을 인식할 수 없습니다."
            
        except Exception as e:
            print(f"STT 오류: {e}")
            return "음성 인식에 실패했습니다."

    def text_to_speech(self, text, output_path="response.mp3"):
        if not self.client:
            print("TTS 오류: OpenAI 클라이언트가 없습니다.")
            return
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text,
            )
            response.stream_to_file(output_path)
            print(f"TTS 파일 저장 완료: {output_path}")
        except Exception as e:
            print(f"TTS 오류: {e}")

    def cleanup(self):
        """리소스 정리"""
        self.stop_recording()
        if hasattr(self, 'p') and self.p:
            self.p.terminate()

    def __del__(self):
        self.cleanup()
