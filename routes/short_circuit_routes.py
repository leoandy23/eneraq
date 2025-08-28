from flask import Blueprint, request, jsonify, render_template
from http import HTTPStatus
from core.config import SessionLocal
from services.short_circuit_service import (
    create_short_circuit,
    get_short_circuits,
    get_short_circuits_count,
)

short_circuit_bp = Blueprint("short_circuit", __name__)


@short_circuit_bp.route("/api/short-circuit", methods=["POST"])
def create_short_circuit_route():
    """
    Endpoint para crear un nuevo registro de cortocircuito.
    """
    try:
        data = request.get_json()

        # Validaciones básicas
        if not data:
            return (
                jsonify({"status": "error", "error": "No se recibieron datos JSON"}),
                HTTPStatus.BAD_REQUEST,
            )

        if "control_mac" not in data:
            return (
                jsonify(
                    {"status": "error", "error": "El campo control_mac es requerido"}
                ),
                HTTPStatus.BAD_REQUEST,
            )

        with SessionLocal() as db:
            short_circuit, error = create_short_circuit(db, data)

        if error:
            return (
                jsonify({"status": "error", "error": error}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "data": (
                        short_circuit.to_dict()
                        if hasattr(short_circuit, "to_dict")
                        else {
                            "id": short_circuit.id,
                            "control_mac": short_circuit.control_mac,
                            "wifi_mac": short_circuit.wifi_mac,
                            "timestamp": (
                                short_circuit.timestamp.isoformat()
                                if short_circuit.timestamp
                                else None
                            ),
                        }
                    ),
                }
            ),
            HTTPStatus.CREATED,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "error": f"Error interno del servidor: {str(e)}"}
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@short_circuit_bp.route("/api/short-circuits", methods=["GET"])
def get_short_circuits_route():
    """
    Endpoint para obtener registros de cortocircuitos con paginación.
    """
    try:
        # Obtener parámetros de paginación
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Validaciones
        if page < 1:
            return (
                jsonify(
                    {"status": "error", "error": "La página debe ser mayor o igual a 1"}
                ),
                HTTPStatus.BAD_REQUEST,
            )

        if per_page < 1 or per_page > 100:
            return (
                jsonify(
                    {"status": "error", "error": "per_page debe estar entre 1 y 100"}
                ),
                HTTPStatus.BAD_REQUEST,
            )

        skip = (page - 1) * per_page

        with SessionLocal() as db:
            result, error = get_short_circuits(db, skip, per_page)

        if error:
            return (
                jsonify({"status": "error", "error": error}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        # Convertir registros a diccionario
        records = []
        for record in result["records"]:
            records.append(
                {
                    "id": record.id,
                    "control_mac": record.control_mac,
                    "wifi_mac": record.wifi_mac,
                    "timestamp": (
                        record.timestamp.isoformat() if record.timestamp else None
                    ),
                    "current_active": record.current_active,
                    "current_duration_seconds": record.current_duration_seconds,
                    "previous_active": record.previous_active,
                    "previous_timestamp": (
                        record.previous_timestamp.isoformat()
                        if record.previous_timestamp
                        else None
                    ),
                    "previous_duration_seconds": record.previous_duration_seconds,
                }
            )

        total_pages = (result["total_records"] + per_page - 1) // per_page

        return (
            jsonify(
                {
                    "status": "success",
                    "data": records,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total_records": result["total_records"],
                        "total_pages": total_pages,
                    },
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "error": f"Error interno del servidor: {str(e)}"}
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@short_circuit_bp.route("/admin/short-circuits", methods=["GET"])
def admin_short_circuits():
    """
    Dashboard administrativo para cortocircuitos.
    """
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10

        skip = (page - 1) * per_page

        with SessionLocal() as db:
            result, error = get_short_circuits(db, skip, per_page)

        if error:
            return render_template("error.html", error=error)

        total_pages = (result["total_records"] + per_page - 1) // per_page

        return render_template(
            "short_circuits_dashboard.html",
            records=result["records"],
            page=page,
            per_page=per_page,
            total_records=result["total_records"],
            total_pages=total_pages,
        )

    except Exception as e:
        return render_template("error.html", error=str(e))


@short_circuit_bp.route("/api/short-circuits/count", methods=["GET"])
def get_short_circuits_count_route():
    """
    Endpoint para obtener el conteo total de cortocircuitos.
    """
    try:
        with SessionLocal() as db:
            count, error = get_short_circuits_count(db)

        if error:
            return (
                jsonify({"status": "error", "error": error}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return jsonify({"status": "success", "count": count}), HTTPStatus.OK

    except Exception as e:
        return (
            jsonify(
                {"status": "error", "error": f"Error interno del servidor: {str(e)}"}
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
