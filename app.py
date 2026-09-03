import streamlit as st
import pytesseract
from PIL import Image
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

# 1. Configuración de la página
st.set_page_config(
    page_title="LensVoice: OCR-AUDIO Multimodal",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .gradient-header {
        background: linear-gradient(90deg, #ff4b4b 0%, #ff8c42 50%, #4b9cd3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.6rem !important;
        font-weight: 800 !important;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #a0aec0;
        font-size: 1.05rem;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

IDIOMAS = {
    "Español 🇪🇸": "es",
    "Inglés 🇺🇸": "en",
    "Francés 🇫🇷": "fr",
    "Alemán 🇩🇪": "de",
    "Italiano 🇮🇹": "it",
    "Portugués 🇵🇹": "pt",
    "Japonés 🇯🇵": "ja",
    "Chino (Simplificado) 🇨🇳": "zh-CN"
}

# 2. BARRA LATERAL (Sidebar): Navegación y Ajustes
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=600&auto=format&fit=crop", use_container_width=True)
    st.title("🧩 Menú Principal")
    
    opcion_menu = st.radio(
        "Selecciona el modo de interacción:",
        [
            "📸 Cámara en Vivo (OCR-AUDIO)",
            "📁 Cargar Imagen (OCR-AUDIO)",
            "✍️ Texto Directo"
        ]
    )
    
    st.markdown("---")
    st.subheader("⚙️ Opciones de Audio y Traducción")
    
    modo_audio = st.selectbox(
        "Modo de reproducción de audio:",
        ["Audio del Texto Traducido", "OCR-AUDIO (Texto Original en Foto)"]
    )
    
    opcion_idioma = st.selectbox("Idioma de Destino (para Traducción):", list(IDIOMAS.keys()), index=0)
    codigo_idioma = IDIOMAS[opcion_idioma]
    
    velocidad_lectura = st.checkbox("Lectura Lenta / Pausada", value=False)

# Encabezado dinámico
st.markdown('<h1 class="gradient-header">🎙️ LensVoice: Sistema OCR-AUDIO</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-title">Modo activo: <b>{opcion_menu}</b></p>', unsafe_allow_html=True)

texto_para_procesar = ""
imagen_para_procesar = None

# OPCIÓN 1: CÁMARA EN VIVO
if opcion_menu == "📸 Cámara en Vivo (OCR-AUDIO)":
    st.subheader("📸 Captura con Cámara (OCR-AUDIO)")
    st.write("Toma una foto a cualquier letrero, documento o libro para convertirlo a voz:")
    foto_camara = st.camera_input("Capturar foto desde tu cámara")
    if foto_camara:
        imagen_para_procesar = Image.open(foto_camara)

# OPCIÓN 2: CARGAR IMAGEN
elif opcion_menu == "📁 Cargar Imagen (OCR-AUDIO)":
    st.subheader("📁 Subir Archivo de Imagen (OCR-AUDIO)")
    st.write("Carga una imagen en formato JPG, PNG o JPEG que contenga texto:")
    archivo_subido = st.file_uploader("Selecciona la imagen desde tu equipo", type=["png", "jpg", "jpeg"])
    if archivo_subido:
        imagen_para_procesar = Image.open(archivo_subido)

# OPCIÓN 3: TEXTO DIRECTO
elif opcion_menu == "✍️ Texto Directo":
    st.subheader("✍️ Entrada de Texto a Voz")
    texto_ingresado = st.text_area(
        "Escribe o pega el texto que deseas sintetizar en audio:",
        placeholder="Ejemplo: Hola, bienvenidos a la aplicación multimodal de OCR y voz...",
        height=180
    )
    if texto_ingresado.strip() != "":
        texto_para_procesar = texto_ingresado

# PROCESAMIENTO OCR
if imagen_para_procesar is not None:
    col1, col2 = st.columns([1, 1], gap="medium")
    with col1:
        st.markdown("#### 🖼️ Vista Previa")
        st.image(imagen_para_procesar, caption="Imagen seleccionada", use_container_width=True)
    
    with col2:
        st.markdown("#### 🔍 Lectura de Texto (OCR)")
        with st.spinner("Procesando caracteres con Tesseract OCR..."):
            try:
                texto_ocr = pytesseract.image_to_string(imagen_para_procesar)
                if texto_ocr.strip() != "":
                    st.success("¡Texto extraído con éxito por OCR!")
                    st.text_area("Texto Detectado en Imagen:", texto_ocr, height=180)
                    texto_para_procesar = texto_ocr
                else:
                    st.warning("No se pudo detectar texto legible en la imagen.")
            except Exception as e:
                st.error(f"Error al ejecutar OCR: {e}")

# BLOQUE MULTIMODAL DE TRADUCCIÓN Y AUDIO
if texto_para_procesar != "":
    st.markdown("---")
    st.subheader("🔊 Generador OCR-AUDIO y Traducción")
    
    if st.button("🚀 Procesar y Generar OCR-AUDIO", use_container_width=True, type="primary"):
        with st.spinner("Sintetizando señal de audio..."):
            try:
                texto_final_audio = texto_para_procesar
                lang_audio = "es"
                
                if modo_audio == "Audio del Texto Traducido" or opcion_menu == "✍️ Texto Directo":
                    # Traducción con deep-translator
                    traductor = GoogleTranslator(source='auto', target=codigo_idioma.lower())
                    texto_traducido = traductor.translate(texto_para_procesar)
                    texto_final_audio = texto_traducido
                    lang_audio = codigo_idioma.lower()
                    
                    st.markdown(f"**Texto Traducido ({opcion_idioma}):**")
                    st.info(texto_final_audio)
                else:
                    st.markdown("**Texto Original (OCR-AUDIO):**")
                    st.info(texto_final_audio)
                
                # Generación de archivo MP3
                tts = gTTS(text=texto_final_audio, lang=lang_audio, slow=velocidad_lectura)
                ruta_audio = "temp_ocr_audio.mp3"
                tts.save(ruta_audio)
                
                st.markdown("#### 🎧 Reproductor de Audio (OCR-AUDIO):")
                with open(ruta_audio, "rb") as f_audio:
                    st.audio(f_audio.read(), format="audio/mp3")
                
                os.remove(ruta_audio)
            except Exception as e:
                st.error(f"Ocurrió un error al procesar el módulo OCR-AUDIO: {e}")
