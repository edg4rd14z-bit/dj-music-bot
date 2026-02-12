import streamlit as st
import json
import os
from ytmusicapi import YTMusic

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AI DJ Mix", page_icon="🎵")
st.title("🎵 Generador de Playlists")

# --- AUTENTICACIÓN BLINDADA ---
try:
    # 1. Recuperamos datos y limpiamos espacios o comillas extrañas
    c_id = str(st.secrets.get("mi_client_id", "")).strip().replace('"', '')
    c_secret = str(st.secrets.get("mi_client_secret", "")).strip().replace('"', '')
    r_token = str(st.secrets.get("mi_refresh_token", "")).strip().replace('"', '')

    # 2. Verificación rápida
    if len(c_id) < 10 or len(c_secret) < 5:
        st.error("❌ Error en Secrets: Los datos parecen estar vacíos o incompletos.")
        st.stop()

    # 3. CONSTRUCCIÓN MANUAL DEL JSON (La clave del éxito)
    # Aquí forzamos los nombres exactos que la librería exige.
    credenciales = {
        "client_id": c_id,
        "client_secret": c_secret,
        "refresh_token": r_token,
        "token_type": "Bearer"
    }

    # 4. Guardamos el archivo limpio
    archivo_final = "oauth_final.json"
    with open(archivo_final, 'w') as f:
        json.dump(credenciales, f)

    # 5. Conectamos
    yt = YTMusic(archivo_final)
    st.success("✅ Conectado con Google correctamente")

except Exception as e:
    st.error("🛑 Error de conexión:")
    st.code(str(e))
    # Debug para ver si las claves existen (sin mostrar contraseñas)
    st.warning("Diagnóstico de claves detectadas:")
    st.write(f"- Client ID detectado: {'Sí' if c_id else 'No'}")
    st.write(f"- Client Secret detectado: {'Sí' if c_secret else 'No'}")
    st.stop()

# --- FORMULARIO DE LA APP ---
with st.form("playlist_form"):
    tematica = st.text_input("Temática / Vibe", placeholder="Ej: Gym Motivación")
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
                video_ids = list(set(video_ids)) # Sin duplicados
                nombre = f"Mix: {tematica}"
                pl_id = yt.create_playlist(title=nombre, description=f"Vibe: {tematica}")
                yt.add_playlist_items(pl_id, video_ids)
                st.balloons()
                st.success(f"Playlist '{nombre}' creada con {len(video_ids)} canciones.")
            else:
                st.warning("No se encontraron canciones.")
        except Exception as e:
            st.error(f"Error creando la lista: {e}")
