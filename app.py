import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración segura
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en Secrets")

# Usamos la versión 'latest' para evitar el error 404
model = genai.GenerativeModel('gemini-1.5-flash-latest')

st.title("🕹️ GameKeeper IA")

foto = st.camera_input("Saca una foto al juego")

if foto:
    img = Image.open(foto)
    try:
        with st.spinner("Identificando..."):
            # Enviamos la imagen y el texto
            response = model.generate_content([
                "Identifica este videojuego. Devuelve solo: Nombre (Consola)", 
                img
            ])
            st.success(f"Encontrado: {response.text}")
            if st.button("Guardar Juego"):
                st.balloons()
    except Exception as e:
        st.error(f"Error: {e}")
