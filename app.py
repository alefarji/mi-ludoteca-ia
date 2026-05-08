import streamlit as st
from PIL import Image
import time

# Configuración de la página
st.set_page_config(page_title="GameKeeper IA", page_icon="🕹️")

st.title("🕹️ GameKeeper IA")
st.subheader("Tu colección de juegos, al día")

# Menú lateral
menu = ["Mi Colección", "Añadir por Foto", "Estadísticas"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Mi Colección":
    st.info("Aquí aparecerán tus juegos guardados.")
    # Esto es un ejemplo de cómo se verá
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://via.placeholder.com/150", caption="Zelda: BotW (Switch)")
    with col2:
        st.image("https://via.placeholder.com/150", caption="Elden Ring (PS5)")

elif choice == "Añadir por Foto":
    st.write("### Escanear nuevo juego")
    
    # Este componente abre la cámara en el móvil automáticamente
    foto = st.camera_input("Saca una foto al lomo o portada del juego")

    if foto:
        st.image(foto, caption="Foto capturada")
        with st.spinner("La IA está identificando el juego..."):
            time.sleep(2) # Simulamos el pensamiento de la IA
            st.success("¡Juego detectado: Final Fantasy VII Rebirth!")
            st.button("Confirmar y Guardar en Colección")

elif choice == "Estadísticas":
    st.write("Total de juegos: 2")
    st.progress(50) # Ejemplo de barra de completado
