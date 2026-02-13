import streamlit as st
import json
import os  # <--- ESTA ERA LA LÍNEA QUE FALTABA
from ytmusicapi import YTMusic

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- 1. RECUPERACIÓN DE DATOS BLINDADA ---
# Recuperamos tus datos de los Secrets de Streamlit
# Usamos .get() para evitar errores si falta alguno
c_id = str(st.secrets.get("mi_client_id", "")).strip().replace('"', '')
c_secret = str(st.secrets.get("mi_client_secret", "")).strip().replace('"', '')
r_token = str(st.secrets.get("mi_refresh_token", "")).strip().replace('"', '')

# Verificación de seguridad: Si falta algo, avisamos y paramos.
if not c_id or not c_secret or not r_token:
    st.error("❌ Faltan credenciales en los Secrets.")
    st.info("Asegúrate de configurar en Streamlit: mi_client_id, mi_client_secret, mi_refresh_token")
    st.stop()

# --- 2. LA SOLUCIÓN MAESTRA (Archivo con TODO incluido) ---
# Creamos un diccionario con LOS 8 CAMPOS que la librería podría pedir.
# Al tener todo aquí dentro, la librería no se quejará de que le falta nada.
datos_maestros = {
    # 1. Credenciales de la App (Para evitar error "oauth_credentials not provided")
    "client_id": c_id,
    "client_secret": c_secret,
    
    # 2. Credenciales del Usuario
    "refresh_token": r_token,
    "token_type": "Bearer",
    
    # 3. Campos técnicos (Para evitar error "missing scope/access_token")
    "scope": "https://www.googleapis.com/auth/youtube",
    "access_token": "token_relleno_temporal", # Valor falso que se actualizará solo
    "expires_in": 0,
    "expires_at": 0,
    "filepath": ""
}

archivo_oauth = 'oauth_completo.json'

try:
    # Escribimos el archivo completo en el disco
    with open(archivo_oauth, 'w') as f:
        json.dump(datos_maestros, f)

    # --- 3. CONEXIÓN ---
    # IMPORTANTE: Llamamos a la librería SOLO con el archivo.
    yt = YTMusic(archivo_oauth)
    
    st.success("✅ ¡CONEXIÓN EXITOSA! (Autenticación completa)")

except Exception as e:
    st.error("🛑 Error inesperado durante la conexión:")
    st.code(str(e))
    # Limpieza de seguridad
    if os.path.exists(archivo_oauth):
        os.remove(archivo_oauth)
    st.stop()

# --- 4. TU APLICACIÓN (Lógica del DJ) ---
st.write("---")
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Gym Motivación")
    with col2:
        cantidad = st.slider("Cantidad de canciones", 5, 50, 15)
    
    generos = st.multiselect("Géneros", ["Pop", "Rock", "Reggaeton", "Electronic", "Indie", "Latino", "Metal", "Jazz"])
    submitted = st.form_submit_button("🔥 Crear Playlist")

if submitted and tematica:
    with st.spinner(f'El DJ está cocinando la playlist de "{tematica}"...'):
        try:
            video_ids = []
            lista_busqueda = generos if generos else [""]
            # Calculamos cuántas canciones buscar por cada género
            canciones_por_genero = max(1, cantidad // len(lista_busqueda))

            progress_bar = st.progress(0)
            
            for i, genero in enumerate(lista_busqueda):
                query = f"{tematica} {genero}".strip()
                # Buscamos canciones
                res = yt.search(query, filter="songs", limit=canciones_por_genero)
                for item in res:
                    if 'videoId' in item:
                        video_ids.append(item['videoId'])
                # Actualizamos barra de progreso
                progress_bar.progress((i + 1) / len(lista_busqueda))
            
            if video_ids:
                # Quitamos duplicados y aseguramos que no exceda el límite
                video_ids = list(set(video_ids))[:cantidad]
                
                nombre = f"Mix: {tematica}"
                # Creamos la playlist vacía
                pl_id = yt.create_playlist(title=nombre, description=f"Creado con AI DJ. Vibe: {tematica}")
                # Le metemos las canciones
                yt.add_playlist_items(pl_id, video_ids)
                
                st.balloons()
                st.success(f"¡Éxito! Playlist '{nombre}' creada con {len(video_ids)} canciones.")
                st.info("Revisa tu biblioteca de YouTube Music en unos segundos.")
            else:
                st.warning("No encontré canciones para esa búsqueda. Intenta términos más generales.")
                
        except Exception as e:
            st.error(f"Error creando la lista: {e}")
