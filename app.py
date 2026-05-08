import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

# --- CONFIGURACIÓN IA ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Falta la clave API en los Secrets")

MODEL_NAME = 'gemini-2.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

# --- FUNCIONES DE PERSISTENCIA (EL DISCO DURO) ---
archivo_datos = "mis_juegos.json"

def cargar_datos():
    if os.path.exists(archivo_datos):
        with open(archivo_datos, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_datos(lista_juegos):
    with open(archivo_datos, "w", encoding="utf-8") as f:
        json.dump(lista_juegos, f, ensure_ascii=False, indent=4)

# --- CONFIGURACIÓN APP ---
st.set_page_config(page_title="GameKeeper IA", page_icon="🕹️", layout="wide")
st.title("🕹️ GameKeeper IA")

# Inicializamos la sesión con los datos del archivo
if 'coleccion' not in st.session_state:
    st.session_state.coleccion = cargar_datos()

# --- NAVEGACIÓN ---
menu = ["Mi Colección", "Añadir por Foto"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Mi Colección":
    st.header("📚 Mi Estantería Permanente")
    
    if not st.session_state.coleccion:
        st.info("Tu estantería está vacía.")
    else:
        st.success(f"Tienes {len(st.session_state.coleccion)} juegos guardados.")
        # Botón para limpiar (opcional, por si quieres resetear)
        if st.sidebar.button("Borrar toda la colección"):
            st.session_state.coleccion = []
            guardar_datos([])
            st.rerun()

        cols = st.columns(4)
        for i, juego in enumerate(st.session_state.coleccion):
            with cols[i % 4]:
                st.info(juego)

elif choice == "Añadir por Foto":
    st.header("📸 Escanear Nuevo Juego")
    foto = st.camera_input("Haz la foto")

    if foto:
        img = Image.open(foto)
        with st.spinner("Identificando..."):
            try:
                prompt = "Identifica este videojuego. Devuelve SOLO: Nombre (Plataforma)"
                response = model.generate_content([prompt, img])
                resultado = response.text.strip()
                
                st.subheader(f"🎮 {resultado}")
                
                if st.button("Confirmar y Guardar en Disco"):
                    # 1. Añadir a la lista de la pantalla
                    st.session_state.coleccion.append(resultado)
                    # 2. Guardar en el archivo físico
                    guardar_datos(st.session_state.coleccion)
                    
                    st.balloons()
                    st.success("¡Guardado permanentemente!")
            except Exception as e:
                st.error(f"Error: {e}")
