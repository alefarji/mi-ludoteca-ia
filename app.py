import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN IA ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Falta la clave API en los Secrets")

MODEL_NAME = 'gemini-2.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

# --- CONFIGURACIÓN APP ---
st.set_page_config(page_title="GameKeeper IA", page_icon="🕹️", layout="wide")
st.title("🕹️ GameKeeper IA")
st.caption(f"Cerebro activo: {MODEL_NAME}")

# --- MEMORIA DE LA APP ---
# Si la lista de juegos no existe, la creamos
if 'coleccion' not in st.session_state:
    st.session_state.coleccion = []

# --- MENÚ LATERAL ---
menu = ["Mi Colección", "Añadir por Foto"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- PESTAÑA: MI COLECCIÓN ---
if choice == "Mi Colección":
    st.header("📚 Mi Estantería Digital")
    
    if len(st.session_state.coleccion) == 0:
        st.info("Tu estantería está vacía. ¡Ve a 'Añadir por Foto' para empezar!")
    else:
        st.success(f"Tienes {len(st.session_state.coleccion)} juegos en tu colección.")
        
        # Mostramos los juegos en una cuadrícula bonita
        cols = st.columns(3) # 3 columnas
        for index, juego in enumerate(st.session_state.coleccion):
            # Repartimos los juegos entre las columnas
            with cols[index % 3]: 
                st.markdown(f"**{juego}**")
                st.divider()

# --- PESTAÑA: AÑADIR JUEGO ---
elif choice == "Añadir por Foto":
    st.header("📸 Escanear Juego")
    
    # Creamos dos columnas: una para la cámara y otra para el resultado
    col1, col2 = st.columns(2)
    
    with col1:
        foto = st.camera_input("Enfoca la portada o el lomo")

    if foto:
        img = Image.open(foto)
        
        with col2:
            st.write("### Resultado:")
            try:
                with st.spinner("Analizando..."):
                    prompt = "Identifica este videojuego. Devuelve SOLO: Nombre (Plataforma). Ej: Elden Ring (PS5)"
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        resultado = response.text.strip() # Quitamos espacios extra
                        st.success(f"🎮 {resultado}")
                        
                        # Botón para guardar
                        if st.button("Guardar en mi colección"):
                            # Añadimos a la memoria
                            st.session_state.coleccion.append(resultado)
                            st.balloons()
                            st.write("✅ ¡Guardado!")
                            
                    else:
                        st.warning("No pude identificar el juego.")
            except Exception as e:
                st.error(f"Error al analizar: {e}")
