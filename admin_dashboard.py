import streamlit as st
from database import Database
import pandas as pd
import time

def admin_dashboard():
    """Panel de administrador"""
    st.markdown("### 👑 Panel Administrador")
    
    if 'user' not in st.session_state or st.session_state['user']['role'] != 'admin':
        st.error("❌ Acceso denegado")
        return
    
    db = Database()
    user = st.session_state['user']
    
    # Sidebar Admin
    with st.sidebar:
        st.markdown(f"**👑 Admin:** {user['nombre']}")
        st.divider()
        
        menu = st.radio("Gestión", 
                       ["📊 Dashboard", "🏢 Gestionar Ofertas", 
                        "📋 Revisar Postulaciones", "👥 Usuarios"])
    
    if menu == "📊 Dashboard":
        dashboard_admin(db)
    elif menu == "🏢 Gestionar Ofertas":
        gestionar_ofertas(db)
    elif menu == "📋 Revisar Postulaciones":
        revisar_postulaciones(db)
    else:
        gestionar_usuarios(db)

def dashboard_admin(db):
    """Dashboard principal con estadísticas"""
    st.markdown("#### 📊 Dashboard General")
    
    # Estadísticas corregidas
    try:
        # Contar ofertas
        ofertas_resp = db.sb.table("ofertas_practicas").select("*", count="exact").execute()
        total_ofertas = getattr(ofertas_resp, 'count', 0) or 0

        # Contar postulaciones
        postulaciones_resp = db.sb.table("postulaciones").select("*", count="exact").execute()
        total_postulaciones = getattr(postulaciones_resp, 'count', 0) or 0

        # Contar pendientes
        pendientes_resp = db.sb.table("postulaciones")\
            .select("*", count="exact")\
            .eq("estado", "pendiente")\
            .execute()
        postulaciones_pendientes = getattr(pendientes_resp, 'count', 0) or 0

        stats = {
            "total_ofertas": total_ofertas,
            "total_postulaciones": total_postulaciones,
            "pendientes": postulaciones_pendientes
        }
    except:
        stats = {"total_ofertas": 0, "total_postulaciones": 0, "pendientes": 0}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📌 Ofertas Activas", stats['total_ofertas'])
    with col2:
        st.metric("📬 Postulaciones", stats['total_postulaciones'])
    with col3:
        st.metric("⏳ Pendientes", stats['pendientes'])
    
    st.divider()
    st.markdown("#### 📈 Visualización")
    st.info("💡 En un sistema completo, aquí irían gráficos con Plotly")

def gestionar_ofertas(db):
    """CRUD completo de ofertas"""
    st.markdown("#### 🏢 Gestión de Ofertas de Prácticas")
    
    tab1, tab2, tab3 = st.tabs(["➕ Crear Oferta", "📋 Listar Ofertas", "✏️ Editar/Eliminar"])
    
    with tab1:
        crear_oferta_form(db)
    
    with tab2:
        listar_ofertas_admin(db)
    
    with tab3:
        editar_oferta_form(db)

