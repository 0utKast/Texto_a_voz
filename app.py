import os
import io
import time
import re
import soundfile as sf
import fitz # PyMuPDF
from docx import Document
from flask import Flask, render_template, request, send_file, jsonify
from kokoro_onnx import Kokoro
from werkzeug.utils import secure_filename

# Configurar ruta de espeak-ng para Windows
ESPEAK_PATH = r"C:\Program Files\eSpeak NG"
os.environ["PHONEMIZER_ESPEAK_PATH"] = ESPEAK_PATH

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Cargar el modelo globalmente para rapidez
MODEL_PATH = "kokoro-v1.0.onnx"
VOICES_PATH = "voices-v1.0.bin"

print("Inicializando modelo Kokoro-82M...")
kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
print("Modelo listo.")

def extract_text_from_file(filepath):
    ext = filepath.split('.')[-1].lower()
    text = ""
    if ext == 'pdf':
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
    elif ext == 'docx':
        doc = Document(filepath)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif ext == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    return text.strip()

def split_text(text):
    # Split by sentences (simple regex)
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    
    chunks = []
    current_chunk = ""
    
    # Asimetría: Primer trozo grande para ganar tiempo, resto pequeños para fluidez
    FIRST_CHUNK_TARGET = 3000 # ~2-2.5 minutos
    NORMAL_CHUNK_TARGET = 1000 # ~45-60 segundos
    
    for s in sentences:
        target = FIRST_CHUNK_TARGET if len(chunks) == 0 else NORMAL_CHUNK_TARGET
        
        if len(current_chunk) + len(s) < target:
            current_chunk += " " + s
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = s
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

# Mapeo de prefijos de voz a idiomas para el frontend
VOICE_LANG_MAP = {
    "af": {"lang": "en-us", "label": "English (US) - Female"},
    "am": {"lang": "en-us", "label": "English (US) - Male"},
    "bf": {"lang": "en-gb", "label": "English (UK) - Female"},
    "bm": {"lang": "en-gb", "label": "English (UK) - Male"},
    "ef": {"lang": "es", "label": "Spanish - Female"},
    "em": {"lang": "es", "label": "Spanish - Male"},
    "ff": {"lang": "fr", "label": "French - Female"},
    "if": {"lang": "it", "label": "Italian - Female"},
    "im": {"lang": "it", "label": "Italian - Male"},
    "jf": {"lang": "ja", "label": "Japanese - Female"},
    "jm": {"lang": "ja", "label": "Japanese - Male"},
    "pf": {"lang": "pt-br", "label": "Portuguese - Female"},
    "pm": {"lang": "pt-br", "label": "Portuguese - Male"},
    "zf": {"lang": "zh", "label": "Chinese - Female"},
    "zm": {"lang": "zh", "label": "Chinese - Male"},
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/extract", methods=["POST"])
def extract():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        text = extract_text_from_file(filepath)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route("/api/split", methods=["POST"])
def split():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"chunks": []})
    chunks = split_text(text)
    return jsonify({"chunks": chunks})

@app.route("/api/voices")
def get_voices():
    all_voices = kokoro.get_voices()
    voices_data = []
    for v in all_voices:
        prefix = v[:2]
        info = VOICE_LANG_MAP.get(prefix, {"lang": "en-us", "label": "Other"})
        voices_data.append({
            "id": v,
            "label": f"{v.replace('_', ' ').title()}",
            "lang": info["lang"],
            "group": info["label"]
        })
    return jsonify(voices_data)

@app.route("/api/speak", methods=["POST"])
def speak():
    data = request.json
    text = data.get("text", "")
    voice = data.get("voice", "af_nicole")
    speed = float(data.get("speed", 1.0))
    lang = data.get("lang", "en-us")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        start_time = time.time()
        samples, sample_rate = kokoro.create(text, voice=voice, speed=speed, lang=lang)
        duration = time.time() - start_time
        
        # Guardar en buffer de memoria
        buffer = io.BytesIO()
        sf.write(buffer, samples, sample_rate, format='WAV')
        buffer.seek(0)
        
        print(f"Generado: '{text[:20]}...' en {duration:.2f}s")
        return send_file(buffer, mimetype="audio/wav", as_attachment=False)
    except Exception as e:
        print(f"Error en generación: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
