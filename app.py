import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la IA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Falta la clave API en los Secrets de Streamlit")

# Nombre del modelo estándar
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Configuración de la App
st.set_page_config(page_title="GameKeeper IA", page_icon="🕹️")
st.title("🕹️ GameKeeper IA")

menu = ["Mi Colección", "Añadir por Foto"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Mi Colección":
    st.info("Tu estantería aparecerá aquí pronto.")

elif choice == "Añadir por Foto":
    st.write("### 📸 Escanea tu juego")
    foto = st.camera_input("Saca una foto clara de la portada o el lomo")

    if foto:
        img = Image.open(foto)
        st.image(img, caption="Imagen para analizar", width=300)
        
        try:
            with st.spinner("La IA está identificando el juego..."):
                # Instrucciones para la IA
                prompt = "Dime el nombre de este videojuego y su consola. Formato: Nombre (Consola). No digas nada más."
                
                # Llamada a la IA
                response = model.generate_content([prompt, img])
                
                if response.text:
                    resultado = response.text
                    st.success(f"🎮 Detectado: **{resultado}**")
                    
                    if st.button("Confirmar y Guardar"):
                        st.balloons()
                        st.write(f"✅ '{resultado}' se ha guardado (en memoria).")
                else:
                    st.warning("La IA no pudo leer la imagen. Prueba con más luz.")
                    
        except Exception as e:
            # Si vuelve a fallar, este mensaje nos dará la pista final
            st.error(f"Error técnico: {e}")
            st.info("Si el error persiste, revisa que tu API Key sea de 'Gemini API' y no de otro servicio de Google.")
