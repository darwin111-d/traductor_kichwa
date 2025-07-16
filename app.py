import streamlit as st
from PIL import Image
import pyttsx3
from io import BytesIO
import speech_recognition as sr
import unicodedata
import os
import base64
import sys
import time 
sys.path.append(os.path.join(os.path.dirname(__file__), 'traductor_kichwa'))
try:
    from st_audiorec import st_audiorec
    AUDIOREC_AVAILABLE = True
except ImportError:
    AUDIOREC_AVAILABLE = False

from traductor_kichwa.main import traducir_oracion, normalizar_texto

# === FUNCIONES DE AUDIO ===
@st.cache_resource
def get_tts_engine():
    engine = pyttsx3.init()
    engine.setProperty('rate', 100)      # Más lento (valor típico: 100-150)
    engine.setProperty('volume', 0.8)    # Más suave (0.0 a 1.0)
    engine.setProperty('voice', 'spanish')
    return engine

def text_to_audio(text):
    engine = get_tts_engine()
    temp_filename = 'temp_audio.mp3'
    engine.save_to_file(text, temp_filename)
    engine.runAndWait()
    with open(temp_filename, 'rb') as f:
        audio_bytes = f.read()
    os.remove(temp_filename)  # Elimina el archivo temporal
    return audio_bytes

# Ruta de imágenes
IMGS_PATH = os.path.join(os.path.dirname(__file__), 'traductor_kichwa', 'imagenes')

# Configuración de la página
titulo = "TRADUCTOR ESPAÑOL - KICHWA"
st.set_page_config(page_title=titulo, page_icon="🌎", layout="centered")

