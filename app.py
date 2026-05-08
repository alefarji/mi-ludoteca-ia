import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la IA con manejo de errores
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Falta la clave API en los Secrets de Streamlit")

# FUNCIÓN MÁGICA: Busca un modelo disponible que soporte generación de contenido
def obtener_modelo_valido():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Priorizamos gemini-1.5-flash si está en la lista
                if 'gemini-1.5-flash' in m.name:
                    return m.name
        return 'models/gemini-pro-vision' # Plan B antiguo
    except Exception as e:
        return 'gemini-1.5-flash' # Último recurso

nombre_modelo = obtener_modelo_valido()
model = genai.GenerativeModel(nombre_modelo)

# 2. Configuración de la App
st.set_page_config(page_title="GameKeeper IA", page_icon="🕹️")
st.title("🕹️ GameKeeper IA")
st.caption(f"Usando modelo: {nombre_modelo}") # Esto nos dirá qué modelo está usando

menu = ["Mi Colección", "Añadir por Foto"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Mi Colección":
    st.info("Tu estantería aparecerá aquí pronto.")

elif choice == "Añadir por Foto":
    st.write("### 📸 Escanea tu juego")
    foto = st.camera_input("Saca una foto clara")

    if foto:
        img = Image.open(foto)
        st.image(img, caption="Imagen enviada", width=300)
        
        try:
            with st.spinner("La IA está analizando..."):
                prompt = "Dime el nombre de este videojuego y su consola. Formato: Nombre (Consola). Sé directo."
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success(f"🎮 Detectado: **{response.text}**")
                    if st.button("Confirmar y Guardar"):
                        st.balloons()
                else:
                    st.warning("No se recibió respuesta clara.")
        except Exception as e:
            st.error(f"Error técnico: {e}")
            st.info("Revisa si tu API Key tiene restricciones de región en Google Cloud.")
