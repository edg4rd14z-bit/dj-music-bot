import streamlit as st
import json
import time
from ytmusicapi import YTMusic

st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- 1. RECUPERACIÓN DE DATOS BLINDADA ---
# Recuperamos y limpiamos las credenciales de Streamlit Secrets
c_id = str(st.secrets.get("mi_client_id", "")).strip().replace('"', '')
c_secret = str(st.secrets.get("mi_client_secret", "")).strip().replace('"', '')
r_token = str(st.secrets.get("mi_refresh_token", "")).strip().replace('"', '')

# Verificación de seguridad
if not c_id or not c_secret or not r_token:
    st.error("❌ Faltan credenciales en los Secrets.")
    st.info("Asegúrate de configurar: mi_client_id, mi_client_secret, mi_refresh_token")
    st.stop()

# --- 2. LA SOLUCIÓN "FRANKENSTEIN" (Relleno Total) ---
# Aquí fabricamos un archivo con TODOS los campos posibles para evitar errores de "missing arguments"
datos_completos = {
    "client_id": c_id,
    "client_secret": c_secret,
    "refresh_token": r_token,
    "token_type": "Bearer",
    # ESTOS SON LOS CAMPOS QUE FALTABAN Y CAUSABAN EL ERROR:
    "scope": "https://www.googleapis.com/auth/youtube",
    "access_token": "dummy_token", # Ponemos un valor falso temporal para que no falle al iniciar
    "expires_in": 0,
    "expires_at": 0
}

archivo_oauth = 'oauth_completo.json'

try:
    # Escribimos el archivo maestro
    with open(archivo_oauth, 'w') as f:
        json.dump(datos_completos, f)

    # --- 3. CONEXIÓN DIRECTA ---
    # Ya no usamos 'oauth_credentials=' porque el archivo ya lo tiene TODO.
    yt = YTMusic(archivo_oauth)
    
    st.success("✅ ¡CONEXIÓN EXITOSA! (Sistema operativo)")

except Exception as e:
    st.error("🛑 Error inesperado:")
    st.code(str(e))
    st.stop()

# --- 4. INTERFAZ DE USUARIO ---
st.write("---")
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Gym Motivación")
    with col2:
        cantidad = st.slider("Cantidad", 5, 50, 15)
    
    generos = st.multiselect("Géneros", ["Pop", "Rock", "Reggaeton", "Electronic", "Indie", "Latino"])
    submitted = st.form_submit_button("🔥 Crear Playlist")

if submitted and tematica:
    with st.spinner('El DJ está mezclando...'):
        try:
            video_ids = []
            lista_busqueda = generos if generos else [""]
            canciones_por_genero = max(1, cantidad // len(lista_busqueda))

            progress_bar = st.progress(0)
            
            for i, genero in enumerate(lista_busqueda):
                query = f"{tematica} {genero}".strip()
                # Buscamos canciones
                res = yt.search(query, filter="songs", limit=canciones_por_genero)
                for item in res:
                    if 'videoId' in item:
                        video_ids.append(item['videoId'])
                progress_bar.progress((i + 1) / len(lista_busqueda))
            
            if video_ids:
                video_ids = list(set(video_ids))
                nombre = f"Mix: {tematica}"
                # Creamos la playlist
                pl_id = yt.create_playlist(title=nombre, description=f"Creado con AI. Vibe: {tematica}")
                # Añadimos canciones
                yt.add_playlist_items(pl_id, video_ids)
                
                st.balloons()
                st.success(f"Playlist '{nombre}' creada con {len(video_ids)} canciones.")
                st.info("Revisa tu YouTube Music en unos segundos.")
            else:
                st.warning("No encontré canciones para esa búsqueda.")
                
        except Exception as e:
            st.error(f"Error creando la lista: {e}")
