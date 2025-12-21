from manager import BatchManager
import os

manager = BatchManager("projects", "kokoro-v1.0.onnx", "voices-v1.0.bin")
project_id = "1766183229_Esta_edición_reúne_por_primera"
chunk_id = 72

print(f"Generando chunk {chunk_id} manualmente...")
try:
    manager.process_chunk(project_id, chunk_id)
    print("Éxito.")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
