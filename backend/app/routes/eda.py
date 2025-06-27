from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.eda_service import get_eda_summary, get_detailed_breakdown, get_time_series_analysis

eda_bp = Blueprint('eda', __name__)

@eda_bp.route('/eda', methods=['GET'])
@jwt_required()
def eda():
    try:
        summary = get_eda_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@eda_bp.route('/eda/breakdown/<dimension>', methods=['GET'])
@jwt_required()
def detailed_breakdown(dimension):
    top_n = request.args.get('top_n', 10, type=int)
    
    try:
        breakdown = get_detailed_breakdown(dimension, top_n)
        return jsonify(breakdown)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@eda_bp.route('/eda/timeseries', methods=['GET'])
@jwt_required()
def time_series():
    group_by = request.args.get('group_by', 'month_year')
    try:
        analysis = get_time_series_analysis(group_by)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500