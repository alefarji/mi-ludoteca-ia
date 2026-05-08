import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import requests
import json

# === 1. CONFIGURACIÓN DE SEGURIDAD ===
# Usamos el modelo que vimos en tus capturas de pantalla
MODELO_ACTIVO = 'gemini-2.5-flash'

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel(MODELO_ACTIVO)
else:
    st.error("Falta la clave API en los Secrets")

# === 2. DISEÑO CSS (CORREGIDO) ===
# Aquí estaba el error. El parámetro correcto es unsafe_allow_html
estilo_visual = """
<style>
.games-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px; }
.card { 
    background: #1e1e1e; border-radius: 10px; overflow: hidden; 
    border: 1px solid #333; transition: 0.3s; height: 350px;
    display: flex; flex-direction: column;
}
.card:hover { transform: translateY(-5px); border-color: #ff4b4b; }
.card img { width: 100%; height: 230px; object-fit: cover; }
.info { padding: 12px; text-align: center; flex-grow: 1; }
.info h4 { margin: 0; font-size: 0.9rem; color: white; line-height: 1.2; }
.info p { margin: 5px 0; font-size: 0.75rem; color: #888; }
</style>
"""
st.markdown(estilo_visual, unsafe_allow_html=True)

# === 3. FUNCIÓN PARA BUSCAR CARÁTULAS (IGDB) ===
def buscar_caratula_oficial(nombre_juego):
    try:
        # 1. Pedir Token
        auth_url = "https://id.twitch.tv/oauth2/token"
        auth_params = {
            'client_id': st.secrets["TWITCH_CLIENT_ID"],
            'client_secret': st.secrets["TWITCH_CLIENT_SECRET"],
            'grant_type': 'client_credentials'
        }
        token_res = requests.post(auth_url, params=auth_params).json()
        token = token_res['access_token']
        
        # 2. Buscar Juego
        headers = {
            'Client-ID': st.secrets["TWITCH_CLIENT_ID"],
            'Authorization': f'Bearer {token}'
        }
        query = f'search "{nombre_juego}"; fields name, cover.url; limit 1;'
        api_res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query).json()
        
        if api_res and 'cover' in api_res[0]:
            # Convertimos la miniatura en imagen de alta calidad
            return "https:" + api_res[0]['cover']['url'].replace('t_thumb', 't_cover_big')
    except:
        pass
    return "https://via.placeholder.com/264x352?text=Sin+Imagen"

# === 4. ESTRUCTURA DE LA APP ===
st.title("🕹️ GameKeeper Pro")

if 'ludoteca' not in st.session_state:
    st.session_state.ludoteca = []

menu = ["Mi Colección", "Escanear Juego"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Mi Colección":
    if not st.session_state.ludoteca:
        st.info("Aún no tienes juegos. ¡Escanea el primero!")
    else:
        # Renderizamos la cuadrícula de tarjetas
        html_grid = '<div class="games-grid">'
        for j in st.session_state.ludoteca:
            html_grid += f'''
            <div class="card">
                <img src="{j['img']}">
                <div class="info">
                    <h4>{j['titulo']}</h4>
                    <p>🎮 {j['plataforma']}</p>
                    <p style="font-style: italic; font-size: 0.65rem;">📅 {j['fecha']}</p>
                </div>
            </div>
            '''
        html_grid += '</div>'
        st.markdown(html_grid, unsafe_allow_html=True)

elif choice == "Escanear Juego":
    foto = st.camera_input("Haz una foto a la portada o lomo")
    
    if foto:
        img_pil = Image.open(foto)
        with st.spinner("La IA está leyendo el juego..."):
            try:
                # Gemini identifica el texto
                res = model.generate_content(["Dime el nombre del juego y la consola. Formato: Nombre (Consola)", img_pil])
                identificado = res.text.strip()
                
                # IGDB busca la imagen profesional
                nombre_solo = identificado.split('(')[0]
                url_portada = buscar_caratula_oficial(nombre_solo)
                
                st.image(url_portada, width=200, caption="Carátula oficial encontrada")
                st.subheader(f"¿Añadir {identificado}?")
                
                if st.button("Confirmar Guardado"):
                    nuevo_item = {
                        "titulo": identificado,
                        "plataforma": "Detectada",
                        "img": url_portada,
                        "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    st.session_state.ludoteca.append(nuevo_item)
                    st.balloons()
                    st.success("¡Guardado en tu estantería!")
            except Exception as e:
                st.error(f"Error: {e}")
