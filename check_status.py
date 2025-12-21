import json
import os

project_id = "1766183229_Esta_edición_reúne_por_primera"
path = rf"c:\proyectos_python\MisApps\Texto_a_voz\projects\{project_id}\status.json"

with open(path, "r", encoding="utf-8") as f:
    status = json.load(f)

print(f"Total: {status['total_chunks']}")
print(f"Completed: {status['completed_chunks']}")
print(f"Is Finished: {status['is_finished']}")

incomplete = [c["id"] for c in status["chunks"] if c["status"] != "completed"]
print(f"Incomplete IDs: {incomplete}")

for cid in incomplete:
    found = any(c["id"] == cid for c in status["chunks"])
    print(f"Chunk {cid} found in list: {found}")
