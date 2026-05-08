import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configurar la IA de Google
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la clave API en los Secrets de Streamlit")

# Usamos el nombre completo del modelo
model = genai.GenerativeModel('models/gemini-1.5-flash')

st.set_page_config(page_title="GameKeeper IA", page_icon="🕹️")
st.title("🕹️ GameKeeper IA")

menu = ["Mi Colección", "Añadir por Foto"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Mi Colección":
    st.info("Tu estantería digital aparecerá aquí.")

elif choice == "Añadir por Foto":
    st.write("### 📸 Escanea tu juego")
    foto = st.camera_input("Enfoca el lomo o la portada")

    if foto:
        img = Image.open(foto)
        st.image(img, caption="Imagen capturada", width=300)
        
        try:
            with st.spinner("La IA está analizando la imagen..."):
                prompt = "Analiza esta imagen y dime el nombre del videojuego y su consola. Formato: Nombre (Consola). Si no es un juego, di 'No detectado'."
                # Cambiamos un poco la forma de enviar para evitar errores de red
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success(f"Resultado: **{response.text}**")
                    if st.button("Guardar en mi colección"):
                        st.balloons()
                        st.write("✅ Guardado.")
                else:
                    st.warning("La IA no devolvió texto. Intenta otra foto.")
        except Exception as e:
            st.error(f"Hubo un problema con la IA: {e}")
            st.info("Prueba a revisar si la API Key en Secrets está bien escrita.")
