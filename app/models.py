from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Collaborator(Base):
    __tablename__ = "collaborators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(80), nullable=False)
    role: Mapped[str] = mapped_column(String(80), nullable=False)
    admission_date: Mapped[date] = mapped_column(Date, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    overtime_entries = relationship("Overtime", back_populates="collaborator")
    absences = relationship("Absence", back_populates="collaborator")
    medical_certificates = relationship("MedicalCertificate", back_populates="collaborator")
    time_punches = relationship("TimePunch", back_populates="collaborator")


class Overtime(Base):
    __tablename__ = "overtime_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collaborator_id: Mapped[int] = mapped_column(ForeignKey("collaborators.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    collaborator = relationship("Collaborator", back_populates="overtime_entries")


class Absence(Base):
    __tablename__ = "absences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collaborator_id: Mapped[int] = mapped_column(ForeignKey("collaborators.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    justified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    collaborator = relationship("Collaborator", back_populates="absences")


class MedicalCertificate(Base):
    __tablename__ = "medical_certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collaborator_id: Mapped[int] = mapped_column(ForeignKey("collaborators.id"), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    cid_code: Mapped[str] = mapped_column(String(16), nullable=True)
    document_url: Mapped[str] = mapped_column(String(255), nullable=True)

    collaborator = relationship("Collaborator", back_populates="medical_certificates")


class TimePunch(Base):
    __tablename__ = "time_punches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collaborator_id: Mapped[int] = mapped_column(ForeignKey("collaborators.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    source: Mapped[str] = mapped_column(String(20), nullable=False)  # portal | whatsapp
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    within_geofence: Mapped[bool] = mapped_column(Boolean, nullable=False)
    raw_payload: Mapped[str] = mapped_column(Text, default="", nullable=False)

    collaborator = relationship("Collaborator", back_populates="time_punches")
