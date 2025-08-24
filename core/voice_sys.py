import os
import time
import pyaudio
import wave
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class VoiceSystem:
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1, rate=44100, input_device_index=None):
        try:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            print(f"OpenAI 클라이언트 초기화 오류: {e}")
            self.client = None

        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        # 사용자가 지정한 입력 장치 인덱스 (None이면 시스템 기본 장치)
        self.input_device_index = input_device_index
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
            # 장치의 권장 샘플레이트/채널을 사용하도록 조정
            self.frames = []

            # 시도: 장치 정보에서 샘플레이트/채널을 가져온다. 실패하면 현재 설정을 사용.
            try:
                device_info = None
                if self.input_device_index is not None:
                    device_info = self.p.get_device_info_by_index(self.input_device_index)
                else:
                    # 시스템 기본 입력 장치 정보 시도
                    try:
                        device_info = self.p.get_default_input_device_info()
                    except Exception:
                        # 기본 장치 조회 실패 시, 입력을 지원하는 첫 장치를 찾음
                        for i in range(self.p.get_device_count()):
                            di = self.p.get_device_info_by_index(i)
                            if int(di.get('maxInputChannels', 0)) > 0:
                                device_info = di
                                break

                if device_info:
                    # 입력을 지원하는 장치인지 확인
                    max_in = int(device_info.get('maxInputChannels', 0))
                    if max_in <= 0:
                        raise RuntimeError(f"선택한 장치는 입력을 지원하지 않습니다: {device_info.get('name')}")

                    # 장치 기본 샘플레이트 및 채널 가져오기
                    device_rate = int(device_info.get('defaultSampleRate', self.rate))
                    # 채널은 최소 1 이상, 최대 장치가 지원하는 수
                    device_channels = int(max(1, min(self.channels, max_in)))

                    # 적용
                    chosen_rate = device_rate
                    chosen_channels = device_channels

                    # 디버그 정보 출력
                    print(f"선택 장치: index={self.input_device_index}, name={device_info.get('name')}, maxInputChannels={max_in}, defaultSampleRate={device_info.get('defaultSampleRate')}")
                else:
                    chosen_rate = self.rate
                    chosen_channels = self.channels

            except Exception as e:
                # 장치 정보 조회 실패 시, 기존 설정으로 시도
                print(f"장치 정보 조회 경고: {e} (기본 rate={self.rate}, channels={self.channels} 사용)")
                chosen_rate = self.rate
                chosen_channels = self.channels

            # 시도 리스트: 여러 조합으로 재시도
            attempts = []
            attempts.append({'channels': int(chosen_channels), 'rate': int(chosen_rate)})
            # 채널 1로 강제
            if int(chosen_channels) != 1:
                attempts.append({'channels': 1, 'rate': int(chosen_rate)})
            # 표준 샘플레이트로 대체
            if int(chosen_rate) != 44100:
                attempts.append({'channels': int(chosen_channels), 'rate': 44100})
                if int(chosen_channels) != 1:
                    attempts.append({'channels': 1, 'rate': 44100})

            opened = False
            last_error = None
            for att in attempts:
                open_kwargs = {
                    'format': self.format,
                    'channels': int(att['channels']),
                    'rate': int(att['rate']),
                    'input': True,
                    'frames_per_buffer': self.chunk,
                }
                if self.input_device_index is not None:
                    open_kwargs['input_device_index'] = int(self.input_device_index)

                try:
                    self.stream = self.p.open(**open_kwargs)
                    # 성공
                    self.rate = int(open_kwargs['rate'])
                    self.channels = int(open_kwargs['channels'])
                    self.is_recording = True
                    self.start_time = time.time()
                    print(f"녹음 시작. (rate={self.rate}, channels={self.channels})")
                    opened = True
                    break
                except Exception as e:
                    last_error = e
                    print(f"스트림 열기 시도 실패: channels={open_kwargs['channels']} rate={open_kwargs['rate']} -> {e}")

            # 입력 장치 지정으로 모두 실패하면 시스템 기본 장치로 재시도
            if not opened and self.input_device_index is not None:
                print("지정한 입력 장치로 모두 실패하여 시스템 기본 장치로 재시도합니다.")
                try:
                    # 시스템 기본으로 시도
                    open_kwargs = {
                        'format': self.format,
                        'channels': self.channels,
                        'rate': self.rate,
                        'input': True,
                        'frames_per_buffer': self.chunk,
                    }
                    self.stream = self.p.open(**open_kwargs)
                    self.rate = int(open_kwargs['rate'])
                    self.channels = int(open_kwargs['channels'])
                    self.is_recording = True
                    self.start_time = time.time()
                    print(f"녹음 시작(시스템 기본). (rate={self.rate}, channels={self.channels})")
                    opened = True
                except Exception as e:
                    last_error = e

            if not opened:
                raise last_error if last_error else RuntimeError("오디오 스트림을 열 수 없습니다.")

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

    def _reserve_next_voice_path(self, base_path):
        """voice_YYYYMMDD_HHMMSS_N.wav 처럼 중복 방지 파일명 예약"""
        base, ext = os.path.splitext(base_path)
        for i in range(1, 100):
            candidate = f"{base}_{i}{ext}"
            if not os.path.exists(candidate):
                return candidate
        raise RuntimeError("voice 파일명 예약 실패")

    def finish_recording(self):
        """녹음 완료 및 STT 처리 (TTS와 동일한 안전 저장 방식)"""
        self.stop_recording()

        # 최소 녹음 시간 체크 (0.5초 이상)
        if len(self.frames) == 0:
            print("녹음된 데이터가 없습니다.")
            return "녹음된 데이터가 없습니다.", None

        duration = len(self.frames) * self.chunk / self.rate
        if duration < 0.5:
            print(f"녹음 시간이 너무 짧습니다: {duration:.2f}초")
            return "녹음 시간이 너무 짧습니다. 최소 0.5초 이상 녹음해주세요.", None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        voice_filename = f"voice_{timestamp}.wav"
        voice_path = os.path.join(self.voice_dir, voice_filename)
        tmp_path = voice_path + ".tmp"

        try:
            # 임시 파일로 저장
            wf = wave.open(tmp_path, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()

            # 파일명 충돌 시 새 이름 예약
            final_path = voice_path
            try:
                os.replace(tmp_path, voice_path)
            except Exception:
                final_path = self._reserve_next_voice_path(voice_path)
                os.replace(tmp_path, final_path)

            print(f"음성 파일 저장 완료: {final_path} ({duration:.2f}초)")

            # STT 처리
            stt_result = self.speech_to_text(final_path)
            return stt_result, final_path

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
            return None
        try:
            voice = getattr(self, 'default_tts_voice', None) or 'alloy'
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
            )
            response.stream_to_file(output_path)
            print(f"TTS 파일 저장 완료: {output_path}")
            return output_path
        except Exception as e:
            print(f"TTS 오류: {e}")
            return None

    def cleanup(self):
        """리소스 정리"""
        try:
            self.stop_recording()
        except Exception:
            pass
        try:
            if hasattr(self, 'p') and self.p:
                self.p.terminate()
        except Exception:
            pass

    def __del__(self):
        try:
            self.cleanup()
        except Exception:
            pass

