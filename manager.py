import os
import json
import time
import re
import soundfile as sf
import numpy as np
from kokoro_onnx import Kokoro
import io
import threading

class BatchManager:
    def __init__(self, projects_dir, model_path, voices_path):
        self.projects_dir = projects_dir
        os.makedirs(self.projects_dir, exist_ok=True)
        self.lock = threading.Lock()
        self.project_states = {} # Caché en memoria para evitar lecturas de disco constantes
        
        # Inicializar Kokoro una sola vez
        print(f"Cargando modelo Kokoro desde {model_path}...")
        self.kokoro = Kokoro(model_path, voices_path)
        print("Modelo cargado.")

    def create_project(self, name, chunks, voice, speed, lang):
        # Sanitizar nombre para evitar errores en Windows (caracteres no permitidos: \ / : * ? " < > |)
        clean_name = re.sub(r'[\\/:*?"<>|]', '', name).replace(' ', '_')
        project_id = f"{int(time.time())}_{clean_name}"
        project_path = os.path.join(self.projects_dir, project_id)
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(os.path.join(project_path, "audio_chunks"), exist_ok=True)

        status = {
            "name": name,
            "voice": voice,
            "speed": speed,
            "lang": lang,
            "total_chunks": len(chunks),
            "completed_chunks": 0,
            "is_finished": False,
            "chunks": [{"id": i, "text": text, "status": "pending"} for i, text in enumerate(chunks)]
        }

        with open(os.path.join(project_path, "status.json"), "w", encoding="utf-8") as f:
            json.dump(status, f) # Sin indentación para velocidad
        
        return project_id

    def get_projects(self):
        projects = []
        for pid in os.listdir(self.projects_dir):
            status_path = os.path.join(self.projects_dir, pid, "status.json")
            if os.path.exists(status_path):
                with open(status_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["id"] = pid
                    projects.append(data)
        return projects

    def get_project(self, project_id):
        status_path = os.path.join(self.projects_dir, project_id, "status.json")
        if os.path.exists(status_path):
            with open(status_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["id"] = project_id
                return data
        return None

    def process_chunk(self, project_id, chunk_id):
        project_path = os.path.join(self.projects_dir, project_id)
        status_path = os.path.join(project_path, "status.json")
        chunk_filename = f"chunk_{chunk_id}.wav"
        chunk_path = os.path.join(project_path, "audio_chunks", chunk_filename)

        # FAST-PATH: Si el archivo ya existe en disco, no hacer nada más
        if os.path.exists(chunk_path):
            print(f"Chunk {chunk_id} ya existe en disco. Saltando generación.")
            return chunk_id

        with self.lock:
            # Re-verificar bajo lock por si otro hilo lo terminó justo ahora
            if os.path.exists(chunk_path):
                return chunk_id

            if project_id not in self.project_states:
                with open(status_path, "r", encoding="utf-8") as f:
                    self.project_states[project_id] = json.load(f)
            
            status = self.project_states[project_id]

            # Convertir a dict para búsqueda O(1) si es necesario
            if isinstance(status["chunks"], list):
                status["chunks"] = {str(c["id"]): c for c in status["chunks"]}

            chunk = status["chunks"].get(str(chunk_id))
            
            if not chunk:
                raise ValueError(f"Chunk {chunk_id} not found in project {project_id}")

            if chunk["status"] == "completed" or status.get("is_optimized"):
                return chunk_id

            try:
                # Generar audio con soporte para trozos largos (Auto-splitting)
                # El modelo tiene un límite de ~510 fonemas. 330 chars es un margen ultra-seguo.
                text = chunk["text"]
                max_chars = 330
                
                all_samples = []
                sample_rate = 24000 # Default de Kokoro
                
                # Dividir el texto en mini-trozos por oraciones y puntuación
                def split_text(t, limit):
                    if len(t) <= limit:
                        return [t]
                    
                    # Intentar por puntos
                    parts = re.split(r'(?<=[.!?])\s+', t)
                    if len(parts) > 1:
                        res = []
                        curr = ""
                        for p in parts:
                            if len(curr) + len(p) < limit:
                                curr += " " + p if curr else p
                            else:
                                if curr: res.append(curr)
                                if len(p) > limit:
                                    res.extend(split_text(p, limit)) # Recursivo
                                    curr = ""
                                else:
                                    curr = p
                        if curr: res.append(curr)
                        return res
                    
                    # Intentar por comas, puntos y coma, etc.
                    parts = re.split(r'(?<=[,;:])\s+', t)
                    if len(parts) > 1:
                        res = []
                        curr = ""
                        for p in parts:
                            if len(curr) + len(p) < limit:
                                curr += " " + p if curr else p
                            else:
                                if curr: res.append(curr)
                                if len(p) > limit:
                                    res.extend(split_text(p, limit)) # Recursivo
                                    curr = ""
                                else:
                                    curr = p
                        if curr: res.append(curr)
                        return res
                    
                    # Hard cut como último recurso
                    return [t[i:i+limit] for i in range(0, len(t), limit)]

                sub_chunks = split_text(text, max_chars)
                print(f"Generando chunk {chunk_id} ({len(sub_chunks)} sub-partes seguro) para {project_id}...")
                
                for i, sub_text in enumerate(sub_chunks):
                    print(f"  > Generando sub-parte {i+1}/{len(sub_chunks)}...")
                    samples, sr = self.kokoro.create(
                        sub_text, 
                        voice=status["voice"], 
                        speed=status["speed"], 
                        lang=status["lang"]
                    )
                    all_samples.append(samples)
                    sample_rate = sr
                
                # Concatenar todos los sub-chunks en un solo audio
                combined_samples = np.concatenate(all_samples)
                sf.write(chunk_path, combined_samples, sample_rate)
                
                # Actualizar estado en memoria
                chunk["status"] = "completed"
                # Contar sobre valores del dict
                status["completed_chunks"] = sum(1 for c in status["chunks"].values() if c["status"] == "completed")
                
                # Si era el último, marcar como finalizado si todos están listos
                if status["completed_chunks"] == status["total_chunks"]:
                    status["is_finished"] = True
                    self.assemble_audio(project_id)

                # Persistir a disco sin indentación
                # Nota: Guardamos una copia con chunks como lista para compatibilidad si se lee afuera
                disk_status = status.copy()
                if isinstance(status["chunks"], dict):
                    disk_status["chunks"] = list(status["chunks"].values())

                with open(status_path, "w", encoding="utf-8") as f:
                    json.dump(disk_status, f)
                    
                return chunk_id
            except Exception as e:
                print(f"Error procesando chunk {chunk_id}: {e}")
                chunk["status"] = "error"
                disk_status = status.copy()
                if isinstance(status["chunks"], dict):
                    disk_status["chunks"] = list(status["chunks"].values())
                with open(status_path, "w", encoding="utf-8") as f:
                    json.dump(disk_status, f)
                raise e

    def process_next_chunk(self, project_id):
        project_path = os.path.join(self.projects_dir, project_id)
        status_path = os.path.join(project_path, "status.json")
        
        with open(status_path, "r", encoding="utf-8") as f:
            status = json.load(f)

        if status["is_finished"]:
            return None

        # Buscar el primer chunk pendiente
        next_chunk = None
        for chunk in status["chunks"]:
            if chunk["status"] == "pending":
                next_chunk = chunk
                break
        
        if not next_chunk:
            status["is_finished"] = True
            # Intentar ensamblar si todo está listo
            self.assemble_audio(project_id)
            with open(status_path, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=4)
            return None

        try:
            # Generar audio
            print(f"Procesando chunk {next_chunk['id']} de {status['total_chunks']}...")
            samples, sample_rate = self.kokoro.create(
                next_chunk["text"], 
                voice=status["voice"], 
                speed=status["speed"], 
                lang=status["lang"]
            )
            
            chunk_filename = f"chunk_{next_chunk['id']}.wav"
            chunk_path = os.path.join(project_path, "audio_chunks", chunk_filename)
            sf.write(chunk_path, samples, sample_rate)
            
            # Actualizar estado
            next_chunk["status"] = "completed"
            status["completed_chunks"] += 1
            
            # Si era el último, marcar como finalizado
            if status["completed_chunks"] == status["total_chunks"]:
                status["is_finished"] = True
                self.assemble_audio(project_id)

            with open(status_path, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=4)
                
            return next_chunk["id"]
        except Exception as e:
            print(f"Error procesando chunk {next_chunk['id']}: {e}")
            next_chunk["status"] = "error"
            with open(status_path, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=4)
            raise e

    def assemble_audio(self, project_id):
        project_path = os.path.join(self.projects_dir, project_id)
        audio_chunks_dir = os.path.join(project_path, "audio_chunks")
        output_path = os.path.join(project_path, "final_output.wav")
        status_path = os.path.join(project_path, "status.json")
        
        # Cargar el archivo de estado para saber el orden
        if not os.path.exists(status_path):
            print(f"Error: No se encontró status.json para {project_id}")
            return

        with open(status_path, "r", encoding="utf-8") as f:
            status = json.load(f)

        print(f"Ensamblando audio para {project_id} ({status['total_chunks']} chunks)...")
        
        try:
            # Obtener propiedades del primer chunk para configurar el archivo de salida
            first_chunk_path = os.path.join(audio_chunks_dir, "chunk_0.wav")
            if not os.path.exists(first_chunk_path):
                # Buscar el primer chunk disponible si el 0 no está
                available_chunks = sorted([f for f in os.listdir(audio_chunks_dir) if f.endswith(".wav")])
                if not available_chunks:
                    print("No hay chunks de audio para ensamblar.")
                    return
                first_chunk_path = os.path.join(audio_chunks_dir, available_chunks[0])

            # Leer info del primer chunk
            info = sf.info(first_chunk_path)
            samplerate = info.samplerate
            channels = info.channels
            subtype = info.subtype

            # Abrir el archivo de salida para escritura incremental
            with sf.SoundFile(output_path, mode='w', samplerate=samplerate, channels=channels, subtype=subtype) as outfile:
                for chunk in status["chunks"]:
                    chunk_id = chunk["id"]
                    chunk_path = os.path.join(audio_chunks_dir, f"chunk_{chunk_id}.wav")
                    
                    if os.path.exists(chunk_path):
                        data, sr = sf.read(chunk_path)
                        outfile.write(data)
                    else:
                        print(f"Advertencia: Chunk {chunk_id} no encontrado durante el ensamblado.")

            print(f"Audio final ensamblado exitosamente en: {output_path}")
            
            # Marcar como realmente finalizado solo si el ensamblado tuvo éxito
            if status.get("completed_chunks", 0) >= status.get("total_chunks", 0):
                status["is_finished"] = True
                status["is_optimized"] = True # Marcamos que ya no necesita chunks
                
                with open(status_path, "w", encoding="utf-8") as f:
                    json.dump(status, f, indent=4)
                
                # Eliminar carpeta de chunks para ahorrar espacio
                import shutil
                if os.path.exists(audio_chunks_dir):
                    shutil.rmtree(audio_chunks_dir)
                    print(f"Carpeta de chunks eliminada para {project_id} (Optimizado).")
                    
        except Exception as e:
            print(f"Error crítico durante el ensamblado de audio: {e}")
            # No marcamos como finished si hubo un error en el ensamblado
            raise e

    def delete_project(self, project_id):
        import shutil
        project_path = os.path.join(self.projects_dir, project_id)
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
            print(f"Proyecto {project_id} eliminado.")
            return True
    def rename_project(self, project_id, new_name):
        project_path = os.path.join(self.projects_dir, project_id)
        status_path = os.path.join(project_path, "status.json")
        if os.path.exists(status_path):
            with open(status_path, "r", encoding="utf-8") as f:
                status = json.load(f)
            
            status["name"] = new_name
            
            with open(status_path, "w", encoding="utf-8") as f:
                # Usar indent=4 para que sea legible si el usuario lo abre, 
                # aunque para velocidad podrías omitirlo.
                json.dump(status, f, indent=4)
            
            # Limpiar caché si existe
            if project_id in self.project_states:
                del self.project_states[project_id]
                
            return True
        return False
