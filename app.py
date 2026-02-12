import streamlit as st
import json
import os
from ytmusicapi import YTMusic

st.set_page_config(page_title="Prueba Final", page_icon="🛠️")
st.title("🛠️ Prueba de Conexión Directa")

# --- ZONA DE DATOS (PEGALOS AQUÍ DIRECTAMENTE) ---
# No uses st.secrets por ahora. Ponlos aquí entre comillas.
CLIENT_ID = "770238210054-mdperjbgt9b7626rmji8f36kudde13r4.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REFRESH_TOKEN = "1//05P8UZpyrupdlCgYIARAAGAUSNwF-L9IrllvNh06JkFxLCVRoIIO2d5l0zgu6XOTb_Nt6Sxd1Z2NH9n4YR3Nymh86nNTchodtGdg" 

# --- GENERADOR DE ARCHIVO ---
st.write("Generando archivo de autenticación...")

datos_json = {
    "client_id": CLIENT_ID.strip(),
    "client_secret": CLIENT_SECRET.strip(),
    "refresh_token": REFRESH_TOKEN.strip(),
    "token_type": "Bearer"
}

# Verificación visual (Censurada) para que veas si se pegaron bien
st.code(f"""
Datos que se van a usar:
ID: {datos_json['client_id'][:10]}...
Secret: {datos_json['client_secret'][:5]}...
Token: {datos_json['refresh_token'][:10]}...
""")

try:
    # 1. Borramos cualquier versión vieja
    if os.path.exists('oauth.json'):
        os.remove('oauth.json')
        
    # 2. Creamos el archivo nuevo
    with open('oauth.json', 'w') as f:
        json.dump(datos_json, f, indent=4) # Indent ayuda a que sea legible
        
    # 3. Intentamos conectar
    yt = YTMusic('oauth.json')
    
    st.balloons()
    st.success("✅ ¡CONEXIÓN EXITOSA! El problema eran los Secrets.")
    st.write("Ahora sabemos que tus credenciales funcionan.")
    
except Exception as e:
    st.error("🛑 SIGUE FALLANDO")
    st.error(f"Error: {e}")
    st.write("Si esto falla, el problema es 100% que el Client ID o Secret están mal copiados de Google Cloud, o el Token ya caducó.")
