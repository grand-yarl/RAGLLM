from pathlib import Path
from flask import Flask

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = ['.pdf', '.docx', '.txt']
app.config['UPLOAD_FOLDER'] = Path('./data/documents')

# Define secret key to enable session
app.secret_key = 'This is your secret key to utilize session in Flask'

from rag_system_gui.app import views