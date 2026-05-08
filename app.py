import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import requests
import json
from dataclasses import dataclass

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(page_title="GameKeeper IA v2", page_icon="🕹️", layout="wide")

# === ESTILOS CSS PERSONALIZADOS (PARA EL FLIP EFECT) ===
# Este bloque de código CSS crea el efecto visual de la tarjeta que gira al pasar el ratón.
st.markdown("""
<style>
/* Contenedor principal de la cuadrícula */
.games-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    padding: 20px;
}

/* El contenedor principal de la tarjeta (perspectiva) */
.flip-card {
  background-color: transparent;
  width: 100%;
  height: 300px; /* Altura de la carátula */
  perspective: 1000px; /* Necesario para el efecto 3D */
  cursor: pointer;
  margin-bottom: 20px;
}

/* Este contenedor hace el giro real */
.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.8s;
  transform-style: preserve-3d;
  box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
  border-radius: 10px;
}

/* Girar la tarjeta al pasar el ratón (o tocar en móvil) */
.flip-card:hover .flip-card-inner {
  transform: rotateY(180deg);
}

/* Posicionar cara delantera y trasera */
.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden; /* Safari */
  backface-visibility: hidden;
  border-radius: 10px;
  overflow: hidden;
}

/* Estilo Cara Delantera (La Portada) */
.flip-card-front {
  background-color: #bbb;
  color: black;
}
.flip-card-front img {
    width: 100%;
    height: 100%;
    object-fit: cover; /* Ajusta la imagen sin deformar */
}

/* Estilo Cara Trasera (La Contraportada con info) */
.flip-card-back {
  background-color: #1e1e1e; /* Color oscuro de fondo */
  color: white;
  transform: rotateY(180deg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border: 2px solid #ff4b4b; /* Un borde sutil de color */
}

.flip-card-back h3 { margin-top: 0; font-size: 1.1rem; }
.flip-card-back p { font-size: 0.9rem; color: #aaa; margin: 5px 0; }
.flip-card-back .date { font-style: italic; color: #888; font-size: 0.8rem;}

</style>
""", unsafe_with_html=True)


# === DEFINICIÓN DE DATOS ===
@dataclass
class JuegoGuardado:
    titulo_limpio: str
    plataforma: str
    caratula_url: str
    fecha_agregado: str

# === INICIALIZACIÓN DE SESIÓN (MEMORIA TEMPORAL) ===
if 'ludoteca' not in st.session_state:
    st.session_state.ludoteca = []

# === INICIALIZACIÓN DE CLAVES (SECRETS) ===
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-pro-vision')
    
    CLIENT_ID = st.secrets["TWITCH_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["TWITCH_CLIENT_SECRET"]
except Exception as e:
    st.error(f"Error de configuración. Revisa tus Secrets en Streamlit Cloud: {e}")
    st.stop()

# === FUNCIONES DE AYUDA (API IGDB) ===

def obtener_igdb_token():
    """Obtiene un token de acceso temporal de Twitch para usar IGDB."""
    auth_url = "https://id.twitch.tv/oauth2/token"
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(auth_url, params=params)
    return response.json()['access_token']

def buscar_info_juego(nombre_juego, plataforma):
    """Busca en IGDB la carátula oficial y nombre exacto del juego."""
    token = obtener_igdb_token()
    base_url = "https://api.igdb.com/v4/games"
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {token}'
    }
    
    # Query para IGDB: busca el juego, trae nombre, release date y cover.
    # Filtramos para intentar coincidir con la plataforma si es posible.
    query = f"""
    search "{nombre_juego}";
    fields name, first_release_date, cover.url, platforms.name;
    limit 1;
    """
    # Nota: El filtrado exacto por plataforma es complejo en IGDB en una sola búsqueda rápida,
    # traemos el resultado más relevante y Gemini ya nos dio la plataforma.
    
    try:
        response = requests.post(base_url, headers=headers, data=query)
        datos = response.json()
        
        if datos:
            juego_api = datos[0]
            
            # Obtener URL de carátula (cambiar 't_thumb' por 't_cover_big' para calidad media)
            caratula_url = "https://via.placeholder.com/264x352?text=Sin+Portada" # Placeholder por defecto
            if 'cover' in juego_api:
                # La API da urls tipo //images.igdb.com/igdb/image/upload/t_thumb/co1r7h.jpg
                caratula_url = "https:" + juego_api['cover']['url'].replace('t_thumb', 't_cover_big')
                
            return {
                'titulo_oficial': juego_api['name'],
                'caratula_url': caratula_url
            }
    except Exception as e:
        st.warning(f"No se pudo conectar con la base de datos de imágenes (IGDB): {e}")
        
    # Si falla, devolvemos datos vacíos/placeholders
    return {
        'titulo_oficial': nombre_juego,
        'caratula_url': "https://via.placeholder.com/264x352?text=Error+Imagen"
    }

