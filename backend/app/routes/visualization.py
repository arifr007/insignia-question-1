from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.visualization_service import get_visualization_data
from app.services.anomaly_service import get_anomaly_analysis
from app.services.rca_service import perform_comprehensive_rca
from app.models.mongo import ChatMessage

visualization_bp = Blueprint('visualization', __name__)

def save_chart_to_chat(room_id, chart_data, chart_type, summary_data=None):
    if not room_id:
        return
    
    try:
        # Create a formatted message with chart data
        message_content = f"Here's your {chart_type.replace('_', ' ').title()} chart:"
        
        # Save the chart message with chart_data embedded
        ChatMessage.add_message(
            room_id=room_id,
            message_type='bot',
            content=message_content,
            intent=f'chart_{chart_type}',
            query=None,
            chart_data=chart_data,
            summary=summary_data
        )
    except Exception as e:
        print(f"Error saving chart to chat: {str(e)}")

@visualization_bp.route('/charts/trend', methods=['GET'])
@jwt_required()
def trend_chart():
    room_id = request.args.get('room_id')  # Optional room_id for chat integration
    
    try:
        chart_data = get_visualization_data('trend')
        
        # Save to chat if room_id provided
        if room_id:
            save_chart_to_chat(room_id, chart_data, 'trend', chart_data.get('summary'))
        
        return jsonify({
            "status": "success",
            "data": chart_data,
            "saved_to_chat": bool(room_id)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@visualization_bp.route('/charts/category-breakdown', methods=['GET'])
@jwt_required()
def category_breakdown_chart():
    room_id = request.args.get('room_id')  # Optional room_id for chat integration
    
    try:
        chart_data = get_visualization_data('category_breakdown')
        
        # Save to chat if room_id provided
        if room_id:
            save_chart_to_chat(room_id, chart_data, 'category_breakdown', chart_data.get('summary'))
        
        return jsonify({
            "status": "success",
            "data": chart_data,
            "saved_to_chat": bool(room_id)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@visualization_bp.route('/charts/heatmap', methods=['GET'])
@jwt_required()
def heatmap_chart():
    room_id = request.args.get('room_id')
    
    try:
        chart_data = get_visualization_data('heatmap')
        if room_id:
            save_chart_to_chat(room_id, chart_data, 'heatmap', chart_data.get('summary'))
        
        return jsonify({
            "status": "success",
            "data": chart_data,
            "saved_to_chat": bool(room_id)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@visualization_bp.route('/charts/anomaly-scatter', methods=['GET'])
@jwt_required()
def anomaly_scatter_chart():
    room_id = request.args.get('room_id')
    method = request.args.get('method', 'ml')
    
    try:
        anomaly_response = get_anomaly_analysis(method=method)
        if method == 'comprehensive':
            anomaly_data = anomaly_response.get('ml_anomalies', {})
        else:
            anomaly_data = anomaly_response
        
        chart_data = get_visualization_data('anomaly_scatter', anomaly_data=anomaly_data)
        
        if room_id:
            save_chart_to_chat(room_id, chart_data, 'anomaly_scatter', chart_data.get('summary'))
        
        return jsonify({
            "status": "success",
            "data": chart_data,
            "saved_to_chat": bool(room_id)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@visualization_bp.route('/charts/rca-waterfall', methods=['POST'])
@jwt_required()
def rca_waterfall_chart():
    room_id = request.args.get('room_id')
    data = request.json
    category = data.get('category')
    from_month = data.get('from_month')
    to_month = data.get('to_month')
    
    if not all([category, from_month, to_month]):
        return jsonify({
            "status": "error",
            "message": "Missing required parameters: category, from_month, to_month"
        }), 400
    
    try:
        rca_data = perform_comprehensive_rca(category, from_month, to_month)
        chart_data = get_visualization_data('rca_waterfall', rca_data=rca_data.get('basic_rca', {}))
        if room_id:
            save_chart_to_chat(room_id, chart_data, 'rca_waterfall', rca_data.get('summary'))
        
        return jsonify({
            "status": "success",
            "data": chart_data,
            "rca_analysis": rca_data,
            "saved_to_chat": bool(room_id)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@visualization_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard_data():
    """Get comprehensive dashboard data"""
    category = request.args.get('category')
    
    try:
        dashboard_data = get_visualization_data('dashboard', category=category)
        return jsonify({
            "status": "success",
            "data": dashboard_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@visualization_bp.route('/charts/available', methods=['GET'])
@jwt_required()
def available_charts():
    charts = [
        {
            "type": "trend",
            "name": "Monthly Trend Chart",
            "description": "Line chart showing expense trends over time",
            "endpoint": "/charts/trend",
            "parameters": ["category (optional)"]
        },
        {
            "type": "category_breakdown",
            "name": "Category Breakdown",
            "description": "Pie chart showing expense distribution by category",
            "endpoint": "/charts/category-breakdown",
            "parameters": []
        },
        {
            "type": "heatmap",
            "name": "Cost Center Heatmap",
            "description": "Heatmap showing cost center spending patterns",
            "endpoint": "/charts/heatmap",
            "parameters": ["category (optional)"]
        },
        {
            "type": "anomaly_scatter",
            "name": "Anomaly Scatter Plot",
            "description": "Scatter plot highlighting anomalous expenses",
            "endpoint": "/charts/anomaly-scatter",
            "parameters": ["category (optional)", "method (optional)"]
        },
        {
            "type": "rca_waterfall",
            "name": "RCA Waterfall Chart",
            "description": "Waterfall chart showing root cause analysis",
            "endpoint": "/charts/rca-waterfall",
            "parameters": ["category", "from_month", "to_month"]
        }
    ]
    
    return jsonify({
        "status": "success",
        "data": {
            "available_charts": charts,
            "total_charts": len(charts)
        }
    })
