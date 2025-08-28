from sqlalchemy.orm import declarative_base, relationship
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

Base = declarative_base()


class EnergyDevice(Base):
    __tablename__ = "energy_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    serial_number = Column(String(100), unique=True, nullable=False)
    firmware_version = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    energy_readings = relationship(
        "EnergyReading", back_populates="device", cascade="all, delete-orphan"
    )


class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(
        UUID(as_uuid=True), ForeignKey("energy_devices.id"), nullable=False
    )

    # Componentes principales de la lectura
    alarm_status = Column(String(50), nullable=False)  # normal, warning, critical
    switch_status = Column(
        JSON, nullable=False
    )  # {L1: false, L2: false, L3: false, N: false}
    current_measurements = Column(
        JSON, nullable=False
    )  # {leakage: 121.24, L1: 0, L2: 0, L3: 0}
    power_measurements = Column(
        JSON, nullable=False
    )  # {cos_fi: 0, apparent_power_va: 0, active_power_w: 0}
    voltage_measurements = Column(JSON, nullable=False)

    # Datos crudos completos
    raw_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    device = relationship("EnergyDevice", back_populates="energy_readings")


class ShortCircuit(Base):
    __tablename__ = "short_circuits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    control_mac = Column(String(17))
    wifi_mac = Column(String(17))
    timestamp = Column(DateTime, default=datetime.utcnow)
    current_active = Column(Boolean)
    current_duration_seconds = Column(Integer)
    previous_active = Column(Boolean, nullable=True)
    previous_timestamp = Column(DateTime, nullable=True)
    previous_duration_seconds = Column(Integer, nullable=True)
