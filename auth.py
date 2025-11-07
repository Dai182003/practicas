import streamlit as st
from database import Database
import uuid

def logout():
    """Cierra sesión"""
    for key in ['user', 'token']:
        if key in st.session_state:
            del st.session_state[key]
    st.success(" ¡Has cerrado sesión exitosamente!")
    st.rerun()

def login_form():
    """Formulario de inicio de sesión"""
    st.markdown("<h3 style='text-align: center;'> Iniciar Sesión</h3>", unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("Email", placeholder="ejemplo@correo.com")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar", use_container_width=True)
        
        if submit:
            db = Database()
            resultado = db.obtener_usuario_por_email(email)
            
            if resultado.data and len(resultado.data) > 0:
                user = resultado.data[0]
                if db.verificar_password(password, user['password_hash']):
                    st.session_state['user'] = user
                    st.session_state['token'] = str(uuid.uuid4())
                    st.success(f" Bienvenido, {user['nombre']}!")
                    st.rerun()
                else:
                    st.error(" Contraseña incorrecta")
            else:
                st.error(" Usuario no encontrado")

def register_form():
    """Formulario de registro"""
    st.markdown("<h3 style='text-align: center;'> Registro de Usuario</h3>", unsafe_allow_html=True)
    
    with st.form("register_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre *", placeholder="Rodger Mauricio")
            email = st.text_input("Email *", placeholder="rodger@example.com")
            telefono = st.text_input("Teléfono", placeholder="+593 99 788 9777")
        with col2:
            apellido = st.text_input("Apellido *", placeholder="Muñoz Molina")
            password = st.text_input("Contraseña *", type="password")
            dni = st.text_input("Cédula *", placeholder="1234567890")
        
        carrera = st.selectbox("Carrera Profesional *", 
            ["Ingeniería de Sistemas", "Derecho", "Medicina", "Arquitectura", 
             "Administración", "Marketing", "Otra"])
        
        universidad = st.text_input("Universidad *", 
            placeholder="Universidad Nacional Mayor de San Marcos")
        
        submit = st.form_submit_button("Crear Cuenta", use_container_width=True, type="primary")
        
        if submit:
            if not all([nombre, apellido, email, password, dni, carrera, universidad]):
                st.error(" Por favor completa todos los campos obligatorios (*)")
                return
            
            db = Database()
            
            # Verificar email existente
            if db.obtener_usuario_por_email(email).data:
                st.error(" Este email ya está registrado")
                return
            
            # Verificar DNI existente
            resultado = db.sb.table("users").select("*").eq("dni", dni).execute()
            if resultado.data:
                st.error(" Este usuario ya está registrado")
                return
            
            try:
                datos = {
                    "nombre": nombre,
                    "apellido": apellido,
                    "dni": dni,
                    "telefono": telefono,
                    "carrera": carrera,
                    "universidad": universidad
                }
                db.crear_usuario(email, password, "estudiante", **datos)
                st.success(" ¡Registro exitoso! Ahora puedes iniciar sesión.")
                st.balloons()
            except Exception as e:
                st.error(f" Error en el registro: {e}")