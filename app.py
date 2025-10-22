import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# 🌤️ CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Control por Voz MQTT",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🌈 ESTILOS PERSONALIZADOS (fondo celeste claro + diseño moderno)
st.markdown("""
    <style>
        body {
            background-color: #d6f0ff;
            color: #333;
            font-family: 'Poppins', sans-serif;
        }
        .main {
            background-color: #ffffff;
            border-radius: 25px;
            padding: 40px;
            box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.1);
            margin-top: 40px;
        }
        h1 {
            color: #1a237e;
            text-align: center;
            font-size: 2.8em;
            font-weight: bold;
        }
        h2, h3, h4 {
            color: #3949ab;
        }
        .stButton>button {
            background: linear-gradient(135deg, #7b1fa2, #e91e63);
            color: white;
            border: none;
            border-radius: 12px;
            height: 50px;
            width: 100%;
            font-size: 1.2em;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0px 4px 10px rgba(123, 31, 162, 0.3);
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #9c27b0, #ff4081);
            transform: scale(1.05);
            box-shadow: 0px 6px 15px rgba(156, 39, 176, 0.4);
        }
        .stImage img {
            border-radius: 15px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        }
        .stMarkdown {
            text-align: center;
        }
        .stText {
            text-align: center;
            font-size: 1.1em;
            color: #444;
        }
        .stCaption {
            color: #666;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# 🚀 CONFIGURACIÓN MQTT
def on_publish(client, userdata, result):
    print("El dato ha sido publicado\n")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write("📩 Mensaje recibido:", message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message

# 🎙️ INTERFAZ PRINCIPAL
st.title("🎙️ INTERFACES MULTIMODALES")
st.subheader("CONTROL POR VOZ MQTT")

# Imagen decorativa
image = Image.open('voice_ctrl.jpg')
st.image(image, width=250, caption="Controla dispositivos con tu voz 🗣️")

st.markdown("---")
st.markdown("<h3 style='text-align:center;'>Toca el botón y habla para enviar comandos por voz</h3>", unsafe_allow_html=True)

# 🎤 BOTÓN DE ESCUCHA (BOKEH)
stt_button = Button(label="🎧 Iniciar reconocimiento", width=250)

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

# Escucha los eventos del botón
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# 📡 Envío de comando por voz
if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT").strip()
        st.success(f"🗣️ Comando detectado: **{texto}**")

        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": texto})
        client1.publish("voice_ctrl", message)

        # Crea carpeta temporal si no existe
        try:
            os.mkdir("temp")
        except FileExistsError:
            pass

st.markdown("---")
st.caption("✨ Diseño celeste y moderno | Desarrollado con Streamlit + MQTT + Bokeh")
