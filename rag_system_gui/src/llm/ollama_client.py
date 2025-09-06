import ollama
from rag_system_gui.config import DEFAULT_OLLAMA_MODEL


class OllamaClient:
    @staticmethod
    def generate_response(prompt, model_name=DEFAULT_OLLAMA_MODEL, max_tokens=1000):
        try:
            response = ollama.generate(
                model=model_name,
                prompt=prompt,
                options={
                    'temperature': 0.1,
                    'num_predict': max_tokens,
                    'top_p': 0.9
                }
            )
            return response['response']
        except Exception as e:
            return f"Error generating response: {str(e)}"

    @staticmethod
    def get_available_models():
        """Возвращает список доступных моделей Ollama"""
        try:
            response = ollama.list()
            models = []
            
            if hasattr(response, 'models'):
                for model in response.models:
                    if hasattr(model, 'name'):
                        models.append(model.name)
            elif isinstance(response, dict) and 'models' in response:
                for model in response['models']:
                    if 'name' in model:
                        models.append(model['name'])
            
            return sorted(models)
        except Exception as e:
            print(f"Error getting available models: {e}")
            return []


# Добавьте эту функцию в конец файла
def check_ollama_status():
    """Проверяет статус Ollama и доступные модели"""
    try:
        # Пытаемся получить список моделей
        response = ollama.list()
        
        # Обрабатываем разные форматы ответа
        if hasattr(response, 'models'):
            models = response.models
        else:
            # Если response - словарь
            models = response.get('models', [])
        
        # Извлекаем имена моделей безопасным способом
        model_names = []
        for model in models:
            if hasattr(model, 'name'):
                model_names.append(model.name)
            elif isinstance(model, dict) and 'name' in model:
                model_names.append(model['name'])
            elif hasattr(model, 'model'):  # Альтернативный формат
                model_names.append(model.model)
        
        return True, "Ollama is running", model_names
        
    except Exception as e:
        return False, str(e), []