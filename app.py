import os
import json
import io
import time
import re
import soundfile as sf
import numpy as np
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename

from manager import BatchManager
from processor import TextProcessor

# Configurar ruta de espeak-ng para Windows
ESPEAK_PATH = r"C:\Program Files\eSpeak NG"
os.environ["PHONEMIZER_ESPEAK_PATH"] = ESPEAK_PATH

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROJECTS_FOLDER'] = 'projects'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROJECTS_FOLDER'], exist_ok=True)

# Inicializar Manager y Processor
# Nota: manager inicializa Kokoro internamente
MODEL_PATH = "kokoro-v1.0.onnx"
VOICES_PATH = "voices-v1.0.bin"
manager = BatchManager(app.config['PROJECTS_FOLDER'], MODEL_PATH, VOICES_PATH)
processor = TextProcessor()

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
        text = processor.extract_text(filepath)
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
    
    # Usar el procesador con chunk_len asimétrico si se desea, 
    # pero para simplificar usaremos el estándar del procesador
    chunks = processor.split_into_chunks(text)
    return jsonify({"chunks": chunks})

@app.route("/api/voices")
def get_voices():
    # Usar el modelo interno del manager
    all_voices = manager.kokoro.get_voices()
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

@app.route("/api/projects", methods=["GET"])
def get_projects():
    return jsonify(manager.get_projects())

@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project_status(project_id):
    project = manager.get_project(project_id)
    if project:
        return jsonify(project)
    return jsonify({"error": "Project not found"}), 404

@app.route("/api/projects/create", methods=["POST"])
def create_project():
    data = request.json
    name = data.get("name", "Documento")
    text = data.get("text", "")
    voice = data.get("voice", "af_nicole")
    speed = float(data.get("speed", 1.0))
    lang = data.get("lang", "en-us")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Usar el nuevo split asimétrico: 4000 caracteres para el primero, el resto 2500
    chunks = processor.split_into_chunks(text, target_len=2500, first_chunk_len=4000)
    project_id = manager.create_project(name, chunks, voice, speed, lang)
    return jsonify({"project_id": project_id, "chunks": chunks})

@app.route("/api/projects/<project_id>/chunk/<int:chunk_id>/prepare", methods=["POST"])
def prepare_chunk(project_id, chunk_id):
    try:
        manager.process_chunk(project_id, chunk_id)
        return jsonify({"status": "ready", "chunk_id": chunk_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<project_id>/delete", methods=["DELETE"])
def delete_project(project_id):
    try:
        if manager.delete_project(project_id):
            return jsonify({"status": "deleted", "project_id": project_id})
        else:
            return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/projects/<project_id>/rename", methods=["POST"])
def rename_project(project_id):
    data = request.json
    new_name = data.get("name")
    if not new_name:
        return jsonify({"error": "No name provided"}), 400
    
    try:
        if manager.rename_project(project_id, new_name):
            return jsonify({"status": "renamed", "project_id": project_id, "new_name": new_name})
        else:
            return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<project_id>/chunk/<int:chunk_id>")
def get_chunk_audio(project_id, chunk_id):
    # Intentar obtener el chunk del disco si ya existe
    project_path = os.path.join(app.config['PROJECTS_FOLDER'], project_id)
    chunk_path = os.path.join(project_path, "audio_chunks", f"chunk_{chunk_id}.wav")

    if os.path.exists(chunk_path):
        return send_file(chunk_path, mimetype="audio/wav")

    # Si no existe, generarlo (esta es la parte "on-demand" del streaming persistente)
    try:
        # Nota: manager.process_next_chunk procesa el SIGUIENTE pendiente.
        # Pero aquí queremos un chunk específico. Necesitamos un método para eso.
        # Por simplicidad, si estamos en streaming, solemos ir en orden.
        # Pero para ser robustos, añadiremos un método 'process_specific_chunk' al manager.
        # O simplemente usamos el mecanismo de 'process_next_chunk' si el ID coincide.
        
        # Por ahora, usemos el manager para generar este chunk específico.
        # Modificaré manager.py para añadir process_chunk(pid, cid)
        manager.process_chunk(project_id, chunk_id)
        return send_file(chunk_path, mimetype="audio/wav")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<project_id>/download")
def download_project_audio(project_id):
    project_path = os.path.join(app.config['PROJECTS_FOLDER'], project_id)
    final_path = os.path.join(project_path, "final_output.wav")
    status_path = os.path.join(project_path, "status.json")
    
    # Intentar obtener el nombre personalizado del status.json
    custom_name = project_id
    if os.path.exists(status_path):
        try:
            with open(status_path, "r", encoding="utf-8") as f:
                status = json.load(f)
                custom_name = status.get("name", project_id)
                # Sanitizar para nombre de archivo
                custom_name = re.sub(r'[\\/:*?"<>|]', '', custom_name).strip()
                if not custom_name: custom_name = project_id
        except:
            pass

    if os.path.exists(final_path):
        return send_file(final_path, as_attachment=True, download_name=f"{custom_name}.wav", mimetype="audio/wav")
    
    # Si no existe, ver si el proyecto está terminado para ensamblarlo
    if os.path.exists(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
            status = json.load(f)
        
        # Robustez: Aceptar si el flag está activo O si los contadores coinciden
        total = status.get("total_chunks", 999999)
        completed = status.get("completed_chunks", 0)
        
        if status.get("is_finished") or (completed >= total):
            manager.assemble_audio(project_id)
            if os.path.exists(final_path):
                return send_file(final_path, as_attachment=True, download_name=f"{custom_name}.wav", mimetype="audio/wav")

    return jsonify({"error": "Audio not ready for download. Please wait until conversion finishes."}), 404

@app.route("/api/speak", methods=["POST"])
def speak():
    # Mantener compatibilidad con el modo "usar sin guardar" si se desea
    data = request.json
    text = data.get("text", "")
    voice = data.get("voice", "af_nicole")
    speed = float(data.get("speed", 1.0))
    lang = data.get("lang", "en-us")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        samples, sample_rate = manager.kokoro.create(text, voice=voice, speed=speed, lang=lang)
        buffer = io.BytesIO()
        sf.write(buffer, samples, sample_rate, format='WAV')
        buffer.seek(0)
        return send_file(buffer, mimetype="audio/wav")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
