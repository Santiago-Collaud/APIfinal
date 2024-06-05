from fastapi import APIRouter,HTTPException
from fastapi.responses import JSONResponse
from psycopg2 import IntegrityError
from models.usuarios import Session,In_usuario,User,DetalleUsuario,In_detalle_usuario,In_login,add_pago,Pagos
from sqlalchemy.orm import joinedload ## para usar la tecnica de carga con union (join loading) para devolver el objeto user con cada uno de sus userDetail

users = APIRouter()

@users.get('/hola')
def holaMundo():
    return "Hola Mundo"

#USUARIOS traer todo
@users.get("/usuario/all")
def mostrarUsuarios():
    try:
        return Session.query(User).all()
    except Exception as e:
        print("Error al obtener el usuario:",e)
        return JSONResponse(status_code=500,content={"detail":"error al obtener usuarios"})

#USUARIOS buscar por nombre
@users.get("/usuarios/buscar_nombre/{n}")
def getUsuarioNombre(n:str):
    try:
        return Session.query(User).filter(User.username==n).first()
    except Exception as e:
        print("Error al obtener el usuario:",e)
        return JSONResponse(status_code=500,content={"detail":"error al obtener usuarios"})

#USUARIO crear
@users.post("/usuario/crear")
def crearUsuario(user:In_usuario):
    try: 
        if validarUsername(user.username):
            if validarMail(user.mail):
                NuevoUsuario=User(user.username,user.password,user.mail)

                NuevoDetalleUsuario=DetalleUsuario(user.nombre,user.apellido,user.DNI,user.fecha_nac,user.tipo,user.id_carrera,user.direccion)
                
                NuevoUsuario.DetalleUsuario_relacion=NuevoDetalleUsuario
                
                Session.add(NuevoUsuario)
                Session.commit()
                return "Usuario agregado"
            
        else:
            return "El usuario ya exciste"
    except IntegrityError as e: # Suponiendo que el mje de error contiene "username" para el campo duplicado
        if "username" in str(e):
            return JSONResponse(status_code=400,content={"detail":"username ya existe"})
        else: # Maneja otros errores de integridad
            print("Error de integridad insperado:",e)
            return JSONResponse(status_code=500,content={"detail":"Error al agregar usuario"})

def validarUsername(value):
    existeUsuario = Session.query(User).filter(User.username==value).first()
    Session.close()
    if existeUsuario:
        return None
    else:
        return value

def validarMail(value):
    exiteMail=Session.query(User).filter(User.mail==value).first()
    Session.close()
    if exiteMail:
        return None
    else:
        return value

#DETALLE USUARIO traer todo
@users.get("/detalleUsuario/all")
def mostrarDetallesUsuarios():
    try:
        return Session.query(DetalleUsuario).all()
    except Exception as e:
        print(e)
        return e
    
#DETALLE USUARIO buscar por nombre
@users.get("/detalleUsuario/buscar_nombre/{n}")
def getDetalleNombre(n:str):
    try:
        return Session.query(DetalleUsuario).filter(DetalleUsuario.nombre==n).all()
    except Exception as e:
        print(e)
        return e
    
#DETALLE USUARIO buscar por DNI
@users.get("/detalleUsuario/buscar_DNI/{n}") 
def getDetalleDNI(n:int):
    try:
        return Session.query(DetalleUsuario).filter(DetalleUsuario.DNI==n).all()
    except Exception as e:
        print(e)
        return e

#DETALLE USUARIO crear
@users.post("/detalleUsuario/add")
def crearDetalleusuario(Detalle:In_detalle_usuario):
    try:
        nuevoUsuario=DetalleUsuario(Detalle.nombre,Detalle.apellido,Detalle.DNI,Detalle.fecha_nac,Detalle.tipo)
        Session.add(nuevoUsuario)
        Session.commit()
        return "Detalles agregados con exitos"
    except Exception as e:
        print(e)
        return e
    