# Estilos personalizados
st.markdown(
    f"""
    <style>
    .stApp {{
        background: url('traductor_kichwa/imagenes/banner_v1.png') no-repeat center center fixed
        background-size: cover;
    }}
    .main {{
        background: rgba(255,255,255,0.6); /* overlay blanco más transparente */
        border-radius: 18px;
        padding: 2em 1em;
        box-shadow: 0 4px 32px rgba(0,0,0,0.08);
    }}
    .titulo-principal {{
        font-size: 2.8em;
        font-weight: bold;
        color: var(--primary-color, #1976d2);
        text-align: center;
        margin-bottom: 0.5em;
        letter-spacing: 2px;
        text-shadow: 1px 1px 2px var(--secondary-background-color, #90caf9);
    }}
    .subtitulo {{
        color: var(--secondary-color, #1565c0);
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 2em;
    }}
    .stButton>button {{
        background-color: var(--primary-color, #1976d2);
        color: var(--text-color, #fff);
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5em 2em;
        margin-top: 1em;
        transition: 0.3s;
        box-shadow: 0 2px 8px var(--secondary-background-color, #e3f2fd);
    }}
    .stButton>button:hover {{
        background-color: var(--secondary-color, #1565c0);
        color: var(--text-color, #fffde7);
    }}
    .stTextArea textarea {{
        background: var(--secondary-background-color, #e3f2fd);
        color: var(--text-color, #222);
        border-radius: 8px;
        border: 2px solid var(--primary-color, #90caf9);
        font-size: 1.1em;
        transition: background 0.3s, color 0.3s;
    }}
    .stTextArea textarea:disabled {{
        background: var(--background-color, #f5f5f5);
        color: var(--text-color, #222);
        opacity: 1;
    }}
    .stRadio > div {{
        background: var(--secondary-background-color, #e3f2fd);
        color: var(--text-color, #222);
        border-radius: 8px;
        padding: 0.5em 0.5em;
        margin-bottom: 1em;
        border: 2px solid var(--primary-color, #90caf9);
        transition: background 0.3s, color 0.3s;
    }}
    .stAlert {{
        background: var(--warning-background-color, #fffde7);
        color: var(--text-color, #333);
        border-left: 5px solid #ffd600;
    }}
    hr {{
        border: none;
        border-top: 2px solid var(--primary-color, #90caf9);
    }}
    /* Ajustes para modo oscuro */
    [data-theme="dark"] .stTextArea textarea {{
        background: #23272f !important;
        color: #fff !important;
        border: 2px solid #90caf9 !important;
    }}
    [data-theme="dark"] .stTextArea textarea::placeholder {{
        color: #e0e0e0 !important;
        opacity: 1 !important;
    }}
    [data-theme="dark"] .stTextArea textarea:disabled {{
        background: #18191a !important;
        color: #fff !important;
    }}
    /* Ajustes para modo claro */
    [data-theme="light"] .stTextArea textarea {{
        background: #e3f2fd !important;
        color: #222 !important;
        border: 2px solid #1976d2 !important;
    }}
    [data-theme="light"] .stTextArea textarea::placeholder {{
        color: #666 !important;
        opacity: 1 !important;
    }}
    [data-theme="light"] .stTextArea textarea:disabled {{
        background: #f5f5f5 !important;
        color: #222 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Logo principal junto al título
top_col1, top_col2 = st.columns([1,6])
with top_col1:
    st.image(os.path.join(IMGS_PATH, 'logo_v2.png'), width=90)
with top_col2:
    st.markdown(f'<div class="titulo-principal">{titulo}</div>', unsafe_allow_html=True)

# Subtítulo
descripcion = "Uniendo culturas con innovación."
st.markdown(f'<div class="subtitulo">{descripcion}</div>', unsafe_allow_html=True)

# Instrucciones de uso del traductor
st.markdown('''
<div style="background: #fffde7; border-left: 5px solid #ffd600; padding: 1.2em 1em; border-radius: 10px; margin-bottom: 1.5em; font-size:1.08em;">
📝 <b>Instrucciones para usar el Traductor Español → Kichwa</b><br>
Para obtener resultados correctos en la traducción, siga esta estructura básica:<br>
✅ <b>Estructura recomendada:</b><br>
[Sujeto] + [Verbo conjugado] + [Complemento]<br><br>
🧭 <b>Reglas generales:</b><br>
<ul style="margin-top:0.2em; margin-bottom:0.2em;">
  <li>✅ Use pronombres personales claros:<br>
    <span style="margin-left:1.5em;">yo, tú, él, ella, nosotros, ustedes, ellos</span>
  </li>
  <li>✅ El verbo debe estar conjugado en presente, pasado y futuro</li>
  <li>✅ El complemento debe estar bien escrito, sin abreviaturas ni errores ortográficos.</li>
  <li>✅ Las frases deben evitar abreviaciones o expresiones idiomáticas.</li>
</ul>
📌 <b>Ejemplos correctos:</b><br>
<ul style="margin-top:0.2em; margin-bottom:0.2em;">
  <li>yo juego con mis amigos en la casa</li>
  <li>tú estudias en la universidad</li>
  <li>él va a comer con su familia</li>
</ul>
❌ <b>Errores comunes que debes evitar:</b><br>
<ul style="margin-top:0.2em; margin-bottom:0.2em; color:#d32f2f;">
  <li>❌ Faltan pronombres o están mal escritos → jugamos en la casa</li>
  <li>❌ Verbos sin conjugar → yo jugar casa amigos</li>
</ul>
</div>
''', unsafe_allow_html=True)

# Fondo de marca de agua con la imagen bnner_v4.jpg
st.markdown(
    """
    <style>
    .stApp {
        background: url('traductor_kichwa/imagenes/bnner_v4.jpg') center center no-repeat;
        background-size: 600px auto;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Entrada por voz directa
st.markdown("→ INGRESA EL TEXTO POR ESCRITURA O POR VOZ:")
if st.button("🎤 Escuchar y transcribir voz"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Escuchando... Por favor, habla claramente.")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
        try:
            texto_voz = recognizer.recognize_google(audio, language="es-ES")
            texto_voz = normalizar_texto(texto_voz)
            st.success(f"Texto reconocido: {texto_voz}")
            # Mostrar el texto en el área de texto
            st.session_state["texto_entrada"] = texto_voz
        except sr.UnknownValueError:
            st.error("No se pudo entender el audio.")
        except sr.RequestError:
            st.error("Error al conectar con el servicio de reconocimiento de voz.")

# Área de texto para ingresar el texto a traducir
if "texto_entrada" not in st.session_state:
    st.session_state["texto_entrada"] = ""
if "traduccion" not in st.session_state:
    st.session_state["traduccion"] = ""
if "last_input_time" not in st.session_state:
    st.session_state["last_input_time"] = 0

texto_entrada = st.text_area(
    "Ingresa el texto a traducir:",
    value=st.session_state["texto_entrada"],
    height=120,
    max_chars=500,
    placeholder="Escribe aquí tu texto...",
    key="texto_entrada_area"
)

# Solo botón para traducir
traduccion = ""
traduccion_realizada = False
if st.button("🔄 Traducir", key="btn_traducir"):
    st.session_state["last_input_time"] = time.time()
    try:
        if texto_entrada.strip() == "":
            raise ValueError("Por favor, ingresa una oración para traducir.")
        # Validación mínima: al menos dos palabras
        if len(texto_entrada.strip().split()) < 2:
            raise ValueError("La oración debe tener al menos un sujeto y un verbo.")
        traduccion = traducir_oracion(texto_entrada)
        st.session_state["traduccion"] = traduccion
        traduccion_realizada = True
    except Exception as e:
        # No mostrar nada en el área de traducción ni en la interfaz
        pass
else:
    traduccion = st.session_state["traduccion"]

# Cuadro de texto para mostrar la traducción
st.text_area(
    "Traducción:",
    value=traduccion,
    height=120,
    key="traduccion_area",
    disabled=True
)

# Refrescar la app automáticamente si está esperando traducir
if st.session_state["texto_entrada"].strip() != "" and time.time() - st.session_state["last_input_time"] <= 3:
    st.rerun()

# Botón para escuchar la traducción (ahora justo debajo del cuadro de traducción)
if traduccion:
    if st.button("🔊 Escuchar traducción"):
        audio_bytes = text_to_audio(traduccion)
        audio_b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f'''
            <audio src="data:audio/mp3;base64,{audio_b64}" autoplay style="display:none;"></audio>
        '''
        st.markdown(audio_html, unsafe_allow_html=True)

# Imagen decorativa debajo de los cuadros de texto
st.image(os.path.join(IMGS_PATH, 'banner_2.png'), use_container_width=True)

# Pie de página
footer_col1, footer_col2 = st.columns([1,6])
with footer_col1:
    st.image(os.path.join(IMGS_PATH, 'logo_v1.png'), width=40)
with footer_col2:
    st.markdown("<div style='text-align:left; color:#757575;'>Proyecto estudiantil - M4A | 2025</div>", unsafe_allow_html=True)