from flask import Flask, request, render_template, send_file
import os
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from video_processor import process_video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# 确保上传和处理文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return 'No file part'
    files = request.files.getlist('files[]')
    if not files:
        return 'No selected files'
    
    processed_files = []
    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            processed_file = process_video(filepath, app.config['PROCESSED_FOLDER'])
            processed_files.append(processed_file)
    
    # 如果只上传了一个文件，则直接返回该文件
    if len(processed_files) == 1:
        return send_file(processed_files[0], as_attachment=True)
    
    # 如果上传了多个文件，则返回一个包含所有处理后文件的压缩包
    zip_filename = 'processed_files.zip'
    zip_filepath = os.path.join(app.config['PROCESSED_FOLDER'], zip_filename)
    with ZipFile(zip_filepath, 'w') as zipf:
        for processed_file in processed_files:
            zipf.write(processed_file, os.path.basename(processed_file))
    
    return send_file(zip_filepath, as_attachment=True)
if __name__ == '__main__':
    app.run(debug=True)