def generar_html_tarjeta(juego: JuegoGuardado):
    """Genera el código HTML para una sola tarjeta flip."""
    html = f"""
    <div class="flip-card">
      <div class="flip-card-inner">
        <div class="flip-card-front">
          <img src="{juego.caratula_url}" alt="Portada de {juego.titulo_limpio}">
        </div>
        <div class="flip-card-back">
          <h3>{juego.titulo_limpio}</h3>
          <p>🎮 {juego.plataforma}</p>
          <p class="date">📅 Agregado: {juego.fecha_agregado}</p>
        </div>
      </div>
    </div>
    """
    return html


# === LÓGICA PRINCIPAL DE LA APP ===

st.title("🕹️ GameKeeper IA v2.0")
st.markdown("Tu estantería visual, al día.")

# Menú lateral
menu = ["Mi Colección (Visual)", "Añadir por Foto"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- PESTAÑA 1: MI COLECCIÓN VISUAL ---
if choice == "Mi Colección (Visual)":
    st.header("📚 Mi Estantería Digital")
    
    if not st.session_state.ludoteca:
        st.info("Tu estantería está vacía. ¡Ve a 'Añadir por Foto'!")
        
        # Ejemplo visual para que el usuario sepa qué esperar (puedes borrar esto luego)
        st.subheader("Ejemplo de cómo se verá:")
        ejemplo = JuegoGuardado(
            "Legacy of Kain: Soul Reaver 1 & 2 Remastered",
            "PS5",
            "https://images.igdb.com/igdb/image/upload/t_cover_big/co7y9a.jpg",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        # st.markdown inyecta el HTML de la tarjeta de ejemplo
        st.markdown(f'<div class="games-grid">{generar_html_tarjeta(ejemplo)}</div>', unsafe_with_html=True)

    else:
        # Generar toda la cuadrícula de juegos
        html_cuadricula = '<div class="games-grid">'
        for juego in st.session_state.ludoteca:
            html_cuadricula += generar_html_tarjeta(juego)
        html_cuadricula += '</div>'
        
        # Inyectar el HTML completo
        st.markdown(html_cuadricula, unsafe_with_html=True)
        
        if st.sidebar.button("⚠️ Borrar Colección (Temporal)"):
            st.session_state.ludoteca = []
            st.rerun()

# --- PESTAÑA 2: AÑADIR JUEGO POR FOTO ---
elif choice == "Añadir por Foto":
    st.header("📸 Escanear Nuevo Juego")
    
    col_cam, col_info = st.columns([1, 1])
    
    with col_cam:
        foto = st.camera_input("Enfoca la portada del juego físico")

    if foto:
        image = Image.open(foto)
        
        with col_info:
            st.write("### Identificando con IA...")
            
            # 1. Usar Gemini Pro Vision para leer el lomo/portada
            try:
                prompt = "Identifica qué videojuego es este y para qué consola. Devuelve SOLO en formato JSON: {'titulo': '...', 'plataforma': '...'}. Ej: {'titulo': 'Elden Ring', 'plataforma': 'PS5'}"
                
                response = model.generate_content([prompt, image])
                
                # Intentar parsear el JSON de Gemini
                try:
                    raw_text = response.text.strip().replace('```json', '').replace('```', '')
                    datos_gemini = json.loads(raw_text)
                    titulo_bruto = datos_gemini.get('titulo', 'Desconocido')
                    plataforma = datos_gemini.get('plataforma', 'Varias')
                except json.JSONDecodeError:
                    # Fallback si Gemini no devuelve JSON limpio
                    st.warning("La IA no devolvió un formato limpio. Usando fallback.")
                    titulo_bruto = response.text.split('(')[0].strip()
                    plataforma = "Varias"
                    
                st.info(f"IA detectó: **{titulo_bruto}** ({plataforma})")
                
                # 2. Usar IGDB para buscar la carátula oficial y limpiar el título
                with st.spinner("Buscando carátula oficial..."):
                    info_oficial = buscar_info_juego(titulo_bruto, plataforma)
                    titulo_final = info_oficial['titulo_oficial']
                    caratula_final = info_oficial['caratula_url']
                
                # 3. Mostrar previsualización
                st.subheader("¿Es este tu juego?")
                cols_prev = st.columns([1, 2])
                with cols_prev[0]:
                    st.image(caratula_final, width=150)
                with cols_prev[1]:
                    st.write(f"**Título:** {titulo_final}")
                    st.write(f"**Plataforma:** {plataforma}")
                
                # 4. Botón para guardar
                if st.button(f"✅ Sí, añadir '{titulo_final}' a mi colección"):
                    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # Crear objeto de datos
                    nuevo_juego = JuegoGuardado(
                        titulo_limpio=titulo_final,
                        plataforma=plataforma,
                        caratula_url=caratula_final,
                        fecha_agregado=fecha_hoy
                    )
                    
                    # Guardar en sesión
                    st.session_state.ludoteca.append(nuevo_juego)
                    st.balloons()
                    st.success(f"¡'{titulo_final}' guardado!")
                    
            except Exception as e:
                st.error(f"Error en el proceso de IA/Base de datos: {e}")
