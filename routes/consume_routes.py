from flask import Blueprint, request, jsonify
from services.consume_service import (
    save_sensor_data,
    get_all_energy_devices_with_readings,
)
from core.config import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
import logging

consume_bp = Blueprint("consume", __name__)


@consume_bp.route("/api/save_sensor_data", methods=["POST"])
def consume_sensor_data():
    try:
        # Validar que venga JSON
        if not request.is_json:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400

        data = request.get_json()

        with SessionLocal() as db:
            record = save_sensor_data(db, data)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Sensor data saved successfully",
                    "record_id": str(record.id),
                    "device_id": str(record.device_id),
                }
            ),
            201,
        )

    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return jsonify({"status": "error", "message": str(ve)}), 400

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        return jsonify({"status": "error", "message": "Database error"}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@consume_bp.route("/api/sensor_data", methods=["GET"])
def get_sensor_data():
    try:
        with SessionLocal() as db:
            sensor_data = get_all_energy_devices_with_readings(db)
            return (
                jsonify(
                    {
                        "status": "success",
                        "data": sensor_data,
                    }
                ),
                200,
            )

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        return jsonify({"status": "error", "message": "Database error"}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
