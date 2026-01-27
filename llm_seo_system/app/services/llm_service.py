# app/services/llm_service.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Берём API ключ
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class LLMService:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def ask(self, prompt: str) -> str:
        """
        Отправляет prompt в LLM и возвращает текст ответа
        """

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert SEO content writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content
