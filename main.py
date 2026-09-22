from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, status
import models
from pydantic import BaseModel
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

class UsuarioSchema(BaseModel):
    nombre: str
    correo: str
    edad: int

    class Config:
        from_attributes = True


app = FastAPI()


@app.get("/usuarios")
def obtener_todos_los_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.UsuarioDB).all()
    return usuarios


@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = (
        db.query(models.UsuarioDB)
        .filter(models.UsuarioDB.id == usuario_id)
        .first()
    )
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con el ID {usuario_id} no existe",
        )
    return usuario


@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioSchema, db: Session = Depends(get_db)):

    nuevo_usuario = models.UsuarioDB(
        nombre=usuario.nombre, correo=usuario.correo, edad=usuario.edad
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario) 

    return {
        "mensaje": "Usuario guardado en la base de datos con éxito",
        "usuario": nuevo_usuario,
    }


@app.put("/usuarios/{usuario_id}")
def actualizar_usuario(
    usuario_id: int, 
    usuario_actualizado: UsuarioSchema, 
    db: Session = Depends(get_db)
):

    usuario_db = (
        db.query(models.UsuarioDB)
        .filter(models.UsuarioDB.id == usuario_id)
        .first()
    )


    if usuario_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con el ID {usuario_id} no existe",
        )


    usuario_db.nombre = usuario_actualizado.nombre
    usuario_db.correo = usuario_actualizado.correo
    usuario_db.edad = usuario_actualizado.edad


    db.commit()
    db.refresh(usuario_db)

    return {
        "mensaje": "Usuario actualizado con éxito",
        "usuario": usuario_db,
    }


@app.delete("/usuarios/{usuario_id}", status_code=status.HTTP_200_OK)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):

    usuario_db = (
        db.query(models.UsuarioDB)
        .filter(models.UsuarioDB.id == usuario_id)
        .first()
    )


    if usuario_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con el ID {usuario_id} no existe",
        )


    db.delete(usuario_db)


    db.commit()

    return {"mensaje": f"El usuario con el ID {usuario_id} fue eliminado correctamente"}