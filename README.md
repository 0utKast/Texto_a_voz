# Kokoro Pro AI TTS 🚀

¡Un lector de documentos inteligente, persistente, local y gratuito!

Esta aplicación utiliza el modelo de IA **Kokoro-82M** para convertir texto y documentos (PDF, Word, TXT) en voz humana de alta calidad. A diferencia de un simple conversor, esta versión permite **gestionar una biblioteca de lecturas** y retomar tu progreso en cualquier momento.

## ✨ Características Principales

- **Persistencia y Sesiones:** Guarda tus lecturas automáticamente. Cierra la aplicación y vuelve días después; podrás reanudar tu libro exactamente donde lo dejaste.
- **Streaming Fluido (Gapless):** Sistema de doble reproductor optimizado que elimina las pausas entre fragmentos de texto para una lectura continua.
- **Fragmentación Asimétrica:** Genera un primer bloque largo para reproducción inmediata y pre-procesa los siguientes en segundo plano (Buffer dinámico).
- **Gestión de Lecturas:** Barra lateral para organizar tus sesiones, ver el progreso de cada lectura y eliminar las que ya no necesites.
- **Calidad Profesional:** Voces neuronales naturales (español e inglés) comparables a servicios premium.
- **100% Privado y Local:** Tus datos y documentos nunca salen de tu ordenador. Funciona totalmente offline.
- **Sin Costes ni Límites:** Sin suscripciones, sin claves de API, sin límites de caracteres.

## 🛠️ Requisitos

1. **Python 3.10** o superior (Compatible con 3.13).
2. **eSpeak NG:** Necesario para la conversión de fonemas.
   - [Descargar eSpeak NG para Windows](https://github.com/espeak-ng/espeak-ng/releases) (Instalador .msi).

## 🚀 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/0utKast666/Texto_a_voz.git
   cd Texto_a_voz
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Descargar los modelos:**
   Coloca estos archivos en la raíz del proyecto (descárgalos desde [kokoro-onnx releases](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/v1.0)):
   - `kokoro-v1.0.onnx`
   - `voices-v1.0.bin`

4. **Ejecutar:**
   Haz doble clic en `lanzar_app.bat` o ejecuta:
   ```bash
   python app.py
   ```
   Abre `http://127.0.0.1:5000` en tu navegador.

## 📂 Estructura del Proyecto

- `app.py`: Servidor Flask mejorado con endpoints para gestión de sesiones y streaming persistente.
- `manager.py`: Motor compartido para la gestión de proyectos, caché de audio y persistencia de estado.
- `processor.py`: Procesador de texto para extracción inteligente y fragmentación optimizada.
- `templates/index.html`: Interfaz moderna con barra lateral de sesiones y controles de reproducción dinámicos.
- `projects/`: Carpeta (auto-generada) donde se guardan tus sesiones y fragmentos de audio.

---
Creado con ❤️ para amantes de la lectura y la IA abierta.
