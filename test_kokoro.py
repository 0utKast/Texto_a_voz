import soundfile as sf
from kokoro_onnx import Kokoro
import time
import os

# Configurar ruta de espeak si es necesario
os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\Program Files\eSpeak NG"

def test_kokoro():
    print("Cargando modelo Kokoro-82M...")
    kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    
    texto = "Hola, esta es una prueba de la voz de inteligencia artificial Kokoro, funcionando totalmente en local."
    voz = "af_nicole" # Voz por defecto inicial para prueba, buscaremos españolas luego
    
    print(f"Generando audio con la voz: {voz}...")
    start_time = time.time()
    
    # Generar audio
    samples, sample_rate = kokoro.create(texto, voice=voz, speed=1.0, lang="en-us")
    
    end_time = time.time()
    print(f"Audio generado en {end_time - start_time:.2f} segundos.")
    
    output_file = "test_kokoro.wav"
    sf.write(output_file, samples, sample_rate)
    print(f"Archivo guardado como {output_file}")

if __name__ == "__main__":
    try:
        test_kokoro()
    except Exception as e:
        print(f"Error: {e}")
