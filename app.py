import streamlit as st
import json
import os
from ytmusicapi import YTMusic

st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- ZONA DE DIAGNÓSTICO DE CREDENCIALES ---
st.write("---")
st.subheader("🔍 Verificación de Sistema")

# 1. Intentamos leer los secretos con los nombres nuevos
c_id = st.secrets.get("mi_client_id")
c_secret = st.secrets.get("mi_client_secret")
r_token = st.secrets.get("mi_refresh_token")

# 2. Comprobamos si Streamlit los está leyendo
if not c_id:
    st.error("❌ ERROR: No encuentro 'mi_client_id' en los Secrets.")
    st.stop()
elif not c_secret:
    st.error("❌ ERROR: No encuentro 'mi_client_secret' en los Secrets.")
    st.stop()
elif not r_token:
    st.error("❌ ERROR: No encuentro 'mi_refresh_token' en los Secrets.")
    st.stop()
else:
    st.success("✅ Datos encontrados en Secrets correctamente.")

# 3. Construcción MANUAL del archivo oauth.json
# Esto asegura que las llaves se llamen EXACTAMENTE como la librería exige
datos_json = {
    "client_id": c_id,       # La librería busca "client_id"
    "client_secret": c_secret, # La librería busca "client_secret"
    "refresh_token": r_token, # La librería busca "refresh_token"
    "token_type": "Bearer"
}

# 4. Escribimos el archivo
archivo_auth = 'oauth.json'
try:
    with open(archivo_auth, 'w') as f:
        json.dump(datos_json, f)
    st.info("Archivo de autenticación generado internamente.")
except Exception as e:
    st.error(f"No se pudo escribir el archivo: {e}")
    st.stop()

# --- INTENTO DE CONEXIÓN ---
try:
    # Inicializamos la librería leyendo el archivo que acabamos de crear
    yt = YTMusic(archivo_auth)
    st.success("✨ ¡CONEXIÓN ESTABLECIDA CON GOOGLE! ✨")
    
except Exception as e:
    st.error("🛑 Error Crítico al conectar:")
    st.code(str(e))
    # Si falla, mostramos qué intentó leer (CENSURADO por seguridad)
    st.warning("Debug (Contenido parcial del archivo):")
    st.json({
        "client_id": c_id[:5] + "...", 
        "client_secret": c_secret[:3] + "...",
        "refresh_token": r_token[:10] + "..."
    })
    st.stop()

# --- AQUÍ EMPIEZA LA APP (Solo carga si la conexión funciona) ---
st.write("---")
with st.form("playlist_form"):
    col1, col2 = st.columns(2)
    with col1:
        tematica = st.text_input("Temática / Vibe", placeholder="Ej: Gym Motivación")
    with col2:
        cantidad = st.slider("Cantidad de canciones", 5, 50, 20)

    generos = st.multiselect(
        "Géneros (opcional)",
        ["Pop", "Rock", "Indie", "Hip Hop", "Electronic", "Reggaeton", "Jazz", "Metal", "Lo-Fi", "Latino"]
    )
    
    submitted = st.form_submit_button("🔥 Crear Playlist")

if submitted and tematica:
    with st.spinner('El DJ está trabajando...'):
        try:
            video_ids = []
            lista_busqueda = generos if generos else [""]
            canciones_por_genero = max(1, cantidad // len(lista_busqueda))

            for g in lista_busqueda:
                query = f"{tematica} {g}".strip()
                # Usamos filter='songs' para precisión
                res = yt.search(query, filter="songs", limit=canciones_por_genero)
                for item in res:
                    if 'videoId' in item:
                        video_ids.append(item['videoId'])
            
            if video_ids:
                # Quitamos duplicados
                video_ids = list(set(video_ids))
                nombre = f"Mix: {tematica}"
                desc = f"Creado por AI. Vibe: {tematica}"
                
                pl_id = yt.create_playlist(title=nombre, description=desc)
                yt.add_playlist_items(pl_id, video_ids)
                st.balloons()
                st.success(f"Playlist '{nombre}' creada con {len(video_ids)} canciones.")
            else:
                st.warning("No se encontraron canciones.")
        except Exception as e:
            st.error(f"Error creando la lista: {e}")
