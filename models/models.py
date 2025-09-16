from sqlalchemy.orm import declarative_base, relationship
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

Base = declarative_base()


class DeviceAlive(Base):
    __tablename__ = "device_alive"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_name = Column(String(100), nullable=False)
    mac_address = Column(String(17), unique=False, nullable=False)
    serial_number = Column(String(100), unique=False, nullable=False)
    state_duration = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """
        Convierte el objeto DeviceAlive a un diccionario.
        """
        return {
            "id": str(self.id),
            "device_name": self.device_name,
            "mac_address": self.mac_address,
            "serial_number": self.serial_number,
            "state_duration": self.state_duration,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


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

    def to_dict(self, include_readings: bool = False):
        """
        Convierte el objeto EnergyDevice a un diccionario.

        Args:
            include_readings: Si es True, incluye las lecturas asociadas
        """
        result = {
            "id": str(self.id),
            "serial_number": self.serial_number,
            "firmware_version": self.firmware_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_readings and self.energy_readings:
            result["energy_readings"] = [
                reading.to_dict() for reading in self.energy_readings
            ]

        return result


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

    def to_dict(self, include_device: bool = False, include_raw_data: bool = False):
        """
        Convierte el objeto EnergyReading a un diccionario.

        Args:
            include_device: Si es True, incluye información básica del dispositivo
            include_raw_data: Si es True, incluye los datos crudos completos
        """
        result = {
            "id": str(self.id),
            "device_id": str(self.device_id),
            "alarm_status": self.alarm_status,
            "switch_status": self.switch_status,
            "current_measurements": self.current_measurements,
            "power_measurements": self.power_measurements,
            "voltage_measurements": self.voltage_measurements,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_device and self.device:
            result["device"] = {
                "serial_number": self.device.serial_number,
                "firmware_version": self.device.firmware_version,
            }

        if include_raw_data:
            result["raw_data"] = self.raw_data

        return result


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

    def to_dict(self):
        """
        Convierte el objeto ShortCircuit a un diccionario.
        """
        return {
            "id": self.id,
            "control_mac": self.control_mac,
            "wifi_mac": self.wifi_mac,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "current_active": self.current_active,
            "current_duration_seconds": self.current_duration_seconds,
            "previous_active": self.previous_active,
            "previous_timestamp": (
                self.previous_timestamp.isoformat() if self.previous_timestamp else None
            ),
            "previous_duration_seconds": self.previous_duration_seconds,
        }
