# Kokoro Pro AI TTS 🚀

¡Un lector de documentos inteligente, 100% local, privado y gratuito!

Esta aplicación utiliza el modelo de IA **Kokoro-82M** para convertir texto y documentos (PDF, Word, TXT) en voz humana de alta calidad sin necesidad de conexión a internet ni claves de API.

## ✨ Características

- **Calidad Profesional:** Voces neuronales naturales comparables a servicios de pago.
- **Multiformato:** Carga archivos PDF, DOCX o TXT directamente.
- **Streaming Inteligente:** Empieza a escuchar casi al instante incluso en textos largos.
- **100% Privado:** Tus datos nunca salen de tu ordenador. Funciona totalmente offline.
- **Sin Costes:** Sin suscripciones, sin límites de caracteres, sin publicidad.

## 🛠️ Requisitos

1. **Python 3.10 o superior**
2. **eSpeak NG:** Necesario para la conversión de texto a fonemas.
   - [Descargar eSpeak NG para Windows](https://github.com/espeak-ng/espeak-ng/releases) (Instalador .msi)

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
   Debes descargar los siguientes archivos de la [página de lanzamientos de kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/v1.0) y colocarlos en la raíz del proyecto:
   - `kokoro-v1.0.onnx`
   - `voices-v1.0.bin`

4. **Ejecutar:**
   Haz doble clic en `lanzar_app.bat` o ejecuta en tu terminal:
   ```bash
   python app.py
   ```
   Luego abre `http://127.0.0.1:5000` en tu navegador.

## 📂 Estructura del Proyecto

- `app.py`: Servidor Flask y lógica de procesamiento de IA.
- `templates/index.html`: Interfaz moderna estilo Glassmorphism.
- `lanzar_app.bat`: Lanzador rápido para Windows.
- `informacion.md`: Detalles pedagógicos sobre el proyecto.

---
Creado con ❤️ para el mundo de la IA abierta.
