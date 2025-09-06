import sys
import textwrap
from rag_system_gui.config import DOCUMENTS_DIR
from rag_system_gui import add_documents, rag_query
from rag_system_gui.src import QdrantManager


def main():
    while True:
        print("\n" + "="*80)
        print("RAG СИСТЕМА С QDRANT И DEEPSEEK")
        print("="*80)
        print("1. Добавить документы в базу данных")
        print("2. Выполнить запрос к базе данных")
        print("3. Показать информацию о базе данных")
        print("4. Выйти")
        print(80 * "-")
        choice = input("\nВыберите действие (1-4): ")
        print(80 * "-")
        if choice == "1":
            add_documents(DOCUMENTS_DIR)
        elif choice == "2":
            question = str(input("\nЗадайте вопрос: "))
            answer, context = rag_query(question)
            for line in textwrap.wrap(answer, 80):
                print(line)
            print(80 * "=")
            for data in context:
                print(f"{data['text']}")
                print(f"{data['score']}")
                print(80 * "-")
        elif choice == "3":
            db_manager = QdrantManager()
            collections = db_manager.client.get_collections()
            print(f"Доступные коллекции: {collections.collections}")
        elif choice == "4":
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте еще раз.")


if __name__ == "__main__":
    # Проверяем, активировано ли виртуальное окружение
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("ВНИМАНИЕ: Виртуальное окружение не активировано!")
        print("Рекомендуется активировать его командой:")
        print("  Windows: .venv\\Scripts\\activate.bat")
        print("  Linux/Mac: source .venv/bin/activate")
        response = input("Продолжить без активации? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    main()
