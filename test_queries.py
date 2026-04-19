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

print("\n📊 Собираем РЕАЛЬНЫЕ вопросы про 'LG Gram laptop for students'...\n")
queries = agent.generate_queries('LG Gram laptop for students')

print('\n' + '='*70)
print('✅ СОБРАННЫЕ РЕАЛЬНЫЕ ВОПРОСЫ:')
print('='*70)
for i, q in enumerate(queries, 1):
    print(f'{i}. {q}')
print('='*70)
print(f'\n✨ Всего собрано: {len(queries)} вопросов')
