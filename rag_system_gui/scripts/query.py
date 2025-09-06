import sys
from pathlib import Path

# Добавляем путь к src для импорта
sys.path.append(str(Path(__file__).parent.parent))

from rag_system_gui.src.database.qdrant_client import QdrantManager
from rag_system_gui.src.embedding.embedder import Embedder
from rag_system_gui.src.llm.ollama_client import OllamaClient
from rag_system_gui.config import DEFAULT_OLLAMA_MODEL, DEFAULT_CHUNK_LIMIT


def search_documents(query, limit=DEFAULT_CHUNK_LIMIT):
    """Поиск документов и возврат контекста с оценкой релевантности"""
    try:
        # Генерация эмбеддинга для запроса
        embedder = Embedder()
        query_embedding = embedder.generate_embeddings([query]).tolist()[0]
        
        # Поиск в базе данных
        db_manager = QdrantManager()
        search_result = db_manager.search_with_scores(query_embedding, limit)
        
        # Форматируем результаты с оценками
        results = []
        for hit, score in search_result:
            results.append({
                'text': hit.payload['text'],
                'score': score,
                'source': hit.payload.get('source', 'unknown')
            })
        
        return results
        
    except Exception as e:
        print(f"Search error: {e}")
        return []


def rag_query(query, limit=DEFAULT_CHUNK_LIMIT, model_name=DEFAULT_OLLAMA_MODEL):
    """Выполняет RAG запрос к базе данных с настраиваемыми параметрами"""
    try:
        # Ищем релевантные документы
        context_results = search_documents(query, limit)
        
        if not context_results:
            return "No relevant documents found for your question.", []
        
        # Формируем контекст с информацией о релевантности
        context_parts = []
        for i, result in enumerate(context_results, 1):
            context_parts.append(f"[Document {i}, relevance: {result['score']:.3f}]:")
            context_parts.append(result['text'])
            context_parts.append("")  # Пустая строка между документами
        
        context = "\n".join(context_parts)
        
        # Улучшенный промпт
        prompt = f"""Ты - помощник, который отвечает на вопросы на основе предоставленного контекста.

        КОНТЕКСТ 
        {context}

        ВОПРОС: {query}
        """
        
        # Запрос к языковой модели с выбранной моделью
        llm_client = OllamaClient()
        response = llm_client.generate_response(prompt, model_name)
        return response, context_results  # Возвращаем и ответ и контекст
        
    except Exception as e:
        return f"Error processing query: {str(e)}", []
