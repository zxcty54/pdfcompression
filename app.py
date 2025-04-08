import os
import tempfile
import subprocess
from flask import Flask, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/compress', methods=['POST'])
def compress_pdf():
    file = request.files.get('file')
    if not file:
        return {'error': 'No file provided'}, 400

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, 'input.pdf')
        gs_path = os.path.join(tmpdir, 'compressed_gs.pdf')
        mutool_path = os.path.join(tmpdir, 'compressed_mutool.pdf')
        qpdf_path = os.path.join(tmpdir, 'final_compressed.pdf')

        file.save(input_path)

        # 1️⃣ Ghostscript Compression
        subprocess.run([
            'gs', '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/screen',
            '-dNOPAUSE', '-dQUIET', '-dBATCH',
            f'-sOutputFile={gs_path}', input_path
        ])

        # 2️⃣ Mutool Clean
        subprocess.run([
            'mutool', 'clean', '-gg', '-d', '-s',
            gs_path, mutool_path
        ])

        # 3️⃣ QPDF Optimization
        subprocess.run([
            'qpdf', '--linearize',
            mutool_path, qpdf_path
        ])

        return send_file(qpdf_path, as_attachment=True, download_name='compressed.pdf')

@app.route('/')
def home():
    return 'PDF Compressor API is live!'

if __name__ == '__main__':
    app.run(debug=True)
