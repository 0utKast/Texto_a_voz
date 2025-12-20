# Kokoro Pro AI TTS 🚀 (Alpha v0.1.1)

¡Un lector de documentos inteligente, persistente, local y gratuito!

Esta aplicación utiliza el modelo de IA **Kokoro-82M** para convertir texto y documentos (PDF, Word, TXT) en voz humana de alta calidad. A diferencia de un simple conversor, esta versión permite **gestionar una biblioteca de lecturas** y retomar tu progreso en cualquier momento.

## ✨ Características Principales

- **Persistencia y Sesiones:** Guarda tus lecturas automáticamente. Cierra la aplicación y vuelve días después; podrás reanudar tu libro exactamente donde lo dejaste.
- **Streaming Fluido (Alpha-Ready):** Sistema de doble reproductor optimizado que elimina las pausas entre fragmentos de texto para una lectura continua.
- **Conversión de Fondo Continua:** El sistema ahora procesa el documento completo sin detenerse, independientemente de tu posición de lectura.
- **Buffer de Seguridad Inteligente:** Ahora con retroalimentación en tiempo real. Configurado para arrancar rápido y mantener 0 cortes.
- **Gestión de Lecturas Completa:**
  - **Renombrar Sesiones:** Personaliza el título de tus lecturas (ideal para grandes bibliotecas).
  - **Descarga Inteligente:** Descarga el audio total en WAV con el nombre personalizado que elijas.
  - **Borrado Seguro:** Elimina proyectos y sus archivos de audio con un clic.
- **Voces Neuronales Premium:** Incluye voces como "Em Alex" por defecto para una experiencia superior en español.
- **100% Privado y Local:** Funciona totalmente offline, sin costes ni límites.

## 🛠️ Requisitos

1. **Python 3.10+** (Compatible con 3.13).
2. **eSpeak NG:** Necesario para la conversión de fonemas.
   - [Descargar eSpeak NG para Windows](https://github.com/espeak-ng/espeak-ng/releases).

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

3. **Configuración de Modelos:**
   Asegúrate de tener `kokoro-v1.0.onnx` y `voices-v1.0.bin` en la raíz.

4. **Ejecutar:**
   Lanza `lanzar_app.bat` o `python app.py`. Abre `http://127.0.0.1:5000`.

## 📂 Estructura del Proyecto

- `app.py`: Servidor Flask (API REST) para gestión de sesiones y streaming.
- `manager.py`: Motor de procesamiento por lotes y gestión de estado.
- `processor.py`: Extracción de texto y segmentación inteligente.
- `templates/index.html`: UI moderna con feedback dinámico del buffer.

## 📈 Historial de Versiones (Alpha)

- **v0.1.1 (Alpha):**
  - Eliminado el límite de buffer: la conversión ahora es continua hasta el final del documento.
  - Disponibilidad inmediata de descarga: el botón WAV aparece en cuanto termina la conversión, aunque la lectura no haya acabado.

- **v0.1.0 (Alpha):** 
  - Añadida funcionalidad de renombrar sesiones.
  - Sincronización de nombre de archivo en descargas WAV.
  - Mejora drástica en el feedback del buffer (mensajes en tiempo real).
  - Corrección de bugs de autoplay y rutas de audio.
  - Voz "Em Alex" configurada por defecto.

---
Creado con ❤️ por **0utKast** para la comunidad de audiolibros offline.
