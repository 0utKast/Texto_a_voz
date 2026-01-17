import os
import json
import threading
import time
import sys

# Añadir el directorio actual al path para importar manager
sys.path.append(os.getcwd())
from manager import BatchManager

# Mock/Setup
PROJECTS_DIR = "test_projects_temp"

# No necesitamos cargar Kokoro real para este test de persistencia
class MockBatchManager(BatchManager):
    def __init__(self, projects_dir):
        self.projects_dir = projects_dir
        os.makedirs(self.projects_dir, exist_ok=True)
        self.lock = threading.Lock()
        self.status_lock = threading.Lock()
        self.project_states = {}
        # Saltamos la carga de Kokoro
        print("[MOCK] Manager inicializado sin Kokoro para pruebas de estado.")

def test_persistence():
    if os.path.exists(PROJECTS_DIR):
        import shutil
        shutil.rmtree(PROJECTS_DIR)
    
    manager = MockBatchManager(PROJECTS_DIR)
    
    # Crear un proyecto de prueba manual
    project_id = "test_project_concurrency"
    project_path = os.path.join(PROJECTS_DIR, project_id)
    os.makedirs(project_path, exist_ok=True)
    
    status = {
        "name": "Libro de Prueba",
        "voice": "af_nicole",
        "speed": 1.0,
        "lang": "en-us",
        "total_chunks": 10,
        "completed_chunks": 0,
        "last_chunk": 0, # Progreso de lectura inicial
        "is_finished": False,
        "chunks": [{"id": i, "text": f"Text fragment {i}", "status": "pending"} for i in range(10)]
    }
    
    with open(os.path.join(project_path, "status.json"), "w", encoding="utf-8") as f:
        json.dump(status, f)

    # Barrera para sincronizar el inicio
    start_event = threading.Event()

    # Simular Hilo 1: Generación de fondo (va marcando completed_chunks)
    def background_generation():
        start_event.wait()
        for i in range(5):
            print(f"  [Hilo Gen] Generando chunk {i}...")
            # Simulamos el comportamiento de process_chunk
            def update_gen(s):
                c = next((ch for ch in s["chunks"] if ch["id"] == i), None)
                if c: c["status"] = "completed"
                s["completed_chunks"] = sum(1 for ch in s["chunks"] if ch["status"] == "completed")
            
            manager._update_project_status(project_id, update_gen)
            time.sleep(0.05) # Simular tiempo de generación

    # Simular Hilo 2: Usuario leyendo (va marcando last_chunk)
    def user_reading():
        start_event.wait()
        for i in range(1, 6):
            print(f"  [Hilo Usuario] Usuario alcanzó chunk {i}...")
            # Simulamos el comportamiento de update_last_chunk
            manager.update_last_chunk(project_id, i)
            time.sleep(0.04) # El usuario es un poco más rápido leyendo que la máquina generando en este test

    t1 = threading.Thread(target=background_generation)
    t2 = threading.Thread(target=user_reading)

    print("Iniciando prueba de concurrencia...")
    t1.start()
    t2.start()
    start_event.set()
    t1.join()
    t2.join()

    # Verificar resultado final cargando de disco
    final_status = manager.get_project(project_id)
    
    print("\n--- RESULTADOS FINALES EN status.json ---")
    print(f"Nombre del proyecto: {final_status['name']}")
    print(f"Progreso de Generación: {final_status['completed_chunks']}/{final_status['total_chunks']}")
    print(f"Progreso de Lectura (last_chunk): {final_status['last_chunk']}")
    
    # Comprobaciones críticas
    # 1. Los completed_chunks deben ser 5 (lo que hizo el hilo de Gen)
    # 2. El last_chunk debe ser 5 (lo que hizo el hilo de Usuario)
    # Si la condición de carrera existiera, uno de los dos habría sobrescrito al otro
    # y veríamos last_chunk=0 (sobrescrito por Gen) o completed_chunks=0 (sobrescrito por Usuario)
    
    success = True
    if final_status['last_chunk'] != 5:
        print("❌ FALLO: El progreso de lectura (last_chunk) se perdió o es incorrecto.")
        success = False
    if final_status['completed_chunks'] != 5:
        print("❌ FALLO: El progreso de generación (completed_chunks) se perdió o es incorrecto.")
        success = False
    
    if success:
        print("\n✅ EXITO: Los cambios concurrentes se fusionaron correctamente en el archivo JSON.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_persistence()
    finally:
        # Limpiar
        import shutil
        if os.path.exists(PROJECTS_DIR):
            shutil.rmtree(PROJECTS_DIR)
