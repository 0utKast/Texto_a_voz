import soundfile as sf
from kokoro_onnx import Kokoro
import time
import os

os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\Program Files\eSpeak NG"

def test_spanish():
    print("Cargando modelo Kokoro-82M...")
    kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    
    # 'ef' es el prefijo para español (es-ES) en Kokoro
    texto = "¡Hola! Estoy muy contento de saludarte. Esta es una voz de inteligencia artificial de alta calidad ejecutándose en tu ordenador de forma local. ¿Qué te parece el sonido?"
    voz = "ef_dora" 
    
    print(f"Generando audio en ESPAÑOL con la voz: {voz}...")
    start_time = time.time()
    
    # Importante: usar lang="es" para español
    samples, sample_rate = kokoro.create(texto, voice=voz, speed=1.1, lang="es")
    
    end_time = time.time()
    print(f"Audio generado en {end_time - start_time:.2f} segundos.")
    
    output_file = "test_spanish.wav"
    sf.write(output_file, samples, sample_rate)
    print(f"Archivo guardado como {output_file}")

if __name__ == "__main__":
    try:
        test_spanish()
    except Exception as e:
        print(f"Error: {e}")
