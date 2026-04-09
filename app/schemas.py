from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field


class CollaboratorCreate(BaseModel):
    full_name: str = Field(min_length=3)
    email: EmailStr
    department: str
    role: str
    admission_date: date


class CollaboratorOut(CollaboratorCreate):
    id: int
    active: bool

    model_config = {"from_attributes": True}


class OvertimeCreate(BaseModel):
    collaborator_id: int
    date: date
    hours: float = Field(gt=0)
    reason: str = Field(min_length=3)


class AbsenceCreate(BaseModel):
    collaborator_id: int
    date: date
    justified: bool = False
    notes: str = ""


class MedicalCertificateCreate(BaseModel):
    collaborator_id: int
    issue_date: date
    start_date: date
    end_date: date
    cid_code: str | None = None
    document_url: str | None = None


class TimePunchCreate(BaseModel):
    collaborator_id: int
    latitude: float
    longitude: float


class WhatsAppLocationPayload(BaseModel):
    collaborator_id: int
    latitude: float
    longitude: float
    event_id: str | None = None
    raw_payload: dict | None = None


class TimePunchOut(BaseModel):
    id: int
    collaborator_id: int
    timestamp: datetime
    source: str
    latitude: float
    longitude: float
    within_geofence: bool

    model_config = {"from_attributes": True}


class CollaboratorDashboard(BaseModel):
    collaborator: CollaboratorOut
    month_overtime_hours: float
    month_absences: int
    open_medical_certificates: int
    today_punches: int
