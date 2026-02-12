# ... (imports y configuración de página igual que antes) ...

# --- AUTENTICACIÓN BLINDADA ---
st.write("---")
st.subheader("🔐 Conexión Segura")

try:
    # 1. Recuperamos y LIMPIAMOS los datos (quitamos espacios y forzamos texto)
    # Usamos .strip() para borrar espacios al principio/final
    # Usamos str() para asegurar que sea texto puro
    c_id = str(st.secrets.get("mi_client_id", "")).strip().replace('"', '')
    c_secret = str(st.secrets.get("mi_client_secret", "")).strip().replace('"', '')
    r_token = str(st.secrets.get("mi_refresh_token", "")).strip().replace('"', '')

    # 2. Verificación de seguridad
    if len(c_id) < 10 or len(c_secret) < 5:
        st.error("❌ Los secretos parecen estar vacíos o incompletos.")
        st.stop()

    # 3. Construcción del JSON Limpio
    datos_json = {
        "client_id": c_id,
        "client_secret": c_secret,
        "refresh_token": r_token,
        "token_type": "Bearer"
    }

    # 4. Usamos un nombre de archivo nuevo para evitar caché vieja
    archivo_auth = 'auth_cache_v2.json'
    
    with open(archivo_auth, 'w') as f:
        json.dump(datos_json, f)
    
    # INTENTO DE CONEXIÓN
    yt = YTMusic(archivo_auth)
    st.success(f"✅ Conexión establecida (ID: {c_id[:10]}...)")

except Exception as e:
    st.error("🛑 Error Fatal:")
    st.write(e)
    # Debug visual: Veremos exactamente qué se escribió en el archivo
    st.warning("Diagnóstico del archivo generado:")
    if os.path.exists('auth_cache_v2.json'):
        with open('auth_cache_v2.json', 'r') as f:
            st.code(f.read()) # Muestra el contenido real del disco
    st.stop()

# ... (El resto de tu código del formulario sigue aquí) ...
