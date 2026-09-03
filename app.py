import streamlit as st
import pytesseract
from PIL import Image
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

# Configuración de página
st.set_page_config(
    page_title="LensVoice Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo UI/UX basado en tarjetas oscuras, píldoras y tipografía limpia
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0f1117;
        color: #e2e8f0;
    }
    
    /* Header estilizado */
    .brand-header {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    
    .brand-sub {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    
    /* Paneles y tarjetas */
    .ui-card {
        background-color: #181b24;
        border: 1px solid #262b36;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    /* Personalización de botones */
    .stButton>button {
        background-color: #2563eb;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.6rem 1.2rem;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #1d4ed8;
        border: none;
    }

    /* Píldoras e información */
    .tag-pill {
        display: inline-block;
        background-color: #262b36;
        color: #93c5fd;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

IDIOMAS = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Alemán": "de",
    "Italiano": "it",
    "Portugués": "pt",
    "Japonés": "ja",
    "Chino": "zh-CN"
}

# Configuración del menú lateral
with st.sidebar:
    st.markdown("### Navegación")
    
    opcion_menu = st.radio(
        "Modo de entrada:",
        ["Cámara en vivo", "Archivo de imagen", "Texto directo"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### Configuración")
    
    modo_audio = st.selectbox(
        "Salida de audio:",
        ["Texto traducido", "Texto original (OCR)"]
    )
    
    opcion_idioma = st.selectbox(
        "Idioma destino:",
        list(IDIOMAS.keys()),
        index=0
    )
    codigo_idioma = IDIOMAS[opcion_idioma]
    
    velocidad_lectura = st.checkbox("Velocidad pausada", value=False)

# Encabezado principal
st.markdown('<div class="brand-header">LensVoice Studio</div>', unsafe_allow_html=True)
st.markdown(f'<div class="brand-sub"><span class="tag-pill">Modo</span> {opcion_menu}</div>', unsafe_allow_html=True)

texto_para_procesar = ""
imagen_para_procesar = None

# Opción 1: Cámara
if opcion_menu == "Cámara en vivo":
    st.markdown("#### Captura mediante cámara")
    foto_camara = st.camera_input("Capturar documento", label_visibility="collapsed")
    if foto_camara:
        imagen_para_procesar = Image.open(foto_camara)

# Opción 2: Carga de archivo
elif opcion_menu == "Archivo de imagen":
    st.markdown("#### Cargar archivo de imagen")
    archivo_subido = st.file_uploader("Seleccionar imagen (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    if archivo_subido:
        imagen_para_procesar = Image.open(archivo_subido)

# Opción 3: Entrada directa de texto
elif opcion_menu == "Texto directo":
    st.markdown("#### Entrada de texto")
    texto_ingresado = st.text_area(
        "Escribe o pega el texto para procesar:",
        placeholder="Ingresa aquí el texto...",
        height=160,
        label_visibility="collapsed"
    )
    if texto_ingresado.strip() != "":
        texto_para_procesar = texto_ingresado

# Procesamiento OCR para imágenes
if imagen_para_procesar is not None:
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("#### Vista previa")
        st.image(imagen_para_procesar, use_container_width=True)
    
    with col2:
        st.markdown("#### Extracción OCR")
        with st.spinner("Procesando imagen..."):
            try:
                texto_ocr = pytesseract.image_to_string(imagen_para_procesar)
                if texto_ocr.strip() != "":
                    st.text_area("Texto detectado:", texto_ocr, height=180, label_visibility="collapsed")
                    texto_para_procesar = texto_ocr
                else:
                    st.warning("No se detectó texto legible en la imagen.")
            except Exception as e:
                st.error("Error de inicialización OCR. Verifica la existencia del archivo packages.txt en el repositorio de GitHub.")

# Bloque final de Traducción y Audio
if texto_para_procesar != "":
    st.markdown("---")
    st.markdown("#### Procesamiento de audio y traducción")
    
    if st.button("Generar lectura de audio", use_container_width=True):
        with st.spinner("Sintetizando audio..."):
            try:
                texto_final_audio = texto_para_procesar
                lang_audio = "es"
                
                if modo_audio == "Texto traducido" or opcion_menu == "Texto directo":
                    traductor = GoogleTranslator(source='auto', target=codigo_idioma.lower())
                    texto_traducido = traductor.translate(texto_para_procesar)
                    texto_final_audio = texto_traducido
                    lang_audio = codigo_idioma.lower()
                    
                    st.markdown(f"**Traducción ({opcion_idioma}):**")
                    st.info(texto_final_audio)
                else:
                    st.markdown("**Texto original:**")
                    st.info(texto_final_audio)
                
                tts = gTTS(text=texto_final_audio, lang=lang_audio, slow=velocidad_lectura)
                ruta_audio = "temp_studio_audio.mp3"
                tts.save(ruta_audio)
                
                st.markdown("#### Reproductor")
                with open(ruta_audio, "rb") as f_audio:
                    st.audio(f_audio.read(), format="audio/mp3")
                
                os.remove(ruta_audio)
            except Exception as e:
                st.error(f"Error al procesar la señal de audio: {e}")
