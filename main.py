import streamlit as st
from auth import login_form, register_form, logout
from student_dashboard import student_dashboard
from admin_dashboard import admin_dashboard
from config import init_database

# Configuración de página
st.set_page_config(
    page_title="Sistema de Prácticas Preprofesionales",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado
def init_session():
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'token' not in st.session_state:
        st.session_state['token'] = None

def main():
    """Función principal de la aplicación"""
    init_session()
    
    # CSS personalizado
    st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #FF4B4B; text-align: center; }
    .sub-header { text-align: center; color: #6c757d; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎓 Sistema de Postulación para Prácticas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Conectando talento universitario con oportunidades reales</p>', unsafe_allow_html=True)
    
    # Si hay sesión activa
    if st.session_state['user']:
        user = st.session_state['user']
        
        # Botón de logout en sidebar
        with st.sidebar:
            if st.button(" Cerrar Sesión", use_container_width=True):
                logout()
        
        # Redirigir según rol
        if user['role'] == 'admin':
            admin_dashboard()
        else:
            student_dashboard()
    
    else:
        # Mostrar login y registro
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container(border=True):
                login_form()
        
        with col2:
            with st.container(border=True):
                register_form()
        
        # Footer
        st.divider()
        st.markdown("""
        
        """)

if __name__ == "__main__":
    main()