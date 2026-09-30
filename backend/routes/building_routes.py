from flask import Blueprint, jsonify
from models.building import Building

building_bp = Blueprint("building", __name__)


@building_bp.route("/", methods=["GET"])
def get_all_buildings():
    """جلب جميع المباني"""
    buildings = Building.get_all()
    return jsonify({"buildings": buildings, "count": len(buildings)}), 200


@building_bp.route("/<int:building_id>", methods=["GET"])
def get_building(building_id):
    """جلب مبنى بالمعرف"""
    building = Building.get_by_id(building_id)
    if not building:
        return jsonify({"error": "المبنى غير موجود"}), 404
    return jsonify({"building": building}), 200


@building_bp.route("/code/<string:building_code>", methods=["GET"])
def get_building_by_code(building_code):
    """جلب مبنى بالكود"""
    building = Building.get_by_code(building_code)
    if not building:
        return jsonify({"error": "المبنى غير موجود"}), 404
    return jsonify({"building": building}), 200