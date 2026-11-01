from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func

from backend.models import db, Crop, DiseaseDetection, EnvironmentalData, YieldPrediction, Recommendation

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    uid = current_user.id

    # Summary stats
    total_crops    = Crop.query.filter_by(user_id=uid).count()
    healthy_crops  = Crop.query.filter_by(user_id=uid, health_status='Healthy').count()
    diseased_crops = Crop.query.filter_by(user_id=uid, health_status='Diseased').count()
    total_detections = DiseaseDetection.query.filter_by(user_id=uid).count()
    total_predictions = YieldPrediction.query.filter_by(user_id=uid).count()

    # Latest environmental reading
    latest_env = (EnvironmentalData.query
                  .filter_by(user_id=uid)
                  .order_by(EnvironmentalData.reading_date.desc())
                  .first())

    # Recent crops (last 5)
    recent_crops = (Crop.query
                    .filter_by(user_id=uid)
                    .order_by(Crop.created_at.desc())
                    .limit(5).all())

    # Recent disease detections (last 5)
    recent_detections = (DiseaseDetection.query
                         .filter_by(user_id=uid)
                         .order_by(DiseaseDetection.detected_at.desc())
                         .limit(5).all())

    # Unread recommendations
    unread_recs = (Recommendation.query
                   .filter_by(user_id=uid, is_read=False)
                   .order_by(Recommendation.created_at.desc())
                   .limit(5).all())

    return render_template('dashboard/index.html',
        total_crops       = total_crops,
        healthy_crops     = healthy_crops,
        diseased_crops    = diseased_crops,
        total_detections  = total_detections,
        total_predictions = total_predictions,
        latest_env        = latest_env,
        recent_crops      = recent_crops,
        recent_detections = recent_detections,
        unread_recs       = unread_recs,
    )


@dashboard_bp.route('/dashboard/chart-data')
@login_required
def chart_data():
    """Return JSON for dashboard charts (last 7 days environmental data)."""
    uid = current_user.id
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    rows = (EnvironmentalData.query
            .filter(EnvironmentalData.user_id == uid,
                    EnvironmentalData.reading_date >= seven_days_ago)
            .order_by(EnvironmentalData.reading_date.asc())
            .all())

    labels       = [r.reading_date.strftime('%d %b') for r in rows]
    temperature  = [r.temperature  for r in rows]
    humidity     = [r.humidity     for r in rows]
    soil_moisture= [r.soil_moisture for r in rows]
    rainfall     = [r.rainfall     for r in rows]

    # Health breakdown
    healthy  = Crop.query.filter_by(user_id=uid, health_status='Healthy').count()
    diseased = Crop.query.filter_by(user_id=uid, health_status='Diseased').count()
    at_risk  = Crop.query.filter_by(user_id=uid, health_status='At Risk').count()

    return jsonify({
        'env': {
            'labels'      : labels,
            'temperature' : temperature,
            'humidity'    : humidity,
            'soil_moisture': soil_moisture,
            'rainfall'    : rainfall,
        },
        'health': {
            'healthy' : healthy,
            'diseased': diseased,
            'at_risk' : at_risk,
        }
    })
