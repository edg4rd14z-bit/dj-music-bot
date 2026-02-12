import streamlit as st
import json
import time
from ytmusicapi import YTMusic

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- 1. RECUPERACIÓN DE DATOS ---
c_id = st.secrets.get("mi_client_id", "").strip().replace('"', '')
c_secret = st.secrets.get("mi_client_secret", "").strip().replace('"', '')
r_token = st.secrets.get("mi_refresh_token", "").strip().replace('"', '')

if not c_id or not c_secret or not r_token:
    st.error("❌ Faltan credenciales en los Secrets.")
    st.stop()

# --- 2. CREACIÓN DEL ARCHIVO MAESTRO (SOLUCIÓN AL ERROR) ---
try:
    # Aquí está la clave: Le damos TODOS los campos, incluso los que no tenemos
    datos_completos = {
        "client_id": c_id,
        "client_secret": c_secret,
        "refresh_token": r_token,
        "token_type": "Bearer",
        # Estos son los 3 campos que faltaban y provocaban el error:
        "scope": "https://www.googleapis.com/auth/youtube",
        "access_token": "",  # Lo dejamos vacío, la librería lo generará sola
        "expires_in": 0,
        "expires_at": 0
    }

    archivo_oauth = 'oauth_final.json'
    
    # Escribimos el archivo completo
    with open(archivo_oauth, 'w') as f:
        json.dump(datos_completos, f)

    # --- 3. CONEXIÓN ---
    # Ya no necesitamos pasar credenciales aparte, porque el archivo ya las tiene todas
    yt = YTMusic(archivo_oauth)
    st.success("✅ ¡CONEXIÓN EXITOSA! (Sistema listo)")

except Exception as e:
    st.error("🛑 Error inesperado:")
    st.code(str(e))
    st.stop()

# --- 4. FORMULARIO Y LÓGICA ---
st.write("---")
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Correr por la playa")
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
