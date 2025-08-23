import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from core.config import CONFIG_JUDGE_FINE_TUNING

load_dotenv()

class AISystem:
    def __init__(self):
        self.system_instruction = "당신은 독서를 돕는 AI입니다. 상대의 질문에 정성스럽게 대답하세요. 그리고 구체적이고 논리적인 설명이 좋습니다. 하지만 너무 길게 말하지는 마세요."
        try:
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
            genai.configure(api_key=self.gemini_api_key)
            
            self.model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=self.system_instruction)
        except Exception as e:
            print(f"Gemini API 초기화 오류: {e}")
            self.model = None

        self.judge_fine_tuning = CONFIG_JUDGE_FINE_TUNING
        

    def _AI(self, prompt, fine_tuning=None):
        if not self.model:
            return "AI 모델을 사용할 수 없습니다."
        
        try:
            if fine_tuning:
                chat_history = []
                for q, a in fine_tuning:
                    chat_history.append({'role': 'user', 'parts': [q]})
                    chat_history.append({'role': 'model', 'parts': [a]})
                
                chat = self.model.start_chat(history=chat_history)
                response = chat.send_message(prompt)
            else:
                response = self.model.generate_content(prompt)

            return response.text.strip()
        except Exception as e:
            print(f"AI 응답 생성 오류: {e}")
            return f"[AI 오류: {e}]"

    def judge_question(self, user_question):
        prompt = f"{user_question}\n\n위 질문에 답하기 위해 책의 내용이 필요하면 'True', 필요하지 않으면 'False'를 출력하세요. 오직 'True' 또는 'False'만 출력해야 합니다."
        response = self._AI(prompt, fine_tuning=self.judge_fine_tuning)
        print(f"질문 분석 결과: {response}")
        resp = (response or "").strip().lower()
        if resp not in ("true", "false"):
            return False 
        return resp == "true"


    def create_prompt(self, user_question, ocr_text=None):
        if ocr_text:
            return f"책 내용: [\n{ocr_text}\n]\n\n위 책 내용에 대한 질문: [{user_question}]"
        return user_question

    def get_response(self, final_prompt):
        return self._AI(final_prompt)

if __name__ == '__main__':
    ai = AISystem()

    test = ["이 책에서 주인공의 성격은 어떻게 변해가?", "요즘 볼만한 영화 추천해줘", "주인공은 처음에는 소심했지만, 여러 사건을 겪으며 점차 대담해졌다."]

    for q in test:
        print(f"질문: {q}")
        is_needed = ai.judge_question(q)
        print(f"책 내용 필요?: {is_needed}")
        print('===============')