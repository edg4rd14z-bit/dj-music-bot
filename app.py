import streamlit as st
import json
from ytmusicapi import YTMusic

st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- AUTENTICACIÓN A PRUEBA DE FALLOS ---
try:
    # 1. Recuperamos los datos sueltos de los Secrets
    # Usamos .get() para evitar errores si falta alguno
    c_id = st.secrets.get("client_id")
    c_secret = st.secrets.get("client_secret")
    r_token = st.secrets.get("refresh_token")

    if not c_id or not c_secret or not r_token:
        st.error("❌ Faltan credenciales en Streamlit Secrets.")
        st.warning("Asegúrate de tener: client_id, client_secret y refresh_token definidos en el TOML.")
        st.stop()

    # 2. Construimos el JSON CORRECTO manualmente
    # Aquí forzamos los nombres correctos 'client_id' y 'client_secret'
    oauth_credentials = {
        "client_id": c_id,
        "client_secret": c_secret,
        "refresh_token": r_token,
        "token_type": "Bearer"
    }

    # 3. Guardamos el archivo temporalmente
    with open('oauth.json', 'w') as f:
        json.dump(oauth_credentials, f)

    # 4. Iniciamos sesión
    yt = YTMusic('oauth.json')
    st.success("✅ Conexión establecida correctamente")

except Exception as e:
    st.error(f"Error crítico de autenticación: {e}")
    st.stop()

# --- AQUÍ EMPIEZA TU APP NORMAL ---
# (Pega aquí el resto de tu código del formulario y la lógica de búsqueda)
    # ... el resto de tu código ...
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
