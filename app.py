import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

# Configuración de página
st.set_page_config(
    page_title="Control por Voz 🎤",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS para darle estilo bonito
st.markdown("""
    <style>
    body {
        background-color: #121212;
    }
    .stApp {
        background: #121212;
        color: #f8f8f2;
    }
    h1, h2, h3 {
        color: #ff69b4;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    .stButton>button {
        background-color: #ff69b4;
        color: white;
        border-radius: 10px;
        height: 50px;
        width: 200px;
        font-size: 18px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff85c1;
        color: white;
    }
    .css-1cpxqw2 {
        background: #2c2c2c;
    }
    </style>
""", unsafe_allow_html=True)

# Funciones MQTT
def on_publish(client, userdata, result): 
    print("✅ Mensaje publicado correctamente.")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.success(f"📥 Mensaje recibido: {message_received}")

# Configuración MQTT
broker = "157.230.214.127"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message

# Interfaz principal
st.title("🎤 Interfaces Multimodales")
st.subheader("✨ Control por Voz ✨")

# Imagen
image = Image.open('voice_ctrl.jpg')
st.image(image, width=300, caption="Controla con tu voz 🎙️")

# Instrucción
st.write("Pulsa el botón y empieza a hablar:")

# Botón de voz
stt_button = Button(label="🎙️ Iniciar Grabación", width=300)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

# Evento para recibir el texto de voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Procesamiento de texto recibido
if result:
    if "GET_TEXT" in result:
        user_text = result.get("GET_TEXT")
        st.success(f"📝 Texto detectado: {user_text}")
        
        # Publicar el mensaje
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": user_text.strip()})
        ret = client1.publish("voice_ctrl", message)
        
        # Crear carpeta temporal si no existe
        try:
            os.mkdir("temp")
        except FileExistsError:
            pass
