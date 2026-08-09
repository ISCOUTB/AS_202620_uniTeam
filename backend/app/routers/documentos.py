"""Router: Documentos de Activos"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.documento_activo import DocumentoActivo
from app.models.activo import Activo
from app.schemas.documento_activo import DocumentoActivoCreate, DocumentoActivoResponse
from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/activos/{activo_id}/documentos", tags=["Documentos de Activos"])


@router.get("", response_model=List[DocumentoActivoResponse])
def listar(activo_id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    activo = db.query(Activo).filter(Activo.id == activo_id).first()
    if not activo:
        not_found("Activo", str(activo_id))
    return db.query(DocumentoActivo).filter(DocumentoActivo.activo_id == activo_id).order_by(DocumentoActivo.creado_en.desc()).all()


@router.post("", response_model=DocumentoActivoResponse, status_code=201)
def crear(activo_id: UUID, data: DocumentoActivoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    activo = db.query(Activo).filter(Activo.id == activo_id).first()
    if not activo:
        not_found("Activo", str(activo_id))
    doc = DocumentoActivo(**data.model_dump(), activo_id=activo_id, subido_por=current_user.id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{id}", status_code=204)
def eliminar(activo_id: UUID, id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(require_admin)):
    doc = db.query(DocumentoActivo).filter(DocumentoActivo.id == id, DocumentoActivo.activo_id == activo_id).first()
    if not doc:
        not_found("Documento", str(id))
    db.delete(doc)
    db.commit()
    return None
