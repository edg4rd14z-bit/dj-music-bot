import streamlit as st
import json
import os
from ytmusicapi import YTMusic

st.set_page_config(page_title="Modo Diagnóstico", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ Diagnóstico de Credenciales")

st.write("Analizando configuración...")

# 1. INTENTO DE RECUPERACIÓN DE DATOS
# Buscamos las variables con nombres estándar
c_id = st.secrets.get("client_id")
c_secret = st.secrets.get("client_secret")
r_token = st.secrets.get("refresh_token")

# 2. REPORTE DE ESTADO (Censurado)
col1, col2, col3 = st.columns(3)

with col1:
    if c_id:
        st.success(f"✅ Client ID detectado\n({str(c_id)[:5]}...)")
    else:
        st.error("❌ Client ID: NO ENCONTRADO")

with col2:
    if c_secret:
        st.success(f"✅ Secret detectado\n({str(c_secret)[:3]}...)")
    else:
        st.error("❌ Secret: NO ENCONTRADO")

with col3:
    if r_token:
        st.success(f"✅ Token detectado\n({str(r_token)[:10]}...)")
    else:
        st.error("❌ Token: NO ENCONTRADO")

# 3. SI FALTA ALGO, PARAMOS AQUÍ
if not c_id or not c_secret or not r_token:
    st.warning("⚠️ REVISIÓN NECESARIA: Ve a Settings > Secrets en Streamlit Cloud.")
    st.code("""
# El formato correcto debe ser:
client_id = "tu-id-de-google..."
client_secret = "tu-secreto..."
refresh_token = "tu-token-largo..."
    """, language="toml")
    st.stop()

# 4. INTENTO DE GENERACIÓN DE ARCHIVO
try:
    datos_json = {
        "client_id": c_id.strip().replace('"', ''), # Limpieza extra
        "client_secret": c_secret.strip().replace('"', ''),
        "refresh_token": r_token.strip().replace('"', ''),
        "token_type": "Bearer"
    }
    
    with open('oauth.json', 'w') as f:
        json.dump(datos_json, f, indent=4)
    
    st.info("Archivo 'oauth.json' generado internamente.")
    
    # Muestra el contenido que va a intentar usar (CENSURADO)
    st.text("Contenido que se enviará a YouTube Music:")
    st.json({
        "client_id": datos_json["client_id"][:10] + "...",
        "client_secret": datos_json["client_secret"][:5] + "...",
        "refresh_token": datos_json["refresh_token"][:20] + "..."
    })

except Exception as e:
    st.error(f"Error escribiendo archivo: {e}")
    st.stop()

# 5. PRUEBA DE FUEGO: CONEXIÓN
st.write("---")
st.write("🔄 Intentando conectar con YouTube Music...")

try:
    yt = YTMusic('oauth.json')
    st.balloons()
    st.success("✨ ¡ÉXITO! LA CONEXIÓN FUNCIONA ✨")
    st.write("Ahora ya puedes volver a poner el código de la Playlist.")
    
except Exception as e:
    st.error("🛑 FALLÓ LA CONEXIÓN")
    st.error(f"Mensaje de error: {e}")
    st.write("Esto significa que los datos están ahí, pero Google los rechaza.")
    st.write("Posibles causas:")
    st.write("1. El Client ID o Secret no coinciden con el proyecto de Google Cloud.")
    st.write("2. El Refresh Token ya caducó o pertenece a otra cuenta.")
