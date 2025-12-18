from kokoro_onnx import Kokoro
import json

def list_voices():
    kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    voices = kokoro.get_voices()
    print(f"Voces disponibles: {len(voices)}")
    print(json.dumps(voices, indent=2))

if __name__ == "__main__":
    list_voices()
