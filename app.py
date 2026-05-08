import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configurar la IA de Google
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('models/gemini-1.5-flash')

st.set_page_config(page_title="GameKeeper IA", page_icon="🕹️")
st.title("🕹️ GameKeeper IA")

menu = ["Mi Colección", "Añadir por Foto"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Mi Colección":
    st.info("Tu estantería digital aparecerá aquí.")
    # (Aquí luego conectaremos una base de datos real)

elif choice == "Añadir por Foto":
    st.write("### 📸 Escanea tu juego")
    foto = st.camera_input("Enfoca el lomo o la portada")

    if foto:
        img = Image.open(foto)
        st.image(img, caption="Analizando...", width=300)
        
        with st.spinner("Identificando juego..."):
            # La magia: Le enviamos la foto a Gemini con una instrucción clara
            prompt = "Identifica qué videojuego es el de la imagen. Devuelve SOLO el nombre del juego y la plataforma en este formato: Nombre (Plataforma). Si no estás seguro, di 'No reconocido'."
            response = model.generate_content([prompt, img])
            
            resultado = response.text
            st.success(f"He encontrado: **{resultado}**")
            
            if st.button("Guardar en mi colección"):
                st.balloons()
                st.write(f"✅ {resultado} añadido con éxito.")
