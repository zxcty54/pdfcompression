from flask import Flask, request, send_file, render_template_string
import subprocess
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

HTML = """
<!doctype html>
<html>
<head>
  <title>PDF Compressor</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; background: #f0f0f0; text-align: center; }
    form { background: white; padding: 20px; border-radius: 8px; display: inline-block; }
    input[type="file"], input[type="submit"] { margin: 10px; }
  </style>
</head>
<body>
  <h2>Upload PDF to Compress</h2>
  <form method=post enctype=multipart/form-data>
    <input type=file name=file required>
    <br>
    <input type=submit value="Compress PDF">
  </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def compress_pdf():
    if request.method == 'POST':
        pdf_file = request.files['file']
        if not pdf_file or not pdf_file.filename.endswith('.pdf'):
            return "❌ Please upload a valid PDF file."

        os.makedirs('tmp', exist_ok=True)
        input_path = f'tmp/{uuid.uuid4()}.pdf'
        output_path = f'tmp/compressed_{uuid.uuid4()}.pdf'
        pdf_file.save(input_path)

        gs_command = [
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/ebook',  # /screen /ebook /printer /prepress /default
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            input_path
        ]

        try:
            subprocess.run(gs_command, check=True)
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return f"❌ Compression failed: {e}"
        finally:
            try: os.remove(input_path)
            except: pass
            try: os.remove(output_path)
            except: pass

    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True)
