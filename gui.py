import sys
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from rag_system_gui.config import *
from rag_system_gui import rag_query, search_documents, add_documents
from rag_system_gui.src.llm.ollama_client import check_ollama_status
from rag_system_gui.src import QdrantManager


class ModernRAGGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RAG System - Qdrant + DeepSeek")
        self.root.geometry("1100x750")  # Немного увеличим окно
        self.root.configure(bg="#f0f0f0")
        
        # Настройки по умолчанию
        self.current_model = "deepseek-coder"
        self.chunk_limit = 5
        self.available_models = []
        
        # Центрирование окна
        self.center_window()
        
        # Стилизация
        self.setup_styles()
        
        # Загрузка доступных моделей
        self.load_available_models()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Проверка сервисов при запуске
        self.check_services_on_startup()
    
    def load_available_models(self):
        """Загружает список доступных моделей Ollama"""
        try:
            ollama_ok, ollama_msg, model_names = check_ollama_status()
            
            if ollama_ok and model_names:
                self.available_models = model_names
            else:
                self.available_models = ["deepseek-coder"]  # Значение по умолчанию
                self.log_message(f"Could not load models: {ollama_msg}")
                
        except Exception as e:
            print(f"Error loading models: {e}")
            self.available_models = ["deepseek-coder"]

    def setup_query_tab(self, parent):
        """Настройка вкладки запросов с выбором модели и количества чанков"""
        # Верхняя часть - настройки и ввод запроса
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Настройки запроса
        settings_frame = ttk.Frame(top_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(settings_frame, text="Model:", width=10).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.model_var = tk.StringVar(value=self.current_model)
        model_combo = ttk.Combobox(settings_frame, textvariable=self.model_var, 
                                values=self.available_models, width=20, state="readonly")
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        model_combo.bind("<<ComboboxSelected>>", self.on_model_change)
        
        ttk.Label(settings_frame, text="Chunk limit:", width=10).grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.limit_var = tk.StringVar(value=str(self.chunk_limit))
        limit_spin = ttk.Spinbox(settings_frame, textvariable=self.limit_var, from_=1, to=20, width=5)
        limit_spin.grid(row=0, column=3, sticky=tk.W)
        limit_spin.bind("<Return>", self.on_limit_change)
        limit_spin.bind("<<Increment>>", self.on_limit_change)
        limit_spin.bind("<<Decrement>>", self.on_limit_change)
        
        ttk.Button(settings_frame, text="Refresh Models", command=self.refresh_models,
                style='Secondary.TButton').grid(row=0, column=4, padx=(20, 0))
        
        # Поле ввода запроса
        query_frame = ttk.Frame(top_frame)
        query_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(query_frame, text="Ask a question:", style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.query_var = tk.StringVar()
        query_entry = ttk.Entry(query_frame, textvariable=self.query_var, font=('Arial', 12))
        query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        query_entry.bind('<Return>', lambda e: self.run_query())
        
        ttk.Button(query_frame, text="Search", command=self.run_query, 
                style='Primary.TButton').pack(side=tk.RIGHT)
        
        # Центральная часть - результаты с вкладками
        result_notebook = ttk.Notebook(parent)
        result_notebook.pack(fill=tk.BOTH, expand=True)
        # СОХРАНЯЕМ ССЫЛКУ НА КОМБОБОКС
        self.model_combo = ttk.Combobox(settings_frame, textvariable=self.model_var, 
                                    values=self.available_models, width=20, state="readonly")
        self.model_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)
        # Вкладка ответа
        answer_frame = ttk.Frame(result_notebook, padding=10)
        result_notebook.add(answer_frame, text="Answer")
        
        self.answer_area = scrolledtext.ScrolledText(answer_frame, height=15, 
                                                    font=('Arial', 11), wrap=tk.WORD)
        self.answer_area.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка контекста
        context_frame = ttk.Frame(result_notebook, padding=10)
        result_notebook.add(context_frame, text="Context")
        
        self.context_area = scrolledtext.ScrolledText(context_frame, height=15, 
                                                    font=('Consolas', 9), wrap=tk.WORD)
        self.context_area.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка информации о запросе
        info_frame = ttk.Frame(result_notebook, padding=10)
        result_notebook.add(info_frame, text="Query Info")
        
        self.info_area = scrolledtext.ScrolledText(info_frame, height=15, 
                                                font=('Consolas', 9), wrap=tk.WORD)
        self.info_area.pack(fill=tk.BOTH, expand=True)

    def on_model_change(self, event=None):
        """Обработчик изменения модели"""
        selected_model = self.model_var.get()
        if selected_model and selected_model != self.current_model:
            self.current_model = selected_model
            self.log_message(f"Model changed to: {self.current_model}")
        else:
            # Если выбор не изменился, не логируем
            pass

    def on_limit_change(self, event=None):
        """Обработчик изменения лимита чанков"""
        try:
            self.chunk_limit = int(self.limit_var.get())
            self.log_message(f"Chunk limit changed to: {self.chunk_limit}")
        except ValueError:
            self.limit_var.set(str(self.chunk_limit))  # Восстанавливаем предыдущее значение

    def refresh_models(self):
        """Обновляет список доступных моделей"""
        self.log_message("Refreshing available models...")
        self.load_available_models()
        
        # Обновляем комбобокс, а не StringVar
        if hasattr(self, 'model_combo'):
            current_selection = self.model_combo.get()
            self.model_combo['values'] = self.available_models
            
            # Сохраняем текущий выбор, если он все еще доступен
            if current_selection in self.available_models:
                self.model_combo.set(current_selection)
                self.current_model = current_selection
            elif self.available_models:
                # Иначе выбираем первую доступную модель
                self.model_combo.set(self.available_models[0])
                self.current_model = self.available_models[0]
        
        self.log_message(f"Available models: {', '.join(self.available_models)}")

    def _run_query_thread(self, query):
        """Поток выполнения запроса с учетом выбранных параметров"""
        try:
            # Получаем текущие настройки
            model_name = self.current_model
            chunk_limit = self.chunk_limit
            
            # Обновляем информацию о запросе
            info_text = f"Query: {query}\n"
            info_text += f"Model: {model_name}\n"
            info_text += f"Chunk limit: {chunk_limit}\n\n"
            
            self.root.after(0, lambda: self.info_area.insert(tk.END, info_text))
            
            # Сначала ищем документы
            context_results = search_documents(query, limit=chunk_limit)
            
            if not context_results:
                self.root.after(0, self._update_no_results, query)
                return
            
            # Показываем информацию о найденных документах
            info_text += f"Found {len(context_results)} relevant chunks:\n"
            for i, result in enumerate(context_results, 1):
                info_text += f"{i}. Score: {result['score']:.4f}, Source: {result.get('source', 'unknown')}\n"
            
            self.root.after(0, lambda: self.info_area.insert(tk.END, info_text))
            
            # Формируем контекст для показа пользователю
            context_text = f"Context used for answer (showing {len(context_results)} chunks):\n\n"
            for i, result in enumerate(context_results, 1):
                context_text += f"=== Chunk {i} (relevance: {result['score']:.3f}) ===\n"
                context_text += f"Source: {result.get('source', 'unknown')}\n"
                context_text += f"Content: {result['text']}\n\n"
            
            self.root.after(0, lambda: self.context_area.insert(tk.END, context_text))
            
            # Выполняем запрос с выбранными параметрами
            answer, _ = rag_query(query, limit=chunk_limit, model_name=model_name)
            
            # Обновляем GUI
            self.root.after(0, self._update_query_results, query, answer, model_name, chunk_limit)
            
        except Exception as e:
            self.root.after(0, self._update_query_error, str(e))

    def _update_query_results(self, query, answer, model_name, chunk_limit):
        """Обновление результатов запроса с информацией о параметрах"""
        self.answer_area.delete(1.0, tk.END)
        self.answer_area.insert(tk.END, f"Question: {query}\n")
        self.answer_area.insert(tk.END, f"Model: {model_name}, Chunks: {chunk_limit}\n\n")
        self.answer_area.insert(tk.END, f"Answer:\n{answer}")
        
        # Добавляем информацию в info area
        self.info_area.insert(tk.END, f"\nQuery completed successfully using model: {model_name}")
        
        self.log_message(f"Query completed using {model_name} with {chunk_limit} chunks")

    def _update_no_results(self, query):
        """Обновление при отсутствии результатов"""
        self.answer_area.delete(1.0, tk.END)
        self.answer_area.insert(tk.END, f"Question: {query}\n\n")
        self.answer_area.insert(tk.END, "No relevant documents found for this question.")
        
        self.context_area.delete(1.0, tk.END)
        self.context_area.insert(tk.END, "No matching documents found in the database.")
        
        self.info_area.insert(tk.END, f"\nNo results found for query: {query}")
        
        self.log_message(f"No results for query: {query}")

    def _update_query_error(self, error_msg):
        """Обновление при ошибке запроса"""
        self.answer_area.delete(1.0, tk.END)
        self.answer_area.insert(tk.END, "Error occurred during processing.")
        
        self.context_area.delete(1.0, tk.END)
        self.context_area.insert(tk.END, f"Error: {error_msg}")
        
        self.info_area.insert(tk.END, f"\nError during query: {error_msg}")
        
        self.log_message(f"Query error: {error_msg}")

    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Настройка стилей для элементов интерфейса"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветовой схемы
        style.configure('TFrame', background='#f0f0f0')
        style.configure('Header.TLabel', background='#4a6fa5', foreground='white', font=('Arial', 14, 'bold'))
        style.configure('Title.TLabel', background='#f0f0f0', foreground='#2c3e50', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', background='#f0f0f0', foreground='#34495e', font=('Arial', 12))
        
        # Стили для кнопок
        style.configure('Primary.TButton', background='#3498db', foreground='white', font=('Arial', 10, 'bold'))
        style.map('Primary.TButton', background=[('active', '#2980b9')])
        
        style.configure('Secondary.TButton', background='#2ecc71', foreground='white', font=('Arial', 10, 'bold'))
        style.map('Secondary.TButton', background=[('active', '#27ae60')])
        
        style.configure('Danger.TButton', background='#e74c3c', foreground='white', font=('Arial', 10, 'bold'))
        style.map('Danger.TButton', background=[('active', '#c0392b')])
        
        # Стили для вкладок
        style.configure('TNotebook', background='#f0f0f0', borderwidth=0)
        style.configure('TNotebook.Tab', background='#bdc3c7', foreground='#2c3e50', padding=[10, 5], font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#3498db')], foreground=[('selected', 'white')])
    
    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        # Основной контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        header_frame = ttk.Frame(main_container, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="RAG System with Qdrant & DeepSeek", style='Header.TLabel')
        title_label.pack(pady=15)
        
        # Создание вкладок
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка документов
        docs_frame = ttk.Frame(notebook, padding=10)
        notebook.add(docs_frame, text="📁 Documents")
        
        # Вкладка запросов
        query_frame = ttk.Frame(notebook, padding=10)
        notebook.add(query_frame, text="🔍 Query")
        
        # Вкладка настроек
        settings_frame = ttk.Frame(notebook, padding=10)
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # Заполняем вкладки
        self.setup_documents_tab(docs_frame)
        self.setup_query_tab(query_frame)
        self.setup_settings_tab(settings_frame)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_container, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_documents_tab(self, parent):
        """Настройка вкладки документов"""
        # Левая панель - управление документами
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(left_frame, text="Document Management", style='Title.TLabel').pack(pady=(0, 10))
        
        # Кнопки управления
        ttk.Button(left_frame, text="Add Documents", command=self.add_documents, 
                  style='Primary.TButton').pack(fill=tk.X, pady=5)
        
        ttk.Button(left_frame, text="Process Documents", command=self.process_documents, 
                  style='Secondary.TButton').pack(fill=tk.X, pady=5)
        
        ttk.Button(left_frame, text="Open Documents Folder", command=self.open_documents_folder, 
                  style='Secondary.TButton').pack(fill=tk.X, pady=5)
        
        # Информация о документах
        info_frame = ttk.LabelFrame(left_frame, text="Document Info", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        self.doc_count_var = tk.StringVar(value="0 documents")
        ttk.Label(info_frame, textvariable=self.doc_count_var).pack()
        
        self.doc_size_var = tk.StringVar(value="Total size: 0 MB")
        ttk.Label(info_frame, textvariable=self.doc_size_var).pack()
        
        # Правая панель - лог обработки
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="Processing Log", style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.log_area = scrolledtext.ScrolledText(right_frame, height=20, width=60, 
                                                 font=('Consolas', 10))
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Обновляем информацию о документах
        self.update_documents_info()  
   
    def setup_settings_tab(self, parent):
        """Настройка вкладки настроек"""
        # Настройки сервисов
        service_frame = ttk.LabelFrame(parent, text="Service Status", padding=10)
        service_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.qdrant_status = tk.StringVar(value="Qdrant: Checking...")
        ttk.Label(service_frame, textvariable=self.qdrant_status, 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        
        self.ollama_status = tk.StringVar(value="Ollama: Checking...")
        ttk.Label(service_frame, textvariable=self.ollama_status, 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        
        self.model_status = tk.StringVar(value="Model: Checking...")
        ttk.Label(service_frame, textvariable=self.model_status, 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        
        ttk.Button(service_frame, text="Check Services", command=self.check_services, 
                  style='Secondary.TButton').pack(pady=5)
        
        # Настройки системы
        settings_frame = ttk.LabelFrame(parent, text="System Settings", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(settings_frame, text="Model:", width=10).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.model_var = tk.StringVar(value=self.current_model)
        
        ttk.Label(settings_frame, text="Chunk Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.chunk_size_var = tk.StringVar(value="1000")
        ttk.Entry(settings_frame, textvariable=self.chunk_size_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        ttk.Label(settings_frame, text="Chunk Overlap:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.chunk_overlap_var = tk.StringVar(value="200")
        ttk.Entry(settings_frame, textvariable=self.chunk_overlap_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        ttk.Button(settings_frame, text="Apply Settings", command=self.apply_settings, 
                  style='Secondary.TButton').grid(row=2, column=0, columnspan=2, pady=10)
    
    def update_documents_info(self):
        """Обновление информации о документах"""
        try:
            if DOCUMENTS_DIR.exists():
                documents = list(DOCUMENTS_DIR.glob("*"))
                doc_count = len(documents)
                
                total_size = sum(f.stat().st_size for f in documents if f.is_file())
                total_size_mb = total_size / (1024 * 1024)
                
                self.doc_count_var.set(f"{doc_count} documents")
                self.doc_size_var.set(f"Total size: {total_size_mb:.2f} MB")
            else:
                self.doc_count_var.set("0 documents")
                self.doc_size_var.set("Total size: 0 MB")
                
        except Exception as e:
            self.log_message(f"Error updating document info: {e}")
    
    def add_documents(self):
        """Добавление документов"""
        folder_path = filedialog.askdirectory(title="Select Documents Folder")
        if folder_path:
            try:
                # Копируем документы в папку проекта
                for item in Path(folder_path).iterdir():
                    if item.is_file() and item.suffix.lower() in ['.pdf', '.docx', '.txt']:
                        shutil.copy2(item, DOCUMENTS_DIR / item.name)
                
                self.log_message(f"Added documents from: {folder_path}")
                self.update_documents_info()
                
            except Exception as e:
                self.log_message(f"Error adding documents: {e}")
    
    def process_documents(self):
        """Обработка документов"""
        self.log_message("Starting document processing...")
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self._process_documents_thread)
        thread.daemon = True
        thread.start()
    
    def _process_documents_thread(self):
        """Поток обработки документов"""
        try:
            self.log_message("Loading modules...")
            self.log_message("Processing documents...")
            
            # Обработка документов
            success = add_documents(str(DOCUMENTS_DIR))
            
            if success:
                self.log_message("Documents successfully processed and added to database!")
            else:
                self.log_message("Failed to process documents.")
                
        except Exception as e:
            self.log_message(f"Error processing documents: {e}")
    
    def open_documents_folder(self):
        """Открытие папки с документами"""
        try:
            open_folder_in_explorer(DOCUMENTS_DIR)
        except Exception as e:
            self.log_message(f"Error opening folder: {e}")
    
    def run_query(self):
        """Выполнение запроса"""
        query = self.query_var.get().strip()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a question.")
            return
        
        self.log_message(f"Processing query: {query}")
        
        # Очищаем области результатов
        self.context_area.delete(1.0, tk.END)
        self.answer_area.delete(1.0, tk.END)
        self.context_area.insert(tk.END, "Searching for relevant content...")
        self.answer_area.insert(tk.END, "Generating answer...")
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self._run_query_thread, args=(query,))
        thread.daemon = True
        thread.start()
    
    def start_qdrant(self):
        """Запуск Qdrant через Docker"""
        self.log_message("Starting Qdrant...")
        try:
            import subprocess
            # Запускаем Qdrant в Docker
            subprocess.run(["docker", "run", "-d", "-p", "6333:6333", "-p", "6334:6334", 
                        "qdrant/qdrant"], check=True)
            self.log_message("Qdrant started successfully")
            # Перепроверяем статус через несколько секунд
            self.root.after(3000, self.check_services)
        except Exception as e:
            self.log_message(f"Failed to start Qdrant: {e}")

    def start_ollama(self):
        """Запуск Ollama"""
        self.log_message("Starting Ollama...")
        try:
            import subprocess
            # Запускаем Ollama в отдельном процессе
            subprocess.Popen(["ollama", "serve"])
            self.log_message("Ollama started successfully")
            # Перепроверяем статус через несколько секунд
            self.root.after(3000, self.check_services)
        except Exception as e:
            self.log_message(f"Failed to start Ollama: {e}")

    def download_model(self):
        """Загрузка модели DeepSeek"""
        self.log_message("Downloading DeepSeek model...")
        try:
            import subprocess
            # Загружаем модель
            subprocess.run(["ollama", "pull", "deepseek-r1:latest"], check=True)
            self.log_message("DeepSeek model downloaded successfully")
            # Перепроверяем статус через несколько секунд
            self.root.after(3000, self.check_services)            
        except Exception as e:
            self.log_message(f"Failed to download model: {e}")

    def _update_query_error(self, error_msg):
        """Обновление при ошибке запроса"""
        self.context_area.delete(1.0, tk.END)
        self.context_area.insert(tk.END, "Error occurred during search.")
        
        self.answer_area.delete(1.0, tk.END)
        self.answer_area.insert(tk.END, f"Error: {error_msg}")
        
        self.log_message(f"Query error: {error_msg}")
    
    def check_services(self):
        """Проверка сервисов"""
        self.qdrant_status.set("Qdrant: Checking...")
        self.ollama_status.set("Ollama: Checking...")
        self.model_status.set("Model: Checking...")
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self._check_services_thread)
        thread.daemon = True
        thread.start()
    
    def check_services_on_startup(self):
        """Проверка сервисов при запуске"""
        # Неблокирующая проверка при запуске
        thread = threading.Thread(target=self._check_services_thread)
        thread.daemon = True
        thread.start()
    
    def _check_services_thread(self):
        """Поток проверки сервисов с использованием subprocess"""
        
        # Проверка Qdrant
        try:
            db_manager = QdrantManager()
            connected, message = db_manager.check_connection()
            
            if connected:
                self.root.after(0, lambda: self.qdrant_status.set("Qdrant: ✅ Running"))
            else:
                self.root.after(0, lambda: self.qdrant_status.set(f"Qdrant: ❌ {message}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.qdrant_status.set(f"Qdrant: ❌ Error"))

        # Проверка Ollama через функцию check_ollama_status
        try:
            ollama_ok, ollama_msg, model_names = check_ollama_status()
            
            if ollama_ok:
                self.root.after(0, lambda: self.ollama_status.set("Ollama: ✅ Running"))
                
                # Проверяем наличие deepseek в моделях
                has_deepseek = any('deepseek' in name.lower() for name in model_names)
                if has_deepseek:
                    self.root.after(0, lambda: self.model_status.set("Model: ✅ DeepSeek available"))
                elif model_names:
                    self.root.after(0, lambda: self.model_status.set(f"Model: ⚠️ Available: {', '.join(model_names[:2])}"))
                else:
                    self.root.after(0, lambda: self.model_status.set("Model: ❌ No models"))
            else:
                self.root.after(0, lambda: self.ollama_status.set(f"Ollama: ❌ {ollama_msg}"))
                self.root.after(0, lambda: self.model_status.set("Model: ❌ Unknown"))
                
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.ollama_status.set(f"Ollama: ❌ {error_msg}"))
            self.root.after(0, lambda: self.model_status.set("Model: ❌ Unknown"))
   
    def apply_settings(self):
        """Применение настроек"""
        try:
            chunk_size = int(self.chunk_size_var.get())
            chunk_overlap = int(self.chunk_overlap_var.get())
            
            # Здесь можно сохранить настройки в config.py или отдельный файл
            self.log_message(f"Settings applied: Chunk Size={chunk_size}, Overlap={chunk_overlap}")
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for chunk size and overlap.")
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        def update_log():
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
            self.status_var.set(message)
        
        self.root.after(0, update_log)


if __name__ == "__main__":
    # Проверяем, активировано ли виртуальное окружение
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Virtual environment not activated!")
    
    # Создаем и запускаем приложение
    root = tk.Tk()
    app = ModernRAGGUI(root)
    root.mainloop()
