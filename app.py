import streamlit as st
import json
import os
from ytmusicapi import YTMusic

st.set_page_config(page_title="Music Generator", page_icon="🎵")

# --- 1. RECUPERACIÓN DE DATOS ---
# Usamos .get() y .strip() para limpiar errores de espacios invisibles
c_id = st.secrets.get("auth_client_id", "").strip()
c_secret = st.secrets.get("auth_client_secret", "").strip()
r_token = st.secrets.get("auth_refresh_token", "").strip()

# --- 2. DIAGNÓSTICO DE SEGURIDAD ---
if not c_id or not c_secret or not r_token:
    st.error("❌ ERROR FATAL: No se encuentran los secretos.")
    st.info("Asegúrate de que en 'Secrets' usaste: auth_client_id, auth_client_secret, auth_refresh_token")
    st.stop()

# --- 3. CONSTRUCCIÓN QUIRÚRGICA DEL JSON ---
# Aquí forzamos los nombres de las claves. Es imposible que falle el nombre aquí.
credenciales_limpias = {
    "client_id": c_id,         # La librería EXIGE "client_id"
    "client_secret": c_secret, # La librería EXIGE "client_secret"
    "refresh_token": r_token,  # La librería EXIGE "refresh_token"
    "token_type": "Bearer"
}

# --- 4. ESCRITURA DEL ARCHIVO ---
archivo_final = "oauth_final.json"
try:
    with open(archivo_final, 'w') as f:
        json.dump(credenciales_limpias, f)
except Exception as e:
    st.error(f"No se pudo crear el archivo: {e}")
    st.stop()

# --- 5. CONEXIÓN ---
st.title("🎵 DJ Automático")

try:
    # Inicializamos la librería con el archivo recién horneado
    yt = YTMusic(archivo_final)
    st.success("✅ Conexión establecida correctamente con Google.")
    
    # -- AQUÍ VA TU FORMULARIO DE SIEMPRE --
    with st.form("playlist_form"):
        tematica = st.text_input("Temática", "Gym Rock")
        submitted = st.form_submit_button("Crear Playlist")
        
        if submitted:
            # Tu lógica de búsqueda...
            st.write(f"Buscando canciones para: {tematica}...")
            # (Pega aquí tu lógica de búsqueda search/create_playlist)

except Exception as e:
    st.error("🛑 ERROR DE AUTENTICACIÓN")
    st.write("Detalles técnicos del error:")
    st.code(str(e))
    
    st.warning("🔍 REVISIÓN DE CONTENIDO (CENSURADO):")
    st.json({
        "client_id_length": len(c_id),
        "client_secret_length": len(c_secret),
        "refresh_token_start": r_token[:10] + "..."
    })
