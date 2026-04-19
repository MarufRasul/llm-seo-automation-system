#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Добавляем текущую папку в path
sys.path.insert(0, str(Path(__file__).parent))

# Загружаем .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from llm_seo_system.app.agents.query_simulator_agent import QuerySimulatorAgent

print("🚀 Инициализируем QuerySimulatorAgent...")
agent = QuerySimulatorAgent()

test_topics = [
    'LG Gram laptop for students',
    '동원 연어 영양',  # Корейский: Dongwon salmon nutrition
    '도자기 핸드메이드'  # Корейский: Handmade ceramics
]

for topic in test_topics:
    print(f"\n{'='*70}")
    print(f"🎯 Тема: {topic}")
    print('='*70)
    
    queries = agent.generate_queries(topic)
    
    print('\n✅ СОБРАННЫЕ РЕАЛЬНЫЕ ВОПРОСЫ:')
    print('-'*70)
    for i, q in enumerate(queries, 1):
        print(f'{i}. {q}')
    print(f'\nВсего вопросов: {len(queries)}')
