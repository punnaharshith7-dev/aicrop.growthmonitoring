from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from backend.models import db, Recommendation, Crop, EnvironmentalData, DiseaseDetection

recommendations_bp = Blueprint('recommendations', __name__)

# ── Rule engine ───────────────────────────────────────────────────────────────
def generate_recommendations(user_id):
    """Generate smart farming recommendations based on stored data."""
    recs = []

    # Get latest environmental reading
    env = (EnvironmentalData.query
           .filter_by(user_id=user_id)
           .order_by(EnvironmentalData.reading_date.desc())
           .first())

    # Get crops
    crops = Crop.query.filter_by(user_id=user_id).all()

    if env:
        # Watering recommendations
        if env.soil_moisture is not None and env.soil_moisture < 35:
            recs.append({
                'rec_type'      : 'Watering',
                'recommendation': f'Soil moisture is at {env.soil_moisture}% which is below the optimal range (35–65%). '
                                  f'Irrigate your crops immediately. Apply 25–30 mm of water.',
                'priority'      : 'High',
            })
        elif env.soil_moisture is not None and env.soil_moisture > 75:
            recs.append({
                'rec_type'      : 'Watering',
                'recommendation': f'Soil moisture is at {env.soil_moisture}%. Excess moisture detected. '
                                  f'Stop irrigation and improve field drainage to prevent root rot.',
                'priority'      : 'High',
            })

        # Fertilizer recommendations based on temperature
        if env.temperature is not None:
            if 20 <= env.temperature <= 30:
                recs.append({
                    'rec_type'      : 'Fertilizer',
                    'recommendation': f'Temperature is optimal ({env.temperature}°C). This is a good time for fertilizer application. '
                                      f'Apply NPK fertilizer (20-20-20) at recommended rates.',
                    'priority'      : 'Normal',
                })
            elif env.temperature > 35:
                recs.append({
                    'rec_type'      : 'Fertilizer',
                    'recommendation': f'High temperature ({env.temperature}°C) detected. Avoid fertilizer application during extreme heat '
                                      f'to prevent root burn. Wait for cooler conditions.',
                    'priority'      : 'High',
                })

        # Humidity-based disease prevention
        if env.humidity is not None and env.humidity > 80:
            recs.append({
                'rec_type'      : 'Disease Prevention',
                'recommendation': f'High humidity ({env.humidity}%) detected. Risk of fungal diseases (blight, rust, mold) is elevated. '
                                  f'Apply preventive fungicide (Mancozeb or Copper Oxychloride) at 2g/L.',
                'priority'      : 'High',
            })

    # Crop-specific recommendations
    for crop in crops:
        if crop.health_status == 'Diseased':
            recs.append({
                'rec_type'      : 'Disease Prevention',
                'recommendation': f'Crop "{crop.crop_name}" has been flagged as Diseased. '
                                  f'Isolate the affected field section, remove infected plant parts, '
                                  f'and consult the disease detection module for specific treatment.',
                'priority'      : 'High',
                'crop_id'       : crop.id,
            })

    # General recommendations
    recs += [
        {
            'rec_type'      : 'Crop Care',
            'recommendation': 'Conduct weekly field inspection for pest activity. Check for whiteflies, aphids, and caterpillars. '
                              'Apply neem oil spray (5ml/L) as a preventive bio-pesticide.',
            'priority'      : 'Normal',
        },
        {
            'rec_type'      : 'Crop Care',
            'recommendation': 'Ensure proper weed management. Remove weeds within 3 weeks of planting to avoid competition for nutrients.',
            'priority'      : 'Normal',
        },
    ]

    return recs


@recommendations_bp.route('/recommendations')
@login_required
def index():
    # Auto-generate new recommendations
    generated = generate_recommendations(current_user.id)
    for rec_data in generated:
        rec = Recommendation(
            user_id        = current_user.id,
            crop_id        = rec_data.get('crop_id'),
            rec_type       = rec_data['rec_type'],
            recommendation = rec_data['recommendation'],
            priority       = rec_data['priority'],
        )
        db.session.add(rec)
    db.session.commit()

    # Fetch all recommendations
    all_recs = (Recommendation.query
                .filter_by(user_id=current_user.id)
                .order_by(Recommendation.created_at.desc())
                .all())

    # Group by type
    grouped = {}
    for r in all_recs:
        grouped.setdefault(r.rec_type, []).append(r)

    return render_template('recommendations/index.html',
                           all_recs=all_recs, grouped=grouped)


@recommendations_bp.route('/recommendations/mark-read/<int:rec_id>', methods=['POST'])
@login_required
def mark_read(rec_id):
    rec = Recommendation.query.filter_by(id=rec_id, user_id=current_user.id).first_or_404()
    rec.is_read = True
    db.session.commit()
    return jsonify({'status': 'ok'})


@recommendations_bp.route('/recommendations/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    Recommendation.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All recommendations marked as read.', 'success')
    return redirect(url_for('recommendations.index'))


@recommendations_bp.route('/recommendations/delete/<int:rec_id>', methods=['POST'])
@login_required
def delete_rec(rec_id):
    rec = Recommendation.query.filter_by(id=rec_id, user_id=current_user.id).first_or_404()
    db.session.delete(rec)
    db.session.commit()
    return jsonify({'status': 'deleted'})
