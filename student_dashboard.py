import streamlit as st
from database import Database
import pandas as pd

def student_dashboard():
    """Panel principal del estudiante"""
    st.markdown("### 🎓 Panel Estudiante")
    
    if 'user' not in st.session_state:
        st.warning("⚠️ No has iniciado sesión")
        return
    
    user = st.session_state['user']
    db = Database()
    
    # CONTADOR DE POSTULACIONES
    postulaciones = db.obtener_postulaciones_por_usuario(user['id'])
    total_postulaciones = len(postulaciones.data) if postulaciones.data else 0
    
    # Sidebar con info del estudiante
    with st.sidebar:
        st.markdown(f"**👤 {user['nombre']} {user['apellido']}**")
        st.markdown(f"🎓 *{user['carrera']}*")
        st.markdown(f"🏫 *{user['universidad']}*")
        st.divider()
        st.markdown(f"**📋 Total de Postulaciones:** `{total_postulaciones}`")
        st.divider()
        
        menu = st.radio("Navegación", 
                       ["🔍 Buscar Prácticas", "📋 Mis Postulaciones", "👤 Mi Perfil"])
    
    if menu == "🔍 Buscar Prácticas":
        buscar_practicas(db, user)
    elif menu == "📋 Mis Postulaciones":
        mis_postulaciones(db, user)
    else:
        mi_perfil(db, user)

def buscar_practicas(db, user):
    """Buscador de prácticas con filtros"""
    st.markdown("#### 🔍 Buscar Ofertas de Prácticas")
    
    # Filtros
    with st.expander("📂 Filtros Avanzados", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            area_filtrar = st.selectbox("Área", 
                ["", "Tecnología", "Administración", "Marketing", "Recursos Humanos", 
                 "Finanzas", "Diseño", "Ingeniería", "Otro"], 
                help="Filtrar por área profesional")
        with col2:
            modalidad_filtrar = st.selectbox("Modalidad", 
                ["", "Presencial", "Remoto", "Híbrido"], 
                help="Filtrar por modalidad de trabajo")
        with col3:
            ubicacion_filtrar = st.text_input("Ubicación", 
                placeholder="Lima", 
                help="Filtrar por ciudad o región")
    
    # Aplicar filtros
    filtros = {}
    if area_filtrar: filtros["area"] = area_filtrar
    if modalidad_filtrar: filtros["modalidad"] = modalidad_filtrar
    if ubicacion_filtrar: filtros["ubicacion"] = ubicacion_filtrar
    
    ofertas = db.obtener_ofertas(filtros=filtros if any(filtros.values()) else None)
    
    if not ofertas.data:
        st.info("📭 No se encontraron ofertas con estos filtros")
        return
    
    # Mostrar ofertas en cards
    st.markdown(f"**{len(ofertas.data)} ofertas encontradas**")
    
    for oferta in ofertas.data:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### 🏢 {oferta['titulo']}")
                st.markdown(f"**Empresa:** {oferta['empresa']}")
                st.markdown(f"**Área:** `{oferta['area']}` | **Modalidad:** `{oferta['modalidad']}`")
                st.markdown(f"**Ubicación:** 📍 {oferta['ubicacion']} | **Duración:** {oferta['duracion']}")
                
                with st.expander("Ver detalles"):
                    st.markdown(f"**Descripción:**\n{oferta['descripcion']}")
                    st.markdown(f"**Requisitos:**\n{oferta['requisitos']}")
            
            with col2:
                # Verificar si ya postuló
                postulado = db.sb.table("postulaciones")\
                    .select("*")\
                    .eq("user_id", user['id'])\
                    .eq("oferta_id", oferta['id'])\
                    .execute()
                
                if postulado.data:
                    st.success("✅ Ya postulaste")
                else:
                    if st.button("Postularme", key=f"post_{oferta['id']}", type="primary"):
                        postularse(db, user['id'], oferta['id'])
            
            st.divider()

def postularse(db, user_id, oferta_id):
    """Proceso de postulación"""
    st.markdown("#### 📄 Confirmar Postulación")
    
    # Subir CV (simulado)
    cv_file = st.file_uploader("Adjuntar CV (PDF)", type=["pdf"], key="cv_upload")
    
    if st.button("Confirmar Postulación", type="primary"):
        try:
            archivo_cv = "cv_simulado.pdf"  # En producción, subir a Supabase Storage
            db.crear_postulacion(user_id, oferta_id, archivo_cv)
            st.success("✅ ¡Postulación enviada exitosamente!")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al postular: {e}")

def mis_postulaciones(db, user):
    """Ver postulaciones del estudiante (SOLO VISTA, NO EDITAR/ELIMINAR)"""
    st.markdown("#### 📋 Mis Postulaciones")
    
    postulaciones = db.obtener_postulaciones_por_usuario(user['id'])
    
    if not postulaciones.data:
        st.info("📭 Aún no te has postulado a ninguna práctica")
        return
    
    # Mostrar contador
    st.markdown(f"**Total de postulaciones:** `{len(postulaciones.data)}`")
    
    for post in postulaciones.data:
        with st.container():
            oferta = post['ofertas_practicas']
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                st.markdown(f"**🎯 {oferta['titulo']}**")
                st.markdown(f"🏢 {oferta['empresa']} | 📍 {oferta['ubicacion']}")
            
            with col2:
                estado = post['estado']
                color = "green" if estado == "aprobado" else "orange" if estado == "pendiente" else "red"
                st.markdown(f"**Estado:** :{color}[**{estado.upper()}**]")
            
            with col3:
                st.markdown(f"📅 {post['fecha_postulacion'][:10]}")
            # ESTUDIANTE SOLO VE, NO PUEDE EDITAR/ELIMINAR
            st.divider()

def mi_perfil(db, user):
    """Editar perfil del estudiante"""
    st.markdown("#### 👤 Mi Perfil")
    
    with st.form("perfil_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", value=user['nombre'])
            email = st.text_input("Email", value=user['email'], disabled=True)
            telefono = st.text_input("Teléfono", value=user.get('telefono', ''))
        
        with col2:
            apellido = st.text_input("Apellido", value=user['apellido'])
            dni = st.text_input("DNI", value=user['dni'], disabled=True)
            carrera = st.text_input("Carrera", value=user['carrera'])
        
        universidad = st.text_input("Universidad", value=user['universidad'])
        
        if st.form_submit_button("Actualizar Perfil", type="primary"):
            datos = {
                "nombre": nombre,
                "apellido": apellido,
                "telefono": telefono,
                "carrera": carrera,
                "universidad": universidad
            }
            
            try:
                db.sb.table("users").update(datos).eq("id", user['id']).execute()
                st.success("✅ Perfil actualizado exitosamente")
                st.session_state['user'].update(datos)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")