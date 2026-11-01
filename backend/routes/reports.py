import io
from flask import Blueprint, render_template, make_response, flash, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime

from backend.models import db, Crop, DiseaseDetection, YieldPrediction, EnvironmentalData

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def index():
    uid = current_user.id
    crops       = Crop.query.filter_by(user_id=uid).order_by(Crop.created_at.desc()).all()
    detections  = (DiseaseDetection.query.filter_by(user_id=uid)
                   .order_by(DiseaseDetection.detected_at.desc()).all())
    predictions = (YieldPrediction.query.filter_by(user_id=uid)
                   .order_by(YieldPrediction.predicted_at.desc()).all())
    env_readings= (EnvironmentalData.query.filter_by(user_id=uid)
                   .order_by(EnvironmentalData.reading_date.desc()).limit(30).all())

    return render_template('reports/index.html',
                           crops=crops,
                           detections=detections,
                           predictions=predictions,
                           env_readings=env_readings)


@reports_bp.route('/reports/download/csv/<report_type>')
@login_required
def download_csv(report_type):
    uid  = current_user.id
    now  = datetime.now().strftime('%Y%m%d_%H%M%S')
    rows = []
    filename = f'{report_type}_{now}.csv'

    if report_type == 'crops':
        crops = Crop.query.filter_by(user_id=uid).all()
        rows.append('ID,Crop Name,Type,Planting Date,Field Area (ha),Location,Growth Stage,Health Status,Notes,Created At\n')
        for c in crops:
            rows.append(f'{c.id},{c.crop_name},{c.crop_type},{c.planting_date},{c.field_area},'
                        f'{c.location},{c.growth_stage},{c.health_status},{c.notes},{c.created_at}\n')

    elif report_type == 'disease':
        detections = DiseaseDetection.query.filter_by(user_id=uid).all()
        rows.append('ID,Disease Name,Confidence (%),Healthy,Detected At\n')
        for d in detections:
            rows.append(f'{d.id},{d.disease_name},{d.confidence:.1f},{d.is_healthy},{d.detected_at}\n')

    elif report_type == 'yield':
        predictions = YieldPrediction.query.filter_by(user_id=uid).all()
        rows.append('ID,Crop Type,Area (ha),Rainfall (mm),Temperature (°C),Soil Type,Fertilizer,Predicted Yield (t/ha),Predicted At\n')
        for p in predictions:
            rows.append(f'{p.id},{p.crop_type},{p.area},{p.rainfall},{p.temperature},'
                        f'{p.soil_type},{p.fertilizer},{p.predicted_yield},{p.predicted_at}\n')

    elif report_type == 'environment':
        readings = (EnvironmentalData.query.filter_by(user_id=uid)
                    .order_by(EnvironmentalData.reading_date.desc()).all())
        rows.append('ID,Temperature (°C),Humidity (%),Rainfall (mm),Soil Moisture (%),Reading Date,Notes\n')
        for r in readings:
            rows.append(f'{r.id},{r.temperature},{r.humidity},{r.rainfall},{r.soil_moisture},{r.reading_date},{r.notes}\n')
    else:
        flash('Unknown report type.', 'danger')
        return redirect(url_for('reports.index'))

    content = ''.join(rows)
    response = make_response(content)
    response.headers['Content-Type']        = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response
