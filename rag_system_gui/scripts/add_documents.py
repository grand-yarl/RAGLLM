import sys
from pathlib import Path
from rag_system_gui.src import QdrantManager, DocumentLoader, TextChunker, Embedder
from rag_system_gui.config import CHUNK_SIZE, CHUNK_OVERLAP, DOCUMENTS_DIR


def add_documents(folder_path = DOCUMENTS_DIR):
    """Добавляет документы из указанной папки в базу данных"""
    try:
        # Загрузка документов
        loader = DocumentLoader()
        documents = loader.load_documents_from_folder(folder_path)
        
        if not documents:
            print("No documents found for processing")
            return False
        
        # Разбиение на чанки
        chunker = TextChunker()
        chunks = chunker.process_documents(documents, CHUNK_SIZE, CHUNK_OVERLAP)
        
        # Генерация эмбеддингов
        embedder = Embedder()
        embeddings = embedder.generate_embeddings(chunks)
        
        # Добавление в базу данных
        db_manager = QdrantManager()
        db_manager.create_collection(vector_size=embeddings.shape[1])
        db_manager.add_documents(chunks, embeddings.tolist())
        
        print(f"Processing completed. Added {len(chunks)} chunks.")
        return True
        
    except Exception as e:
        print(f"Error processing documents: {e}")
        return False
