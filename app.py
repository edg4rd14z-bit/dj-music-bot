import streamlit as st
import json
import os
from ytmusicapi import YTMusic

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- 2. AUTENTICACIÓN BLINDADA (Auto-Corrección) ---
st.subheader("🔐 Estado de la Conexión")

try:
    # RECUPERAR DATOS (Usamos .get para que no falle si falta alguno)
    # .strip() quita espacios en blanco al inicio/final
    # .replace('"', '') quita comillas extra si se colaron por error
    c_id = str(st.secrets.get("mi_client_id", "")).strip().replace('"', '')
    c_secret = str(st.secrets.get("mi_client_secret", "")).strip().replace('"', '')
    r_token = str(st.secrets.get("mi_refresh_token", "")).strip().replace('"', '')

    # VERIFICACIÓN VISUAL (Solo para ti, censurada por seguridad)
    if not c_id or not c_secret or not r_token:
        st.error("❌ Faltan datos en los Secrets de Streamlit.")
        st.stop()
    
    # CONSTRUCCIÓN DEL JSON LIMPIO
    # Esto asegura que el archivo tenga el formato PERFECTO que exige la librería
    datos_auth = {
        "client_id": c_id,
        "client_secret": c_secret,
        "refresh_token": r_token,
        "token_type": "Bearer"
    }

    # ESCRIBIR EL ARCHIVO TEMPORAL
    archivo_auth = 'auth.json'
    with open(archivo_auth, 'w') as f:
        json.dump(datos_auth, f)

    # CONECTAR CON YOUTUBE MUSIC
    yt = YTMusic(archivo_auth)
    st.success("✅ Conexión establecida correctamente.")

except Exception as e:
    st.error("🛑 Error de Autenticación:")
    st.code(str(e))
    st.warning("Revisa que en tus Secrets de Streamlit tengas los nombres exactos: mi_client_id, mi_client_secret, mi_refresh_token")
    st.stop()

# --- 3. INTERFAZ DE USUARIO ---
st.write("---")
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Gym Motivación, Cena Romántica")
    with col2:
        cantidad = st.slider("Cantidad de canciones", 5, 50, 20)

    generos = st.multiselect(
        "Géneros (opcional)",
        ["Pop", "Rock", "Indie", "Hip Hop", "Electronic", "Reggaeton", "Jazz", "Metal", "Lo-Fi", "Latino"]
    )
    
    submitted = st.form_submit_button("🔥 Crear Playlist")

# --- 4. LÓGICA DEL DJ ---
if submitted and tematica:
    with st.spinner(f'Buscando canciones para "{tematica}"...'):
        try:
            video_ids = []
            lista_busqueda = generos if generos else [""]
            canciones_por_genero = max(1, cantidad // len(lista_busqueda))

            progress_bar = st.progress(0)

            for i, genero in enumerate(lista_busqueda):
                query = f"{tematica} {genero}".strip()
                # Buscamos específicamente CANCIONES (filter='songs')
                try:
                    resultados = yt.search(query, filter="songs", limit=canciones_por_genero)
                    for track in resultados:
                        if 'videoId' in track:
                            video_ids.append(track['videoId'])
                except Exception as search_error:
                    st.warning(f"Error buscando '{genero}': {search_error}")
                
                # Actualizar barra
                progress_bar.progress((i + 1) / len(lista_busqueda))
            
            if video_ids:
                # Eliminar duplicados y mezclar
                video_ids = list(set(video_ids))
                
                nombre_playlist = f"Mix: {tematica}"
                desc = f"Creado con AI DJ. Vibe: {tematica}. Géneros: {', '.join(generos)}"
                
                playlist_id = yt.create_playlist(title=nombre_playlist, description=desc)
                yt.add_playlist_items(playlist_id, video_ids)
                
                st.balloons()
                st.success(f"¡Éxito! Playlist '{nombre_playlist}' creada con {len(video_ids)} canciones.")
                st.info("Revisa tu biblioteca de YouTube Music en unos segundos.")
            else:
                st.warning("No encontré canciones. Intenta términos más generales.")
                
        except Exception as e:
            st.error(f"Error creando la lista: {e}")
