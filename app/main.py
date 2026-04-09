from datetime import date, datetime
import json
import os

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import and_, extract, func
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Absence, Collaborator, MedicalCertificate, Overtime, TimePunch
from app.schemas import (
    AbsenceCreate,
    CollaboratorCreate,
    CollaboratorDashboard,
    CollaboratorOut,
    MedicalCertificateCreate,
    OvertimeCreate,
    TimePunchCreate,
    TimePunchOut,
    WhatsAppLocationPayload,
)
from app.services.geofence import inside_geofence

COMPANY_LAT = float(os.getenv("COMPANY_LAT", "-23.55052"))
COMPANY_LON = float(os.getenv("COMPANY_LON", "-46.633308"))
GEOFENCE_RADIUS_M = float(os.getenv("GEOFENCE_RADIUS_M", "300"))

app = FastAPI(title="Sistema RH", version="1.0.0")
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post("/collaborators", response_model=CollaboratorOut)
def create_collaborator(payload: CollaboratorCreate, db: Session = Depends(get_db)):
    existing = db.query(Collaborator).filter(Collaborator.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    collaborator = Collaborator(**payload.model_dump())
    db.add(collaborator)
    db.commit()
    db.refresh(collaborator)
    return collaborator


@app.get("/collaborators/{collaborator_id}", response_model=CollaboratorOut)
def get_collaborator(collaborator_id: int, db: Session = Depends(get_db)):
    collaborator = db.get(Collaborator, collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    return collaborator


@app.post("/overtime")
def register_overtime(payload: OvertimeCreate, db: Session = Depends(get_db)):
    collaborator = db.get(Collaborator, payload.collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    overtime = Overtime(**payload.model_dump())
    db.add(overtime)
    db.commit()
    return {"message": "Hora extra registrada"}


@app.post("/absences")
def register_absence(payload: AbsenceCreate, db: Session = Depends(get_db)):
    collaborator = db.get(Collaborator, payload.collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    absence = Absence(**payload.model_dump())
    db.add(absence)
    db.commit()
    return {"message": "Falta registrada"}


@app.post("/medical-certificates")
def register_medical_certificate(payload: MedicalCertificateCreate, db: Session = Depends(get_db)):
    collaborator = db.get(Collaborator, payload.collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="Data final não pode ser menor que data inicial")

    certificate = MedicalCertificate(**payload.model_dump())
    db.add(certificate)
    db.commit()
    return {"message": "Atestado registrado"}


def create_time_punch(
    db: Session,
    collaborator_id: int,
    latitude: float,
    longitude: float,
    source: str,
    raw_payload: str = "",
):
    collaborator = db.get(Collaborator, collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    within_geofence = inside_geofence(
        point_lat=latitude,
        point_lon=longitude,
        company_lat=COMPANY_LAT,
        company_lon=COMPANY_LON,
        allowed_radius_m=GEOFENCE_RADIUS_M,
    )

    punch = TimePunch(
        collaborator_id=collaborator_id,
        source=source,
        latitude=latitude,
        longitude=longitude,
        within_geofence=within_geofence,
        raw_payload=raw_payload,
    )
    db.add(punch)
    db.commit()
    db.refresh(punch)
    return punch


@app.post("/time-punches/portal", response_model=TimePunchOut)
def punch_from_portal(payload: TimePunchCreate, db: Session = Depends(get_db)):
    return create_time_punch(
        db,
        collaborator_id=payload.collaborator_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        source="portal",
    )


@app.post("/integrations/evolution/time-punch", response_model=TimePunchOut)
def punch_from_whatsapp_location(payload: WhatsAppLocationPayload, db: Session = Depends(get_db)):
    raw_payload = json.dumps(payload.raw_payload or {}, ensure_ascii=False)
    return create_time_punch(
        db,
        collaborator_id=payload.collaborator_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        source="whatsapp",
        raw_payload=raw_payload,
    )


@app.get("/collaborators/{collaborator_id}/dashboard", response_model=CollaboratorDashboard)
def collaborator_dashboard(collaborator_id: int, db: Session = Depends(get_db)):
    collaborator = db.get(Collaborator, collaborator_id)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")

    today = date.today()
    month = today.month
    year = today.year

    overtime_hours = (
        db.query(func.coalesce(func.sum(Overtime.hours), 0.0))
        .filter(
            Overtime.collaborator_id == collaborator_id,
            extract("month", Overtime.date) == month,
            extract("year", Overtime.date) == year,
        )
        .scalar()
    )

    absences_count = (
        db.query(func.count(Absence.id))
        .filter(
            Absence.collaborator_id == collaborator_id,
            extract("month", Absence.date) == month,
            extract("year", Absence.date) == year,
        )
        .scalar()
    )

    open_certificates = (
        db.query(func.count(MedicalCertificate.id))
        .filter(
            MedicalCertificate.collaborator_id == collaborator_id,
            and_(MedicalCertificate.start_date <= today, MedicalCertificate.end_date >= today),
        )
        .scalar()
    )

    today_punches = (
        db.query(func.count(TimePunch.id))
        .filter(
            TimePunch.collaborator_id == collaborator_id,
            func.date(TimePunch.timestamp) == today,
        )
        .scalar()
    )

    return {
        "collaborator": collaborator,
        "month_overtime_hours": float(overtime_hours),
        "month_absences": absences_count,
        "open_medical_certificates": open_certificates,
        "today_punches": today_punches,
    }
