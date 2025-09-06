from qdrant_client import QdrantClient
from qdrant_client.http import models
from rag_system_gui.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME


class QdrantManager:
    def __init__(self):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    def create_collection(self, vector_size=384):
        try:
            self.client.get_collection(COLLECTION_NAME)
            print(f"Collection {COLLECTION_NAME} already exists")
        except Exception:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection {COLLECTION_NAME} created")
    
    def add_documents(self, documents, embeddings, sources=None):
        points = []
        for idx, (text, embedding) in enumerate(zip(documents, embeddings)):
            payload = {"text": text}
            if sources and idx < len(sources):
                payload["source"] = sources[idx]
            
            points.append(
                models.PointStruct(
                    id=idx,
                    vector=embedding,
                    payload=payload
                )
            )
        
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"Added {len(documents)} documents")
    
    def search_with_scores(self, query_embedding, limit=5):
        """Поиск с возвратом оценок релевантности"""
        search_result = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True,
            with_vectors=False,
            score_threshold=0.3  # Минимальный порог релевантности
        )
        
        # Возвращаем результаты с оценками
        return [(hit, hit.score) for hit in search_result]
    
    def search(self, query_embedding, limit=3):
        """Простой поиск без оценок (для обратной совместимости)"""
        search_result = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit
        )
        return [hit.payload['text'] for hit in search_result]
    
    def check_connection(self):
        """Проверяет подключение к Qdrant"""
        try:
            self.client.get_collections()
            return True, "Connected successfully"
        except Exception as e:
            return False, str(e)