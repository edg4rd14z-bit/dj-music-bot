import streamlit as st
import json
import os
from ytmusicapi import YTMusic

st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- 1. RECUPERACIÓN DE DATOS (SECRETS) ---
# Recuperamos tus datos de los Secrets de Streamlit
c_id = st.secrets.get("mi_client_id", "").strip().replace('"', '')
c_secret = st.secrets.get("mi_client_secret", "").strip().replace('"', '')
r_token = st.secrets.get("mi_refresh_token", "").strip().replace('"', '')

# Verificación de seguridad
if not c_id or not c_secret or not r_token:
    st.error("❌ Faltan datos en los Secrets. Asegúrate de tener: mi_client_id, mi_client_secret, mi_refresh_token")
    st.stop()

# --- 2. LA SOLUCIÓN AL ERROR ---
try:
    # PASO A: Creamos el archivo 'auth.json'
    # Aunque le falten datos, este archivo sirve de base
    datos_base = {
        "refresh_token": r_token,
        "token_type": "Bearer"
    }
    
    with open('auth.json', 'w') as f:
        json.dump(datos_base, f)

    # PASO B: Preparamos las credenciales por separado
    # Esto es EXACTAMENTE lo que pide el error ("oauth_credentials")
    mis_credenciales = {
        "client_id": c_id,
        "client_secret": c_secret
    }

    # PASO C: Conexión Explícita
    # Le pasamos el archivo (1er argumento) Y las credenciales (2do argumento)
    yt = YTMusic('auth.json', oauth_credentials=mis_credenciales)
    
    st.success("✅ ¡CONEXIÓN ESTABLECIDA CON ÉXITO!")

except Exception as e:
    st.error("🛑 Error Final:")
    st.write(e)
    st.stop()

# --- 3. TU APLICACIÓN ---
st.write("---")
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Roadtrip con amigos")
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
                st.warning("No se encontraron canciones.")
        except Exception as e:
            st.error(f"Error creando la lista: {e}")