def crear_oferta_form(db):
    """Formulario para crear oferta"""
    st.markdown("**Nueva Oferta de Práctica**")
    
    with st.form("nueva_oferta", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("Título del puesto *", placeholder="Desarrollador Frontend")
            empresa = st.text_input("Empresa *", placeholder="Tech Solutions SAC")
            area = st.selectbox("Área *", 
                ["Tecnología", "Administración", "Marketing", "Recursos Humanos", 
                 "Finanzas", "Diseño", "Ingeniería", "Otro"])
        
        with col2:
            duracion = st.text_input("Duración *", placeholder="6 meses")
            modalidad = st.selectbox("Modalidad *", ["Presencial", "Remoto", "Híbrido"])
            ubicacion = st.text_input("Ubicación *", placeholder="Lima, Perú")
        
        descripcion = st.text_area("Descripción *", height=150)
        requisitos = st.text_area("Requisitos *", height=150)
        
        if st.form_submit_button("Publicar Oferta", type="primary"):
            if not all([titulo, empresa, area, duracion, modalidad, ubicacion]):
                st.error("❌ Completa todos los campos obligatorios")
                return
            
            datos = {
                "titulo": titulo,
                "empresa": empresa,
                "area": area,
                "duracion": duracion,
                "modalidad": modalidad,
                "ubicacion": ubicacion,
                "descripcion": descripcion,
                "requisitos": requisitos,
                "estado": "activa"
            }
            
            try:
                db.crear_oferta(datos)
                st.success("✅ Oferta creada exitosamente")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error: {e}")

def listar_ofertas_admin(db):
    """Listar todas las ofertas"""
    ofertas = db.obtener_ofertas()
    
    if not ofertas.data:
        st.info("No hay ofertas registradas")
        return
    
    for oferta in ofertas.data:
        with st.expander(f"🏢 {oferta['titulo']} - {oferta['empresa']}"):
            st.markdown(f"**Área:** {oferta['area']} | **Modalidad:** {oferta['modalidad']}")
            st.markdown(f"**Estado:** `{oferta['estado']}`")
            st.markdown(f"**Descripción:** {oferta['descripcion']}")

def editar_oferta_form(db):
    """Editar o eliminar oferta"""
    oferta_id = st.text_input("ID de la oferta a editar/eliminar", 
                              help="Obtén el ID de la tabla de ofertas")
    
    if oferta_id:
        oferta = db.obtener_oferta_por_id(oferta_id)
        
        if oferta.data:
            oferta = oferta.data[0]
            st.markdown(f"Editando: **{oferta['titulo']}**")
            
            # Similar a crear_oferta_form pero con datos prellenados
            # (simplificado por brevedad)
            st.info("Formulario de edición aquí (similar a crear)")
            
            if st.button("🗑️ Eliminar Oferta", type="secondary"):
                if st.checkbox("⚠️ Confirmar eliminación"):
                    db.eliminar_oferta(oferta_id)
                    st.success("✅ Oferta eliminada")
        else:
            st.error("❌ Oferta no encontrada")

def revisar_postulaciones(db):
    """Revisar y aprobar/rechazar postulaciones con opciones de editar/eliminar"""
    st.markdown("#### 📋 Revisión de Postulaciones")
    
    # Filtros
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        estado_filtro = st.selectbox("Filtrar por estado", 
            ["Todos", "pendiente", "aprobado", "rechazado"])
    
    postulaciones = db.obtener_postulaciones_admin()
    
    if not postulaciones.data:
        st.info("📭 No hay postulaciones para revisar")
        return
    
    # Mostrar contador
    total = len(postulaciones.data)
    pendientes = len([p for p in postulaciones.data if p['estado'] == 'pendiente'])
    st.markdown(f"**Total:** `{total}` | **Pendientes:** `{pendientes}`")
    
    for post in postulaciones.data:
        if estado_filtro != "Todos" and post['estado'] != estado_filtro:
            continue
        
        with st.container():
            # Tarjeta de postulación
            estudiante = post['users']
            oferta = post['ofertas_practicas']
            
            st.markdown(f"### 📄 **{oferta['titulo']}**")
            st.markdown(f"**👤 Estudiante:** {estudiante['nombre']} {estudiante['apellido']} | 📧 {estudiante['email']}")
            st.markdown(f"**🏢 Empresa:** {oferta['empresa']} | 📍 {oferta['ubicacion']}")
            
            # Mostrar notas si existen
            if post.get('notas'):
                st.markdown(f"**📝 Notas:** {post['notas']}")
            
            # Estado actual
            estado = post['estado']
            color = "green" if estado == "aprobado" else "orange" if estado == "pendiente" else "red"
            st.markdown(f"**Estado actual:** :{color}[**{estado.upper()}**] | 📅 {post['fecha_postulacion'][:10]}")
            
            # ACCIONES DEL ADMIN - INCLUYE EDITAR/ELIMINAR
            col_acc1, col_acc2, col_acc3, col_acc4 = st.columns([1, 1, 1, 3])
            with col_acc1:
                if st.button("✅ Aprobar", key=f"apr_{post['id']}", type="primary"):
                    db.actualizar_estado_postulacion(post['id'], 'aprobado')
                    st.success(f"✅ Postulación aprobada para {estudiante['nombre']}")
                    time.sleep(1)
                    st.rerun()
            
            with col_acc2:
                if st.button("❌ Rechazar", key=f"rec_{post['id']}", type="secondary"):
                    db.actualizar_estado_postulacion(post['id'], 'rechazado')
                    st.error(f"❌ Postulación rechazada para {estudiante['nombre']}")
                    time.sleep(1)
                    st.rerun()
            
            with col_acc3:
                if st.button("✏️ Editar", key=f"edit_{post['id']}"):
                    editar_postulacion_admin(db, post['id'], oferta['titulo'])
            
            with col_acc4:
                if st.button("🗑️ Eliminar", key=f"del_{post['id']}", type="secondary"):
                    eliminar_postulacion_admin(db, post['id'], oferta['titulo'])
            
            st.divider()

def editar_postulacion_admin(db, postulacion_id, titulo_oferta):
    """Admin puede editar notas de cualquier postulación"""
    st.markdown(f"**✏️ Editando postulación:** {titulo_oferta}")
    
    # Obtener datos actuales
    postulacion = db.obtener_postulacion_por_id(postulacion_id)
    if not postulacion.data:
        st.error("No se pudo cargar la postulación")
        return
    
    datos_actuales = postulacion.data[0]
    
    # Formulario de edición
    with st.form(key=f"edit_form_admin_{postulacion_id}"):
        notas = st.text_area(
            "Notas adicionales (para uso interno del admin)",
            value=datos_actuales.get('notas', ''),
            help="Estas notas solo las ve el administrador"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Guardar cambios", type="primary"):
                try:
                    db.actualizar_postulacion(postulacion_id, {"notas": notas})
                    st.success("✅ Postulación actualizada por admin")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al actualizar: {e}")
        
        with col2:
            if st.form_submit_button("❌ Cancelar", type="secondary"):
                st.rerun()

def eliminar_postulacion_admin(db, postulacion_id, titulo_oferta):
    """Admin puede eliminar cualquier postulación"""
    st.markdown(f"**⚠️ ¿Eliminar postulación?** {titulo_oferta}")
    st.warning("⚠️ **ADVERTENCIA:** Esta acción eliminará la postulación completamente")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirmar eliminación", key=f"conf_del_admin_{postulacion_id}", type="primary"):
            try:
                db.eliminar_postulacion(postulacion_id)
                st.success("🗑️ Postulación eliminada por admin")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al eliminar: {e}")
    
    with col2:
        if st.button("❌ Cancelar", key=f"cancel_del_admin_{postulacion_id}"):
            st.rerun()

def gestionar_usuarios(db):
    """Gestión básica de usuarios"""
    st.markdown("#### 👥 Gestión de Usuarios")
    
    # Solo para demostración
    st.info("💡 En un sistema completo, aquí se gestionarían usuarios")
    
    if st.checkbox("Mostrar todos los usuarios (solo admin)"):
        users = db.sb.table("users").select("id, nombre, apellido, email, role, created_at").execute()
        if users.data:
            df = pd.DataFrame(users.data)
            st.dataframe(df, use_container_width=True)