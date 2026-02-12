import streamlit as st
import json
import os
from ytmusicapi import YTMusic

st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- 1. RECUPERACIÓN DE SECRETOS ---
c_id = st.secrets.get("mi_client_id", "").strip().replace('"', '')
c_secret = st.secrets.get("mi_client_secret", "").strip().replace('"', '')
r_token = st.secrets.get("mi_refresh_token", "").strip().replace('"', '')

# Validación rápida
if not c_id or not c_secret or not r_token:
    st.error("❌ Faltan credenciales en los Secrets.")
    st.stop()

# --- 2. LA SOLUCIÓN TÉCNICA (Alimentación Forzada) ---
try:
    # A. Creamos un archivo SOLO con el token (que es lo que varía)
    auth_data = {
        "refresh_token": r_token,
        "token_type": "Bearer"
    }
    
    with open('oauth_token_only.json', 'w') as f:
        json.dump(auth_data, f)

    # B. Preparamos las credenciales en un diccionario separado
    # Esto es lo que la librería estaba pidiendo a gritos
    mis_credenciales = {
        "client_id": c_id,
        "client_secret": c_secret
    }

    # C. CONEXIÓN EXPLÍCITA
    # Le pasamos el archivo del token Y ADEMÁS las credenciales por separado
    yt = YTMusic('oauth_token_only.json', oauth_credentials=mis_credenciales)
    
    st.success("✅ ¡CONEXIÓN ESTABLECIDA! (Por fin)")

except Exception as e:
    st.error("🛑 Error final:")
    st.code(str(e))
    st.stop()

# --- 3. TU APP DE SIEMPRE ---
st.write("---")
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Gym Motivación")
    with col2:
        cantidad = st.slider("Cantidad", 5, 50, 20)
    generos = st.multiselect("Géneros", ["Pop", "Rock", "Reggaeton", "Electronic", "Indie"])
    submitted = st.form_submit_button("🔥 Crear Playlist")

if submitted and tematica:
    with st.spinner('El DJ está trabajando...'):
        try:
            video_ids = []
            lista_busqueda = generos if generos else [""]
            canciones_por_genero = max(1, cantidad // len(lista_busqueda))

            for g in lista_busqueda:
                query = f"{tematica} {g}".strip()
                res = yt.search(query, filter="songs", limit=canciones_por_genero)
                for item in res:
                    if 'videoId' in item:
                        video_ids.append(item['videoId'])
            
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
