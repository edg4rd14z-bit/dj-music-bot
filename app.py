import streamlit as st
import json
import os
from ytmusicapi import YTMusic

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")

st.title("🎵 Generador de Playlists")
st.write("Crea mezclas en tu YouTube Music automáticamente.")

# --- AUTENTICACIÓN SEGURA ---
# Leemos la credencial desde los 'Secretos' de Streamlit, no desde un archivo público
try:
    if 'oauth_json' in st.secrets:
        # Guardamos el secreto en un archivo temporal para que ytmusicapi lo lea
        with open('oauth.json', 'w') as f:
            json.dump(dict(st.secrets['oauth_json']), f)
        yt = YTMusic('oauth.json')
        st.success("Conectado con tu cuenta de Google ✅")
    else:
        st.error("No se encontraron credenciales. Configura los 'Secrets' en Streamlit Cloud.")
        st.stop()
except Exception as e:
    st.error(f"Error de autenticación: {e}")
    st.stop()

# --- INTERFAZ DE USUARIO ---
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Atardecer en la playa, Gym Hardcore")
    
    with col2:
        cantidad = st.slider("Cantidad de canciones", 5, 50, 20)

    generos = st.multiselect(
        "Selecciona Géneros (opcional)",
        ["Pop", "Rock", "Indie", "Hip Hop", "Electronic", "Reggaeton", "Jazz", "Metal", "Lo-Fi", "Latino"],
        default=["Pop"]
    )
    
    submitted = st.form_submit_button("🔥 Crear Playlist")

# --- LÓGICA DE CREACIÓN ---
if submitted and tematica:
    with st.spinner('El DJ está buscando las mejores canciones...'):
        video_ids = []
        
        # Si no elige géneros, usamos solo la temática
        lista_busqueda = generos if generos else [""]
        canciones_por_genero = max(1, cantidad // len(lista_busqueda))

        progress_bar = st.progress(0)
        
        for i, genero in enumerate(lista_busqueda):
            query = f"{tematica} {genero}".strip()
            try:
                # Buscamos canciones
                resultados = yt.search(query, filter="songs", limit=canciones_por_genero)
                for track in resultados:
                    video_ids.append(track['videoId'])
            except Exception as e:
                st.warning(f"Error buscando {genero}: {e}")
            
            # Actualizar barra de progreso
            progress_bar.progress((i + 1) / len(lista_busqueda))

        if video_ids:
            # Eliminar duplicados si los hubiera
            video_ids = list(set(video_ids))
            
            nombre_playlist = f"Mix: {tematica} ({', '.join(generos)})"
            try:
                playlist_id = yt.create_playlist(
                    title=nombre_playlist, 
                    description=f"Creada con AI DJ. Vibe: {tematica}. Géneros: {generos}"
                )
                yt.add_playlist_items(playlist_id, video_ids)
                
                st.balloons()
                st.success(f"¡Playlist creada con {len(video_ids)} canciones!")
                st.info("Ve a tu app de YouTube Music, aparecerá en 'Biblioteca' en unos segundos.")
            except Exception as e:
                st.error(f"Error creando la playlist: {e}")
        else:
            st.warning("No encontré canciones. Intenta palabras clave más simples.")
