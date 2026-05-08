import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la IA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Falta la clave API en los Secrets")

# Usamos el modelo que vimos en tus capturas (Version 2.5 Flash)
# Nota: Si este falla, cambia el nombre a 'gemini-3.1-flash-lite'
MODEL_NAME = 'gemini-2.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

st.set_page_config(page_title="GameKeeper IA", page_icon="🕹️")
st.title("🕹️ GameKeeper IA")
st.caption(f"Cerebro activo: {MODEL_NAME}")

menu = ["Mi Colección", "Añadir por Foto"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Mi Colección":
    st.info("Tu estantería digital aparecerá aquí.")

elif choice == "Añadir por Foto":
    st.write("### 📸 Escanea tu juego")
    foto = st.camera_input("Saca una foto clara de la portada o el lomo")

    if foto:
        img = Image.open(foto)
        st.image(img, caption="Imagen capturada", width=300)
        
        try:
            with st.spinner("La IA de 2026 está analizando..."):
                # Instrucciones precisas
                prompt = "Identifica este videojuego. Devuelve SOLO: Nombre (Plataforma). Ej: Elden Ring (PS5)"
                
                response = model.generate_content([prompt, img])
                
                if response.text:
                    resultado = response.text
                    st.success(f"🎮 Detectado: **{resultado}**")
                    
                    if st.button("Confirmar y Guardar"):
                        st.balloons()
                        st.write(f"✅ ¡Guardado!")
                else:
                    st.warning("La IA no pudo procesar la imagen.")
                    
        except Exception as e:
            st.error(f"Error técnico: {e}")
            st.info("Si persiste el 404, prueba a cambiar el nombre del modelo en el código por 'gemini-3.1-flash-lite'")
