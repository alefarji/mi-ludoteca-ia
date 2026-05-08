import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import requests
import json

# === 1. CONFIGURACIÓN DE SEGURIDAD ===
def inicializar_ia():
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos el modelo 2.5 que es el que tienes activo en 2026
        return genai.GenerativeModel('gemini-2.5-flash')
    except:
        st.error("Error con la clave de Google")
        return None

model = inicializar_ia()

# === 2. DISEÑO CSS (EL "LOOK" DE LAS TARJETAS) ===
# Lo metemos en una variable para que no dé error de lectura
estilo_tarjetas = """
<style>
.games-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px; }
.card { 
    background: #1e1e1e; border-radius: 10px; overflow: hidden; 
    border: 1px solid #333; transition: 0.3s; height: 320px;
}
.card:hover { transform: scale(1.02); border-color: #ff4b4b; }
.card img { width: 100%; height: 200px; object-fit: cover; }
.info { padding: 10px; text-align: center; }
.info h4 { margin: 0; font-size: 0.9rem; color: white; }
.info p { margin: 5px 0; font-size: 0.75rem; color: #888; }
</style>
"""
st.markdown(estilo_tarjetas, unsafe_with_html=True)

# === 3. FUNCIONES DE APOYO (IGDB) ===
def buscar_caratula(nombre):
    try:
        # Pedir token a Twitch
        auth_url = "https://id.twitch.tv/oauth2/token"
        params = {
            'client_id': st.secrets["TWITCH_CLIENT_ID"],
            'client_secret': st.secrets["TWITCH_CLIENT_SECRET"],
            'grant_type': 'client_credentials'
        }
        token = requests.post(auth_url, params=params).json()['access_token']
        
        # Buscar en IGDB
        headers = {'Client-ID': st.secrets["TWITCH_CLIENT_ID"], 'Authorization': f'Bearer {token}'}
        query = f'search "{nombre}"; fields name, cover.url; limit 1;'
        r = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query).json()
        
        if r and 'cover' in r[0]:
            return "https:" + r[0]['cover']['url'].replace('t_thumb', 't_cover_big')
    except:
        pass
    return "https://via.placeholder.com/264x352?text=No+Image"

# === 4. LÓGICA DE LA APP ===
st.title("🕹️ GameKeeper Pro")

if 'ludoteca' not in st.session_state:
    st.session_state.ludoteca = []

menu = ["Mi Colección", "Añadir Juego"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Mi Colección":
    if not st.session_state.ludoteca:
        st.info("Estantería vacía.")
    else:
        # Dibujar las tarjetas
        html_final = '<div class="games-grid">'
        for j in st.session_state.ludoteca:
            html_final += f'''
            <div class="card">
                <img src="{j['img']}">
                <div class="info">
                    <h4>{j['titulo']}</h4>
                    <p>🎮 {j['plataforma']}</p>
                    <p>📅 {j['fecha']}</p>
                </div>
            </div>
            '''
        html_final += '</div>'
        st.markdown(html_final, unsafe_with_html=True)

elif choice == "Añadir Juego":
    foto = st.camera_input("Foto del juego")
    if foto:
        img_pil = Image.open(foto)
        with st.spinner("IA Identificando..."):
            res = model.generate_content(["Dime el nombre del juego y consola. Formato: Nombre (Consola)", img_pil])
            texto = res.text.strip()
            
            # Buscamos la carátula oficial
            url_pro = buscar_caratula(texto.split('(')[0])
            
            st.image(url_pro, width=150)
            st.write(f"**Detectado:** {texto}")
            
            if st.button("Guardar en Colección"):
                nuevo = {
                    "titulo": texto,
                    "plataforma": "Consola",
                    "img": url_pro,
                    "fecha": datetime.datetime.now().strftime("%d/%m/%Y")
                }
                st.session_state.ludoteca.append(nuevo)
                st.success("¡Guardado!")