#MOSTRAR usuarios y detalles de usuario
@users.get("/usuarios_todos/all")
def obtener_usuarios():
    try:
        usuarios = Session.query(User).options(
            joinedload(User.DetalleUsuario_relacion).
            joinedload(DetalleUsuario.carreras_relacion)
            ).all()

        Usuarios_con_detalles = []

        for usuario in usuarios:
            usuario_con_detalle = {
                "id": usuario.id,
                "username": usuario.username, 
                "mail": usuario.mail,
                "nombre": usuario.DetalleUsuario_relacion.nombre,
                "apellido": usuario.DetalleUsuario_relacion.apellido,
                "DNI": usuario.DetalleUsuario_relacion.DNI,
                "fecha_nac": usuario.DetalleUsuario_relacion.fecha_Nac,
                "tipo": usuario.DetalleUsuario_relacion.tipo,
                "direccion":usuario.DetalleUsuario_relacion.direccion,
                #"carrera":DetalleUsuario.carreras_relacion.detalle
                "carrera": usuario.DetalleUsuario_relacion.carreras_relacion.detalle if usuario.DetalleUsuario_relacion.carreras_relacion else None
            }
            Usuarios_con_detalles.append(usuario_con_detalle)  # Mover esta línea dentro del bucle

        return JSONResponse(status_code=200, content=Usuarios_con_detalles)
    except Exception as e:
        print("Error al obtener usuarios", e)
        return JSONResponse(status_code=500, content={"detail": "Error al obtener los usuarios"})

#LOGUIN
@users.post("/users/loginUser")
def login(login:In_login):
    
    try:
        usuarioIN=User(login.username,login.password,"","")
        respuesta=Session.query(User).filter(User.username==usuarioIN.username).first()
        if respuesta.password==usuarioIN.password:
            return respuesta
        else:
            return None
    except Exception as e:
        print(e)

#PAGO agregar
@users.post("/pago/addPago/{DNI}")
def agregar_pago(DNI: int, pago: add_pago):
    try:
        # Buscar el usuario por DNI
        usuario_detalle = Session.query(DetalleUsuario).filter(DetalleUsuario.DNI == DNI).first()
        if not usuario_detalle:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            #return "usuario no encontrado"
        # Crear el objeto Pago
        nuevo_pago = Pagos(
            fecha_pago=pago.fecha_pago,
            id_usuario=usuario_detalle.id,
            mes_pago=pago.mes_pago,
            monto=pago.monto
        )
        # Agregar el pago a la sesión y confirmar la transacción
        Session.add(nuevo_pago)
        Session.commit()

        return {"message": "Pago realizado exitosamente"}
    except Exception as e:
        Session.rollback()
        print("Error al crear el pago:", e)
        raise HTTPException(status_code=500, detail="Error al crear el pago")
        #return "Error al crear el pago"

#PAGO mostrar todos los pagos FALTA TERMINAR
@users.get("/pago/mostrar_pagos")
def getAllPagos():
    try:
        usuarios = Session.query(Pagos).options(
            joinedload(Pagos.Dpagos_relacion)
            ).all()
        Pagos_con_detalles = []

        for pago in usuarios:
            pago_con_detalle = {
                "id_pago": pago.id_pago,
                "fecha_pago": pago.fecha_pago,
                "mes_pagado": pago.mes_pagado,
                "monto": pago.monto,
                "usuario": {
                    "id": pago.Dpagos_relacion.id,
                    "nombre": pago.Dpagos_relacion.nombre,
                    "apellido": pago.Dpagos_relacion.apellido,
                    "DNI": pago.Dpagos_relacion.DNI,
                    "fecha_nac": pago.Dpagos_relacion.fecha_Nac,
                    "tipo": pago.Dpagos_relacion.tipo,
                    "direccion": pago.Dpagos_relacion.direccion,
                    "carrera": pago.Dpagos_relacion.carreras_relacion.detalle if pago.Dpagos_relacion.carreras_relacion else None
                }
            }
            Pagos_con_detalles.append(pago_con_detalle)  # Mover esta línea dentro del bucle

        return JSONResponse(status_code=200, content=Pagos_con_detalles)
    except Exception as e:
        print("Error al obtener usuarios", e)
        return JSONResponse(status_code=500, content={"detail": "Error al obtener los usuarios"})


#PAGO buscar pagos por DNI


