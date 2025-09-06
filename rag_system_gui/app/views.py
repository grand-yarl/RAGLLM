import os
import datetime
from rag_system_gui.app import app
from flask import render_template, redirect, url_for, request, flash, send_file
from werkzeug.utils import secure_filename


def allowed_file(filename):
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
        return False
    return True


def get_uploaded_files():
    """Получаем список загруженных файлов"""
    files = []
    upload_folder = app.config['UPLOAD_FOLDER']

    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            filepath = os.path.join(upload_folder, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'path': filepath
                })

    return files


@app.route('/')
def index():
    files = get_uploaded_files()
    return render_template('upload_files.html', uploaded_files=files)


@app.route('/upload', methods=['POST'])
def upload_file():
    # Проверяем, есть ли файлы в запросе
    if 'files' not in request.files:
        flash('No files selected')
        return redirect(request.url)

    files = request.files.getlist('files')
    uploaded_count = 0

    for file in files:
        # Если пользователь не выбрал файл
        if file.filename == '':
            continue

        if file:
            # Безопасное имя файла
            filename = secure_filename(file.filename)

            # Сохраняем файл
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_count += 1

    if uploaded_count > 0:
        flash(f'Successfully uploaded {uploaded_count} file(s)')
    else:
        flash('No valid files were uploaded')

    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    """Скачивание файла"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        flash('File not found')
        return redirect(url_for('index'))


@app.route('/delete/<filename>')
def delete_file(filename):
    """Удаление файла"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f'File {filename} deleted successfully')
    else:
        flash('File not found')

    return redirect(url_for('index'))