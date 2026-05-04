

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader
from typing import List, Optional
import os


class RAGEvaluatorAgent:
    """
    Реальный RAG агент с получением документов из:
    1. Веб-сайтов (WebBaseLoader)
    2. Собственной базы статей
    3. Внешних источников (Google Scholar, Wikipedia и т.д.)
    """
    
    def __init__(self, use_web_sources: bool = True):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.use_web_sources = use_web_sources
        self.vector_store = None
    
    def load_documents_from_urls(self, urls: List[str]) -> List[Document]:
        """Загружает реальные документы с веб-сайтов"""
        print(f" Загружаем документы с {len(urls)} источников...")
        all_docs = []
        
        for url in urls:
            try:
                print(f"  ↓ {url}")
                loader = WebBaseLoader(url)
                docs = loader.load()
                all_docs.extend(docs)
                print(f"    ✓ Загружено {len(docs)} документов")
            except Exception as e:
                print(f"     Ошибка: {e}")
        
        return all_docs
    
    def load_documents_from_memory(self, articles: List[dict]) -> List[Document]:
        """Загружает документы из собственной базы (memory/articles.json)"""
        print(f" Загружаем {len(articles)} статей из памяти...")
        docs = []
        
        for article in articles:
            doc = Document(
                page_content=article.get("content", ""),
                metadata={
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "date": article.get("date", "")
                }
            )
            docs.append(doc)
        
        print(f"  ✓ Загружено {len(docs)} документов")
        return docs
    
    def build_vector_store(self, documents: List[Document]):
        """Создает векторную базу данных"""
        print(f" Создаем векторную базу из {len(documents)} документов...")
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        print("  ✓ Векторная база готова")
    
    def evaluate_with_real_data(
        self,
        query: str,
        urls: Optional[List[str]] = None,
        k: int = 3
    ) -> dict:
        """
        Реальная оценка с получением документов из интернета
        
        Args:
            query: Поисковый запрос
            urls: Список URL для скрейпинга
            k: Количество релевантных документов
        """
        print(f"\n RAG Evaluation (REAL)")
        print(f"  Query: '{query}'")
        print(f"  Sources: {len(urls) if urls else 'Auto-detected'}")
        
        # Если URLs не указаны, используем поиск
        if not urls:
            urls = self._find_relevant_urls(query)
        
        # Загружаем документы
        documents = self.load_documents_from_urls(urls)
        
        if not documents:
            print("    Документы не найдены!")
            return {
                "query": query,
                "retrieved_docs": [],
                "response": "No relevant documents found.",
                "source": "web"
            }
        
        # Создаем векторную базу
        self.build_vector_store(documents)
        
        # Поиск релевантных документов
        retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        retrieved_docs = retriever.invoke(query)
        
        print(f"\n   Найдено документов: {len(retrieved_docs)}")
        for i, doc in enumerate(retrieved_docs, 1):
            title = doc.metadata.get("title", "No title")
            url = doc.metadata.get("url") or doc.metadata.get("source", "No URL")
            print(f"    {i}. {title}")
            print(f"       {url[:60]}...")
        
        # Генерируем ответ на основе найденных документов
        context = "\n".join([
            f"Source: {doc.metadata.get('url') or doc.metadata.get('source', 'Unknown')}\n{doc.page_content[:300]}"
            for doc in retrieved_docs
        ])
        
        response = self.llm.invoke(
            f"""Answer based ONLY on this context. 
If information is not in context, say "Not found in sources".

Context:
{context}

Question: {query}"""
        )
        
        return {
            "query": query,
            "retrieved_docs": [
                {
                    "title": doc.metadata.get("title", ""),
                    "url": doc.metadata.get("url") or doc.metadata.get("source", ""),
                    "content_preview": doc.page_content[:150]
                }
                for doc in retrieved_docs
            ],
            "response": response.content,
            "source": "web",
            "document_count": len(retrieved_docs)
        }

    def evaluate(self, query: str, urls: Optional[List[str]] = None, k: int = 3) -> dict:
        """Compatibility wrapper that still uses real web/API-backed data."""
        return self.evaluate_with_real_data(query=query, urls=urls, k=k)
    
    def _find_relevant_urls(self, query: str) -> List[str]:
        """
        Альтернатива: использовать Google Search API (SerpAPI)
        для найти релевантные URL
        """
        import os
        from langchain_community.utilities import GoogleSearchAPIWrapper
        
        serpapi_key = os.getenv("SERPAPI_KEY")
        if not serpapi_key:
            print("    SERPAPI_KEY не установлен")
            return []
        
        print(f"  🔍 Поиск URL через Google...")
        search = GoogleSearchAPIWrapper(serpapi_api_key=serpapi_key)
        results = search.results(query, num_results=3)
        
        urls = [r.get("link") for r in results if "link" in r]
        print(f"    ✓ Найдено {len(urls)} URL")
        return urls


# Пример использования
if __name__ == "__main__":
    agent = RAGEvaluatorAgent()
    
    # ВАРИАНТ 1: С конкретными URL
    print("\n" + "="*70)
    print("ВАРИАНТ 1: Оценка с реальными URL")
    print("="*70)
    
    urls = [
        "https://en.wikipedia.org/wiki/Laptop",
        "https://www.techradar.com/reviews/best-laptops"
    ]
    
    result = agent.evaluate_with_real_data(
        query="best lightweight laptop for students",
        urls=urls,
        k=2
    )
    
    print("\n Результат:")
    print(f"  Ответ: {result['response'][:200]}...")
    print(f"  Источников: {result['document_count']}")
