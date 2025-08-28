from sqlalchemy.orm import Session
from models.models import ShortCircuit
from datetime import datetime
import dateutil.parser


def create_short_circuit(db: Session, short_circuit_data: dict):
    """
    Crea un nuevo registro de cortocircuito en la base de datos.
    """
    try:
        # Extraer datos del JSON
        control_mac = short_circuit_data.get("control_mac")
        wifi_mac = short_circuit_data.get("wifi_mac")
        timestamp_str = short_circuit_data.get("timestamp")

        # Convertir timestamp a formato MySQL compatible
        if timestamp_str:
            # Parsear el string ISO 8601 a datetime object
            timestamp = dateutil.parser.isoparse(timestamp_str)
        else:
            timestamp = datetime.utcnow()

        current = short_circuit_data.get("short_circuit", {}).get("current", {})
        previous = short_circuit_data.get("short_circuit", {}).get("previous")

        # Procesar timestamp previo si existe
        previous_timestamp_str = previous.get("timestamp") if previous else None
        previous_timestamp = None
        if previous_timestamp_str:
            previous_timestamp = dateutil.parser.isoparse(previous_timestamp_str)

        # Crear objeto ShortCircuit
        short_circuit = ShortCircuit(
            control_mac=control_mac,
            wifi_mac=wifi_mac,
            timestamp=timestamp,
            current_active=current.get("active", False),
            current_duration_seconds=current.get("duration_seconds", 0),
            previous_active=previous.get("active") if previous else None,
            previous_timestamp=previous_timestamp,
            previous_duration_seconds=(
                previous.get("duration_seconds") if previous else None
            ),
        )

        # Guardar en base de datos
        db.add(short_circuit)
        db.commit()
        db.refresh(short_circuit)

        return short_circuit, None

    except Exception as e:
        db.rollback()
        return None, str(e)


def get_short_circuits(db: Session, skip: int = 0, limit: int = 10):
    """
    Obtiene registros de cortocircuitos con paginación.
    """
    try:
        # Obtener total de registros
        total_records = db.query(ShortCircuit).count()

        # Obtener registros paginados
        records = (
            db.query(ShortCircuit)
            .order_by(ShortCircuit.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "records": records,
            "total_records": total_records,
            "skip": skip,
            "limit": limit,
        }, None

    except Exception as e:
        return None, str(e)


def get_short_circuit_by_id(db: Session, short_circuit_id: int):
    """
    Obtiene un cortocircuito por su ID.
    """
    try:
        record = (
            db.query(ShortCircuit).filter(ShortCircuit.id == short_circuit_id).first()
        )
        return record, None
    except Exception as e:
        return None, str(e)


def get_short_circuits_count(db: Session):
    """
    Obtiene el conteo total de registros de cortocircuitos.
    """
    try:
        count = db.query(ShortCircuit).count()
        return count, None
    except Exception as e:
        return None, str(e)
