import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración segura
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en Secrets")

# Nombre del modelo más estable
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🕹️ GameKeeper IA")

foto = st.camera_input("Saca una foto al juego")

if foto:
    img = Image.open(foto)
    try:
        with st.spinner("Identificando videojuego..."):
            # Usamos una lista para pasar el prompt y la imagen
            response = model.generate_content([
                "Identifica este videojuego. Devuelve solo: Nombre (Consola)", 
                img
            ])
            
            if response.text:
                st.success(f"🎮 Encontrado: {response.text}")
                if st.button("Guardar Juego"):
                    st.balloons()
            else:
                st.warning("No se pudo obtener texto de la imagen.")
                
    except Exception as e:
        st.error(f"Error técnico: {e}")
