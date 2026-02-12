import streamlit as st
import json
import os
from ytmusicapi import YTMusic

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- AUTENTICACIÓN (NUEVO MÉTODO) ---
try:
    # Buscamos la llave 'oauth_raw' que configuraste en los Secrets
    if 'oauth_raw' in st.secrets:
        # Leemos el texto y creamos el archivo oauth.json temporalmente
        with open('oauth.json', 'w') as f:
            f.write(st.secrets['oauth_raw'])
        
        # Conectamos
        yt = YTMusic('oauth.json')
        st.success("Conectado con tu cuenta de Google ✅")
    else:
        st.error("⚠️ No encontré la llave 'oauth_raw' en los Secrets.")
        st.info("Asegúrate de que en Streamlit Secrets pusiste: oauth_raw = \"\"\" ... \"\"\"")
        st.stop()
except Exception as e:
    st.error(f"Error de autenticación: {e}")
    st.stop()

# --- INTERFAZ DE USUARIO ---
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Atardecer en la playa")
    with col2:
        cantidad = st.slider("Cantidad de canciones", 5, 50, 20)

    generos = st.multiselect(
        "Géneros (opcional)",
        ["Pop", "Rock", "Indie", "Hip Hop", "Electronic", "Reggaeton", "Jazz", "Metal", "Lo-Fi", "Latino"]
    )
    
    submitted = st.form_submit_button("🔥 Crear Playlist")

# --- LÓGICA DE CREACIÓN ---
if submitted and tematica:
    with st.spinner('El DJ está buscando las mejores canciones...'):
        video_ids = []
        lista_busqueda = generos if generos else [""]
        canciones_por_genero = max(1, cantidad // len(lista_busqueda))

        try:
            for genero in lista_busqueda:
                query = f"{tematica} {genero}".strip()
                resultados = yt.search(query, filter="songs", limit=canciones_por_genero)
                for track in resultados:
                    video_ids.append(track['videoId'])
            
            if video_ids:
                video_ids = list(set(video_ids)) # Quitar duplicados
                nombre = f"Mix: {tematica}"
                desc = f"Creada con AI DJ. Vibe: {tematica}. Géneros: {', '.join(generos)}"
                
                playlist_id = yt.create_playlist(title=nombre, description=desc)
                yt.add_playlist_items(playlist_id, video_ids)
                
                st.balloons()
                st.success(f"¡Playlist creada con {len(video_ids)} canciones!")
            else:
                st.warning("No encontré canciones. Intenta otra búsqueda.")
        except Exception as e:
            st.error(f"Error al crear la playlist: {e}")
