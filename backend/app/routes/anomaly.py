from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.anomaly_service import get_anomaly_analysis

anomaly_bp = Blueprint('anomaly', __name__)

@anomaly_bp.route('/anomaly/detect', methods=['GET'])
@jwt_required()
def detect_anomalies():
    """Detect anomalies using the specified method"""
    method = request.args.get('method', 'comprehensive')

    try:
        result = get_anomaly_analysis(method=method)
        return jsonify({
            "status": "success",
            "method": method,
            "parameters": request.args.to_dict(),
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@anomaly_bp.route('/anomaly/statistical', methods=['GET'])
@jwt_required()
def statistical_anomalies():
    try:
        threshold = float(request.args.get('threshold', 2.5))
        result = get_anomaly_analysis(method='statistical')
        return jsonify({
            "status": "success",
            "method": "statistical",
            "parameters": {
                "threshold": threshold
            },
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@anomaly_bp.route('/anomaly/ml', methods=['GET'])
@jwt_required()
def ml_anomalies():
    try:
        contamination = float(request.args.get('contamination', 0.05))
        result = get_anomaly_analysis(method='ml')
        return jsonify({
            "status": "success",
            "method": "ml",
            "parameters": {
                "contamination": contamination
            },
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@anomaly_bp.route('/anomaly/trends', methods=['GET'])
@jwt_required()
def trend_anomalies():
    try:
        threshold_pct = float(request.args.get('threshold_pct', 30.0))
        result = get_anomaly_analysis(method='trend')
        return jsonify({
            "status": "success",
            "method": "trend",
            "parameters": {
                "threshold_pct": threshold_pct
            },
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
