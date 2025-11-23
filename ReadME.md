# RAG system for LLM project

The main purpose of this project to build **retrieval augmented generation (RAG)** mechanism for large language models. Whole system work with QDrant vectar database and Ollama models.

## Prerequisites

1. Install QDrant database (https://qdrant.tech/) 
2. Install Ollama (https://ollama.com/)
3. Setup local environment by running **setup.bat**
4. Configure QDrant credits in */rag_system_gui/config.py*
5. Configure LLM and Embedding model in */rag_system_gui/config.py*
6. Create folder */data/documents* and add all documents you want to process

## Run console app

1. Run command
```
python main.py
```

## Run desktop app

Run file **run_gui.bat** or command
```
python gui.py
```
