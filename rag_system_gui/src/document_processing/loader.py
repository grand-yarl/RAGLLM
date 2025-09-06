import os
from PyPDF2 import PdfReader
from docx import Document
from pathlib import Path


class DocumentLoader:
    @staticmethod
    def read_pdf(file_path):
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + " "
        except Exception as e:
            print(f"Error reading PDF file {file_path}: {e}")
        return text

    @staticmethod
    def read_docx(file_path):
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX file {file_path}: {e}")
        return text

    @staticmethod
    def read_txt(file_path):
        text = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            print(f"Error reading TXT file {file_path}: {e}")
        return text

    def load_documents_from_folder(self, folder_path):
        documents = []
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            print(f"Folder does not exist: {folder_path}")
            return documents
        
        for filename in os.listdir(folder_path):
            file_path = folder_path / filename
            file_ext = file_path.suffix.lower()
            
            if file_ext == '.pdf':
                text = self.read_pdf(file_path)
            elif file_ext == '.docx':
                text = self.read_docx(file_path)
            elif file_ext == '.txt':
                text = self.read_txt(file_path)
            else:
                continue
                
            if text:
                documents.append((filename, text))
                print(f"Loaded document: {filename}")
        return documents
