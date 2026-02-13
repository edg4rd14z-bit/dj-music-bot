import streamlit as st
import json
import time
from ytmusicapi import YTMusic

st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- 1. RECUPERACIÓN DE DATOS ---
# Limpiamos posibles espacios o comillas extra
c_id = str(st.secrets.get("mi_client_id", "")).strip().replace('"', '')
c_secret = str(st.secrets.get("mi_client_secret", "")).strip().replace('"', '')
r_token = str(st.secrets.get("mi_refresh_token", "")).strip().replace('"', '')

# Verificación de seguridad
if not c_id or not c_secret or not r_token:
    st.error("❌ Faltan credenciales en los Secrets.")
    st.stop()

# --- 2. GENERACIÓN DEL ARCHIVO MAESTRO (SOLUCIÓN TOTAL) ---
# Este diccionario contiene TODOS los campos necesarios para silenciar los errores
datos_maestros = {
    # Credenciales de la App (Lo que pedía el último error)
    "client_id": c_id,
    "client_secret": c_secret,
    
    # Credenciales del Usuario
    "refresh_token": r_token,
    "token_type": "Bearer",
    
    # Campos técnicos (Lo que pedía el error de TypeError anterior)
    # Los ponemos aunque sean "falsos", la librería los actualizará sola
    "scope": "https://www.googleapis.com/auth/youtube",
    "access_token": "token_temporal_relleno",
    "expires_in": 0,
    "expires_at": 0,
    "filepath": ""
}

archivo_oauth = 'oauth_completo.json'

try:
    # Escribimos el archivo completo
    with open(archivo_oauth, 'w') as f:
        json.dump(datos_maestros, f)

    # --- 3. CONEXIÓN ---
    # IMPORTANTE: Llamamos a la librería SOLO con el archivo.
    # Como el archivo ya tiene el client_id y secret dentro, NO usamos oauth_credentials=...
    yt = YTMusic(archivo_oauth)
    
    st.success("✅ ¡CONEXIÓN EXITOSA! (Autenticación completa)")

except Exception as e:
    st.error("🛑 Error inesperado:")
    st.code(str(e))
    # Borramos el archivo temporal por seguridad si falla
    if os.path.exists(archivo_oauth):
        os.remove(archivo_oauth)
    st.stop()

# --- 4. APLICACIÓN ---
st.write("---")
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Cena romántica")
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
                res = yt.search(query, filter="songs", limit=canciones_por_genero)
                for item in res:
                    if 'videoId' in item:
                        video_ids.append(item['videoId'])
                progress_bar.progress((i + 1) / len(lista_busqueda))
            
            if video_ids:
                video_ids = list(set(video_ids))
                nombre = f"Mix: {tematica}"
                pl_id = yt.create_playlist(title=nombre, description=f"Vibe: {tematica}")
                yt.add_playlist_items(pl_id, video_ids)
                
                st.balloons()
                st.success(f"Playlist '{nombre}' creada con {len(video_ids)} canciones.")
            else:
                st.warning("No encontré canciones.")
                
        except Exception as e:
            st.error(f"Error creando la lista: {e}")
