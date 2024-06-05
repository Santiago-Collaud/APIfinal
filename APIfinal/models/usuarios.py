from sqlalchemy import Column,Integer,String,ForeignKey
from config.db import Base,engine
from pydantic import BaseModel,EmailStr
from sqlalchemy.orm import sessionmaker,relationship

class User(Base):
    __tablename__="usuarios"

    id=Column("id",Integer,primary_key=True)
    username=Column("username",String(50),nullable=False,unique=True)
    password=Column("password",String)
    mail=Column("mail",String,nullable=False)
    id_detalleUsuario=Column(Integer,ForeignKey("detalles_usuarios.id"))
    DetalleUsuario_relacion=relationship("DetalleUsuario",backref="usuarios",uselist=False)

    def __init__(self,username,password,mail):
        self.username=username
        self.password=password
        self.mail=mail

class DetalleUsuario(Base):
    __tablename__="detalles_usuarios" 

    id=Column("id",Integer,primary_key=True)
    nombre=Column("nombre",String(50),nullable=False) 
    apellido=Column("apellido",String(50),nullable=False)
    DNI=Column("DNI",Integer,nullable=False)
    fecha_Nac=Column("fecha_nac",String(10))
    tipo=Column("tipo",String,nullable=False)
    direccion=Column("direccion",String(50))
    #id_carrera=Column("id_carrera",Integer)
    id_carrera=Column(Integer,ForeignKey("carreras.id_carrera"))
    carreras_relacion=relationship("Carrera",backref="detalles_usuarios",uselist=False)


    def __init__(self,nombre,apellido,DNI,fecha_nac,direccion,id_carrera,tipo):
        self.nombre=nombre
        self.apellido=apellido
        self.DNI=DNI
        self.fecha_Nac=fecha_nac
        self.tipo=tipo
        self.direccion=direccion
        self.id_carrera=id_carrera

class Pagos(Base):
    __tablename__ = "pagos"

    id_pago=Column("id_pago",Integer,primary_key=True) 
    fecha_pago=Column("fecha",String(10),nullable=False)
    mes_pagado=Column("mes_pago",String(15),nullable=False)
    id_usuario=Column(Integer,ForeignKey("detalles_usuarios.id"))
    monto=Column("monto",Integer)
    Dpagos_relacion=relationship("DetalleUsuario",backref="pagos",uselist=False)

    def __init__(self,fecha_pago,id_usuario,mes_pago,monto):
        self.fecha_pago=fecha_pago
        self.id_usuario=id_usuario
        self.mes_pagado=mes_pago
        self.monto=monto


class Carrera(Base):
    __tablename__="carreras"

    id_carrera=Column("id_carrera",Integer,primary_key=True)
    detalle=Column("detalle",String)

    def __init__(self,detalle_carrera):
        self.detalle=detalle_carrera

Base.metadata.create_all(bind=engine)

Session=sessionmaker(bind=engine)

Session=Session()

#class In_usuario(BaseModel):
#    username:str
#    password:str
#    mail:str

class In_usuario(BaseModel):
    username:str
    password:str
    mail:EmailStr
    DNI:int 
    nombre:str
    apellido:str
    tipo:str
    fecha_nac:str
    direccion:str
    id_carrera:int

class In_detalle_usuario(BaseModel):
    nombre:str
    apellido:str
    DNI:int
    fecha_nac:str
    tipo:str 
    direccion:str
    id_carrera:int

class In_login(BaseModel):
    usermane:str
    password:str

class add_pago(BaseModel):
    fecha_pago:str
    mes_pago:str
    monto:int

class inCarrera(BaseModel):
    detalle_carrera:str

#Base.metadata.drop_all(bind=engine) borra todas las tablas antes de arrancar el server
#Base.metadata.create_all(bind=engine) crea las tablas despues de borrarlas

