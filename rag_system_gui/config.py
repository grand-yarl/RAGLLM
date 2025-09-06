import os
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = Path("./data/documents")

# Создаем необходимые директории
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

# Настройки Qdrant
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "rag_collection"

# Настройки обработки документов
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# Настройки модели
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Добавьте эту строку
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_OLLAMA_MODEL = "deepseek-coder"
DEFAULT_CHUNK_LIMIT = 5


# Функция для открытия папки в проводнике Windows
def open_folder_in_explorer(path):
    """Открывает папку в проводнике Windows"""
    try:
        path = os.path.abspath(path)
        os.startfile(path)
        return True
    except Exception as e:
        print(f"Не удалось открыть папку в проводнике: {e}")
        return False