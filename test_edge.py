import asyncio
import edge_tts

async def amain() -> None:
    TEXT = "Hola, esta es una prueba de voz de inteligencia artificial."
    VOICE = "es-ES-AlvaroNeural"
    OUTPUT_FILE = "test.mp3"
    
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)
    print(f"File saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    try:
        asyncio.run(amain())
    except Exception as e:
        print(f"Error occurred: {e}")
