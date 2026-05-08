import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la clave API")

st.title("🕹️ GameKeeper: Debug Mode")

# --- BLOQUE DE DIAGNÓSTICO ---
st.write("### 🔍 Modelos disponibles para tu llave:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.code(m.name)
except Exception as e:
    st.error(f"Error al listar modelos: {e}")
# -----------------------------

st.divider()

foto = st.camera_input("Prueba a sacar la foto ahora")

if foto:
    img = Image.open(foto)
    # Intentamos usar el nombre más básico posible
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content(["Identifica el juego: Nombre (Consola)", img])
        st.success(response.text)
    except Exception as e:
        st.error(f"Fallo en la predicción: {e}")
