# Proyecto Kokoro Pro: El Futuro del TTS Local y Privado

Este documento explica de forma pedagógica cómo hemos construido esta aplicación y qué hay bajo el capó.

## 1. ¿Qué es Kokoro?

**Kokoro-82M** es un modelo de inteligencia artificial de última generación diseñado específicamente para el **Texto a Voz (TTS - Text to Speech)**. 

A diferencia de los sistemas tradicionales que suenan robóticos, Kokoro utiliza redes neuronales para entender el ritmo, la entonación y la emoción del lenguaje. A pesar de su tamaño increíblemente pequeño (82 millones de parámetros, de ahí su nombre), su calidad compite directamente con servicios de pago como ElevenLabs u OpenAI.

### Características Clave:
- **Calidad Premium:** Voces extremadamente naturales y humanas.
- **Eficiencia Local:** Es tan ligero que puede ejecutarse en un ordenador doméstico sin necesidad de tarjetas gráficas profesionales.
- **Multilingüe:** Soporta español, inglés, francés, italiano, japonés, portugués y chino.

## 2. La Filosofía de la App: Privacidad y Gratuidad

El objetivo principal de este proyecto era romper la dependencia de las suscripciones y las nubes corporativas.

- **100% Local:** Todo el procesamiento ocurre en tu CPU. Tus textos nunca viajan por internet.
- **Offline:** No necesitas conexión a internet para convertir texto a voz. Una vez descargada la app, es autónoma.
- **Gratis para siempre:** No hay APIs, no hay cuotas, no hay límites de caracteres.

---

## 3. Estructura y Funcionamiento de la Aplicación

Hemos diseñado la app con una arquitectura de **Cliente-Servidor local**:

### A. El Motor (Backend - `app.py`)
Es el corazón de la aplicación, escrito en **Python**. Sus funciones son:
1. **Gestión del Modelo:** Carga el archivo `.onnx` (el cerebro de la IA) y el archivo de voces `.bin` en la memoria para que la respuesta sea inmediata.
2. **Extracción de Texto:** Utiliza librerías especializadas para "leer" dentro de archivos PDF y Word, limpiando el contenido para la IA.
3. **División Inteligente (Chunking):** Para textos largos, la app separa el contenido en bloques lógicos. Esto nos permite el "streaming": generar el audio de la primera frase mientras la IA todavía está leyendo la segunda.

### B. La Interfaz (Frontend - `index.html`)
Es lo que ves en tu navegador, construida con **HTML5, CSS3 y JavaScript moderno**:
1. **Diseño Glassmorphism:** Una estética moderna con transparencias y desenfoques.
2. **Sistema de Encolado (Queue):** Gestiona la reproducción continua de los bloques de audio para que no notes cortes entre frases.
3. **Unificación de Archivos:** El navegador recibe los trozos de audio y los une en un solo "Blob" maestro para que, al final, puedas descargar un único archivo `.wav` completo.

### C. El Lanzador (`lanzar_app.bat`)
Un pequeño script de Windows que automatiza el proceso técnico, permitiéndote disfrutar de la IA con un simple doble clic.

---

## 4. Flujo de Trabajo (Resumen)

1. **Entrada:** Pegas un texto o cargas un PDF.
2. **Procesamiento:** Python extrae el texto, lo divide y se lo envía al modelo Kokoro.
3. **Generación:** El modelo convierte ondas de sonido digitales a partir del texto.
4. **Reproducción:** El navegador empieza a sonar casi al instante.
5. **Salida:** Obtienes un archivo de audio de alta calidad listo para tus proyectos.

---
*Este proyecto demuestra que no necesitamos estar conectados a la gran nube para tener herramientas potentes de Inteligencia Artificial.*
