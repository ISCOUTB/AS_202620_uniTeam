"""Router: Reportes"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.exportacion_reporte import ExportacionReporte
from app.schemas.reporte import ReporteCreate, ReporteResponse
from app.core.dependencies import get_current_user
from app.core.exceptions import not_found
from app.models.usuario import Usuario

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("", response_model=List[ReporteResponse])
def listar(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return db.query(ExportacionReporte).filter(
        ExportacionReporte.solicitado_por == current_user.id
    ).order_by(ExportacionReporte.creado_en.desc()).all()


@router.post("", response_model=ReporteResponse, status_code=201)
def solicitar(data: ReporteCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    reporte = ExportacionReporte(
        solicitado_por=current_user.id,
        tipo_reporte=data.tipo_reporte,
        formato_archivo=data.formato_archivo,
        filtros=data.filtros,
    )
    db.add(reporte)
    db.commit()
    db.refresh(reporte)
    return reporte


@router.get("/{id}", response_model=ReporteResponse)
def obtener(id: UUID, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    reporte = db.query(ExportacionReporte).filter(ExportacionReporte.id == id).first()
    if not reporte:
        not_found("Reporte", str(id))
    return reporte
