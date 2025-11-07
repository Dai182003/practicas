import bcrypt
from config import get_supabase_client
from datetime import datetime

class Database:
    def __init__(self):
        self.sb = get_supabase_client()

    # USUARIOS
    def crear_usuario(self, email, password, role="estudiante", **datos):
        """Crea usuario con contraseña hasheada"""
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        data = {
            "email": email,
            "password_hash": hashed,
            "role": role,
            **datos
        }
        return self.sb.table("users").insert(data).execute()

    def obtener_usuario_por_email(self, email):
        """Busca usuario por email"""
        return self.sb.table("users").select("*").eq("email", email).execute()

    def verificar_password(self, password, hashed):
        """Verifica contraseña"""
        return bcrypt.checkpw(password.encode(), hashed.encode())

    # OFERTAS
    def crear_oferta(self, datos):
        """Crea nueva oferta de práctica"""
        return self.sb.table("ofertas_practicas").insert(datos).execute()

    def obtener_ofertas(self, filtros=None):
        """Obtiene ofertas con filtros opcionales"""
        query = self.sb.table("ofertas_practicas").select("*")
        
        if filtros:
            for key, value in filtros.items():
                if value:
                    query = query.eq(key, value)
        
        return query.execute()

    def obtener_oferta_por_id(self, oferta_id):
        """Obtiene una oferta específica"""
        return self.sb.table("ofertas_practicas").select("*").eq("id", oferta_id).execute()

    def actualizar_oferta(self, oferta_id, datos):
        """Actualiza oferta"""
        return self.sb.table("ofertas_practicas").update(datos).eq("id", oferta_id).execute()

    def eliminar_oferta(self, oferta_id):
        """Elimina oferta"""
        return self.sb.table("ofertas_practicas").delete().eq("id", oferta_id).execute()

    # POSTULACIONES
    def crear_postulacion(self, user_id, oferta_id, archivo_cv=None):
        """Crea postulación"""
        data = {
            "user_id": user_id,
            "oferta_id": oferta_id,
            "archivo_cv": archivo_cv
        }
        return self.sb.table("postulaciones").insert(data).execute()

    def obtener_postulaciones_por_usuario(self, user_id):
        """Obtiene postulaciones de un estudiante"""
        return self.sb.table("postulaciones")\
            .select("*, ofertas_practicas(*)")\
            .eq("user_id", user_id)\
            .execute()

    def obtener_postulaciones_admin(self):
        """Obtiene todas las postulaciones para admin"""
        return self.sb.table("postulaciones")\
            .select("*, ofertas_practicas(*), users(nombre, apellido, email)")\
            .execute()

    def actualizar_estado_postulacion(self, postulacion_id, nuevo_estado):
        """Actualiza estado de postulación"""
        return self.sb.table("postulaciones")\
            .update({"estado": nuevo_estado})\
            .eq("id", postulacion_id)\
            .execute()

    # MÉTODOS NUEVOS PARA EDITAR/ELIMINAR POSTULACIONES
    def actualizar_postulacion(self, postulacion_id, datos):
        """Actualiza datos de una postulación"""
        return self.sb.table("postulaciones").update(datos).eq("id", postulacion_id).execute()

    def eliminar_postulacion(self, postulacion_id):
        """Elimina una postulación"""
        return self.sb.table("postulaciones").delete().eq("id", postulacion_id).execute()

    def obtener_postulacion_por_id(self, postulacion_id):
        """Obtiene una postulación específica"""
        return self.sb.table("postulaciones").select("*").eq("id", postulacion_id).execute()

    # ESTADÍSTICAS
    def get_estadisticas(self):
        """Obtiene estadísticas para el panel admin"""
        try:
            # Contar ofertas
            ofertas_resp = self.sb.table("ofertas_practicas").select("*", count="exact").execute()
            total_ofertas = getattr(ofertas_resp, 'count', 0) or 0

            # Contar postulaciones
            postulaciones_resp = self.sb.table("postulaciones").select("*", count="exact").execute()
            total_postulaciones = getattr(postulaciones_resp, 'count', 0) or 0

            # Contar pendientes
            pendientes_resp = self.sb.table("postulaciones")\
                .select("*", count="exact")\
                .eq("estado", "pendiente")\
                .execute()
            postulaciones_pendientes = getattr(pendientes_resp, 'count', 0) or 0

            return {
                "total_ofertas": total_ofertas,
                "total_postulaciones": total_postulaciones,
                "pendientes": postulaciones_pendientes
            }
        except Exception as e:
            print(f"⚠️ Error obteniendo estadísticas: {e}")
            return {
                "total_ofertas": 0,
                "total_postulaciones": 0,
                "pendientes": 0
            }