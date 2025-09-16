from typing import List
from models.models import EnergyDevice, EnergyReading, DeviceAlive
from sqlalchemy.orm import Session, joinedload
from datetime import datetime


def save_sensor_data(db: Session, sensor_data: dict):
    """
    Guarda los datos del sensor en la base de datos.
    - Si el dispositivo no existe, lo crea.
    - Inserta un registro con la data recibida.
    """

    if "serial_number" in sensor_data:
        serial_number = sensor_data["serial_number"]
        device_name = sensor_data.get("device_name", "Unknown Device")
        mac_address = sensor_data.get("mac_address", "00:00:00:00:00:00")
        state_duration = sensor_data.get("state_duration", 0)
        timestamp_str = sensor_data.get("timestamp")
        timestamp = (
            datetime.fromisoformat(timestamp_str)
            if timestamp_str
            else datetime.utcnow()
        )

        device_alive = DeviceAlive(
            device_name=device_name,
            mac_address=mac_address,
            serial_number=serial_number,
            state_duration=state_duration,
            timestamp=timestamp,
        )
        db.add(device_alive)
        db.commit()
        db.refresh(device_alive)
        return device_alive
    else:
        # Extraer detalles principales del JSON
        stm32_details = sensor_data.get("stm32_details", {})
        serial_number = stm32_details.get("serial_number")
        firmware_version = stm32_details.get("firmware_version")

        if not serial_number:
            raise ValueError("El JSON recibido no contiene 'serial_number'")

        # 1️⃣ Buscar dispositivo por serial_number
        device = (
            db.query(EnergyDevice)
            .filter(EnergyDevice.serial_number == serial_number)
            .first()
        )

        # 2️⃣ Si no existe, lo creamos
        if not device:
            device = EnergyDevice(
                serial_number=serial_number,
                firmware_version=firmware_version,
            )
            db.add(device)
            db.flush()  # Para obtener el id sin hacer commit todavía

        # 3️⃣ Crear un nuevo registro con la info
        record = EnergyReading(
            device_id=device.id,
            alarm_status=sensor_data.get("alarm_status", {}).get("status", "unknown"),
            switch_status=sensor_data.get("ln_switch_status", {}),
            current_measurements=sensor_data.get("currents", {}),
            power_measurements=sensor_data.get("measurements", {}),
            voltage_measurements=sensor_data.get("voltages", {}),
            raw_data=sensor_data,
        )

        db.add(record)

        # 4️⃣ Guardar cambios
        db.commit()
        db.refresh(record)

        return record


def get_all_energy_devices_with_readings(db: Session) -> List[dict]:
    """
    Obtiene todos los dispositivos de energía con sus lecturas asociadas.
    Retorna una lista de diccionarios.
    """
    devices = (
        db.query(EnergyDevice).options(joinedload(EnergyDevice.energy_readings)).all()
    )
    return [device.to_dict(include_readings=True) for device in devices]
