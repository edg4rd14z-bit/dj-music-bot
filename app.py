import streamlit as st
import json
import os
import time
from ytmusicapi import YTMusic

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- 1. RECUPERACIÓN DE DATOS (Con depuración) ---
st.write("---")
st.subheader("🔌 Estado de Conexión")

try:
    # Usamos st.secrets[] directamente para que avise si falta la variable
    # .strip() y .replace() limpian errores de copiado
    c_id = st.secrets["mi_client_id"].strip().replace('"', '')
    c_secret = st.secrets["mi_client_secret"].strip().replace('"', '')
    r_token = st.secrets["mi_refresh_token"].strip().replace('"', '')
    
    st.caption("✅ Secretos detectados correctamente en Streamlit.")

except KeyError as e:
    st.error(f"❌ Falta la variable {e} en los Secrets de Streamlit.")
    st.stop()

# --- 2. CREACIÓN DEL ARCHIVO MAESTRO (Frankenstein JSON) ---
# Este archivo contiene las 8 llaves que la librería necesita para no fallar
datos_maestros = {
    # Credenciales de la App (Evita error 'credentials not provided')
    "client_id": c_id,
    "client_secret": c_secret,
    
    # Credenciales del Usuario
    "refresh_token": r_token,
    "token_type": "Bearer",
    
    # Datos Técnicos (Evita error 'missing scope/access_token')
    "scope": "https://www.googleapis.com/auth/youtube",
    "access_token": "token_relleno_temporal", # La librería lo actualizará sola
    "expires_in": 0,
    "expires_at": 0,
    "filepath": ""
}

archivo_oauth = 'oauth_final.json'

# Limpiamos caché vieja por si acaso
if os.path.exists(archivo_oauth):
    os.remove(archivo_oauth)

try:
    # Escribimos el archivo nuevo
    with open(archivo_oauth, 'w') as f:
        json.dump(datos_maestros, f)

    # --- 3. CONEXIÓN ---
    # Llamamos a la librería SOLO con el nombre del archivo
    # Como el archivo ya tiene TODO dentro, no pedirá nada más.
    yt = YTMusic(archivo_oauth)
    
    st.success("✅ ¡CONEXIÓN EXITOSA! (Autenticación completa)")

except Exception as e:
    st.error("🛑 Error Crítico:")
    st.code(str(e))
    st.warning("Intenta reiniciar la app (Arriba derecha > Clear Cache > Rerun)")
    st.stop()

# --- 4. FORMULARIO DE DJ ---
st.write("---")
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Gym Motivación")
    with col2:
        cantidad = st.slider("Cantidad", 5, 50, 15)
    
    generos = st.multiselect("Géneros", ["Pop", "Rock", "Reggaeton", "Electronic", "Indie", "Latino", "Metal"])
    submitted = st.form_submit_button("🔥 Crear Playlist")

# --- 5. LÓGICA DE BÚSQUEDA ---
if submitted and tematica:
    with st.spinner(f'Buscando los mejores temas para "{tematica}"...'):
        try:
            video_ids = []
            lista_busqueda = generos if generos else [""]
            canciones_por_genero = max(1, cantidad // len(lista_busqueda))

            progreso = st.progress(0)
            
            for i, genero in enumerate(lista_busqueda):
                query = f"{tematica} {genero}".strip()
                # Búsqueda filtrada por canciones
                res = yt.search(query, filter="songs", limit=canciones_por_genero)
                for item in res:
                    if 'videoId' in item:
                        video_ids.append(item['videoId'])
                progreso.progress((i + 1) / len(lista_busqueda))
            
            if video_ids:
                video_ids = list(set(video_ids))[:cantidad] # Limitar y quitar duplicados
                nombre = f"Mix: {tematica}"
                
                # Crear playlist
                pl_id = yt.create_playlist(title=nombre, description=f"Creado con AI DJ. Vibe: {tematica}")
                
                # Añadir canciones
                yt.add_playlist_items(pl_id, video_ids)
                
                st.balloons()
                st.success(f"¡Playlist '{nombre}' creada con {len(video_ids)} canciones!")
                st.info("Revisa tu YouTube Music en unos segundos.")
            else:
                st.warning("No encontré canciones. Intenta términos más generales.")
                
        except Exception as e:
            st.error(f"Error creando la lista: {e}")
