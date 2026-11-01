from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from backend.models import db, EnvironmentalData, Crop

environment_bp = Blueprint('environment', __name__)

def get_recommendations_for_reading(temp, humidity, rainfall, soil_moisture):
    """Generate simple rule-based recommendations from sensor data."""
    recs = []
    if temp is not None:
        if temp > 35:
            recs.append(('danger', '🌡️ High Temperature', 'Temperature above 35°C can stress crops. Consider shade nets or increased irrigation.'))
        elif temp < 10:
            recs.append(('warning', '❄️ Low Temperature', 'Temperature below 10°C may damage sensitive crops. Consider protective covering.'))

    if humidity is not None:
        if humidity > 85:
            recs.append(('warning', '💧 High Humidity', 'High humidity increases risk of fungal diseases. Improve air circulation and consider fungicide application.'))
        elif humidity < 30:
            recs.append(('info', '🌬️ Low Humidity', 'Low humidity can cause moisture stress. Increase irrigation frequency.'))

    if soil_moisture is not None:
        if soil_moisture < 30:
            recs.append(('danger', '🌱 Low Soil Moisture', 'Soil moisture is critically low. Irrigate immediately to avoid crop stress.'))
        elif soil_moisture > 80:
            recs.append(('warning', '💦 Waterlogged Soil', 'Excess soil moisture can cause root rot. Improve drainage.'))

    if rainfall is not None:
        if rainfall > 50:
            recs.append(('info', '🌧️ Heavy Rainfall', 'Heavy rainfall recorded. Monitor for flooding and ensure drainage channels are clear.'))

    return recs


@environment_bp.route('/environment')
@login_required
def index():
    crops     = Crop.query.filter_by(user_id=current_user.id).all()
    # Last 20 readings
    readings  = (EnvironmentalData.query
                 .filter_by(user_id=current_user.id)
                 .order_by(EnvironmentalData.reading_date.desc())
                 .limit(20).all())
    # Latest reading
    latest    = readings[0] if readings else None
    recs      = []
    if latest:
        recs = get_recommendations_for_reading(
            latest.temperature, latest.humidity, latest.rainfall, latest.soil_moisture
        )
    return render_template('environment/index.html',
                           crops=crops, readings=readings, latest=latest, recs=recs)


@environment_bp.route('/environment/add', methods=['POST'])
@login_required
def add_reading():
    def safe_float(val):
        try:
            return float(val) if val not in (None, '') else None
        except (ValueError, TypeError):
            return None

    temp          = safe_float(request.form.get('temperature'))
    humidity      = safe_float(request.form.get('humidity'))
    rainfall      = safe_float(request.form.get('rainfall'))
    soil_moisture = safe_float(request.form.get('soil_moisture'))
    crop_id       = request.form.get('crop_id') or None
    valid_crop_id = None
    if crop_id:
        try:
            user_crop = Crop.query.filter_by(id=int(crop_id), user_id=current_user.id).first()
            valid_crop_id = user_crop.id if user_crop else None
        except (ValueError, TypeError):
            valid_crop_id = None

    notes         = request.form.get('notes', '').strip()
    reading_date_str = request.form.get('reading_date', '')

    try:
        reading_date = datetime.strptime(reading_date_str, '%Y-%m-%dT%H:%M') if reading_date_str else datetime.utcnow()
    except ValueError:
        reading_date = datetime.utcnow()

    reading = EnvironmentalData(
        user_id       = current_user.id,
        crop_id       = valid_crop_id,
        temperature   = temp,
        humidity      = humidity,
        rainfall      = rainfall,
        soil_moisture = soil_moisture,
        reading_date  = reading_date,
        notes         = notes,
    )
    db.session.add(reading)
    db.session.commit()
    flash('Environmental reading saved!', 'success')
    return redirect(url_for('environment.index'))


@environment_bp.route('/environment/chart-data')
@login_required
def chart_data():
    days_back = int(request.args.get('days', 7))
    since     = datetime.utcnow() - timedelta(days=days_back)

    rows = (EnvironmentalData.query
            .filter(EnvironmentalData.user_id == current_user.id,
                    EnvironmentalData.reading_date >= since)
            .order_by(EnvironmentalData.reading_date.asc())
            .all())

    return jsonify({
        'labels'       : [r.reading_date.strftime('%d %b %H:%M') for r in rows],
        'temperature'  : [r.temperature   for r in rows],
        'humidity'     : [r.humidity      for r in rows],
        'rainfall'     : [r.rainfall      for r in rows],
        'soil_moisture': [r.soil_moisture for r in rows],
    })


@environment_bp.route('/environment/delete/<int:reading_id>', methods=['POST'])
@login_required
def delete_reading(reading_id):
    reading = EnvironmentalData.query.filter_by(
        id=reading_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(reading)
    db.session.commit()
    flash('Reading deleted.', 'info')
    return redirect(url_for('environment.index'))
