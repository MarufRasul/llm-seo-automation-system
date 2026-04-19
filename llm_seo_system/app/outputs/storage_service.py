import os
from datetime import datetime


class StorageService:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_article(self, topic: str, content: str):
        """Сохраняет статью в файл"""
        safe_topic = topic.replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_topic}_{timestamp}.md"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f" Article saved: {filepath}")
        return filepath

    def save_article_html(self, topic: str, html_content: str):
        """Сохраняет HTML-статью в файл"""
        safe_topic = topic.replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_topic}_{timestamp}.html"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f" HTML article saved: {filepath}")
        return filepath

    def delete_article(self, article_name: str):
        """Удаляет сохраненную статью по имени файла без расширения."""
        filename = article_name if article_name.endswith('.md') else f"{article_name}.md"
        file_path = os.path.join(self.output_dir, filename)

        if os.path.exists(file_path):
            os.remove(file_path)
            print(f" Article deleted: {file_path}")
            return True

        return False
