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

# 🎨 ESTILOS (fondo celeste claro + botón con animación)
st.markdown("""
    <style>
        body {
            background-color: #dff6ff;
            color: #2b2b2b;
            font-family: 'Poppins', sans-serif;
        }
        .main {
            background-color: #ffffff;
            border-radius: 25px;
            padding: 40px;
            box-shadow: 0px 4px 25px rgba(0, 0, 0, 0.1);
            margin-top: 40px;
        }
        h1 {
            color: #0d47a1;
            text-align: center;
            font-size: 2.8em;
            font-weight: 800;
        }
        h2, h3, h4 {
            color: #1565c0;
            text-align: center;
        }
        .stImage img {
            border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        }
        .mic-indicator {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: radial-gradient(circle, #e91e63 40%, transparent 41%);
            animation: pulse 1.5s infinite;
            margin: 10px auto;
        }
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.3); opacity: 0.6; }
            100% { transform: scale(1); opacity: 1; }
        }
        .mic-text {
            text-align: center;
            font-weight: bold;
            color: #7b1fa2;
            margin-top: 8px;
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

image = Image.open('voice_ctrl.jpg')
st.image(image, width=250, caption="Controla dispositivos con tu voz 🗣️")

st.markdown("---")
st.markdown("<h3>Toca el botón y habla para enviar comandos por voz</h3>", unsafe_allow_html=True)

# 🎧 BOTÓN DE ESCUCHA
stt_button = Button(label="🎧 Iniciar reconocimiento", width=250)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    document.dispatchEvent(new CustomEvent("LISTENING", {detail: "on"}));

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
    recognition.onend = function() {
        document.dispatchEvent(new CustomEvent("LISTENING", {detail: "off"}));
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT,LISTENING",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# 🎤 INDICADOR DE ESCUCHA
if result and "LISTENING" in result:
    estado = result["LISTENING"]
    if estado == "on":
        st.markdown('<div class="mic-indicator"></div><div class="mic-text">🎙️ Escuchando...</div>', unsafe_allow_html=True)
    elif estado == "off":
        st.markdown('<div class="mic-text">🛑 Reconocimiento detenido</div>', unsafe_allow_html=True)

# 📡 ENVÍO DEL COMANDO POR VOZ
if result and "GET_TEXT" in result:
    texto = result.get("GET_TEXT").strip()
    st.success(f"🔔 Comando detectado: **{texto}**")

    client1.on_publish = on_publish
    client1.connect(broker, port)
    message = json.dumps({"Act1": texto})
    client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except FileExistsError:
        pass

st.markdown("---")
st.caption("💙 Diseño celeste con animación de micrófono | Desarrollado con Streamlit + MQTT + Bokeh")
