import os
import json
from typing import Dict, List

MEMORY_DIR = "memory"
os.makedirs(MEMORY_DIR, exist_ok=True)


class MemoryService:
    def __init__(self):
        self.topics_file = os.path.join(MEMORY_DIR, "topics.json")
        self.data = self._load()

    def _load(self) -> Dict:
        if os.path.exists(self.topics_file):
            with open(self.topics_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_article_record(self, topic: str, metadata: dict):
        self.data[topic] = metadata
        with open(self.topics_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"[MemoryService] saved topic: {topic}")

    def get_topics(self) -> List[str]:
        return list(self.data.keys())

    def get_metadata(self, topic: str) -> dict:
        return self.data.get(topic, {})
