import os
import numpy as np
import joblib
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user

from backend.models import db, YieldPrediction

yield_bp = Blueprint('yield_pred', __name__)

# Crop yield base values (tonnes/hectare) - used for rule-based fallback
CROP_BASE_YIELD = {
    'rice'    : 4.5,
    'wheat'   : 3.2,
    'corn'    : 5.8,
    'cotton'  : 1.8,
    'soybean' : 2.5,
    'potato'  : 20.0,
    'tomato'  : 35.0,
    'sugarcane': 70.0,
    'mango'   : 8.0,
    'banana'  : 25.0,
    'other'   : 3.0,
}

SOIL_FACTOR = {
    'loamy'  : 1.15,
    'clay'   : 0.90,
    'sandy'  : 0.80,
    'silty'  : 1.05,
    'peaty'  : 0.95,
    'chalky' : 0.85,
    'other'  : 1.00,
}

FERTILIZER_FACTOR = {
    'npk'       : 1.20,
    'urea'      : 1.10,
    'dap'       : 1.15,
    'potash'    : 1.05,
    'organic'   : 1.08,
    'compost'   : 1.06,
    'none'      : 1.00,
}


def rule_based_yield(crop_type, area, rainfall, temperature, soil_type, fertilizer, fertilizer_amount):
    """Rule-based fallback yield prediction when ML model is not available."""
    base   = CROP_BASE_YIELD.get(crop_type.lower(), 3.0)
    s_fac  = SOIL_FACTOR.get(soil_type.lower(),  1.0)
    f_fac  = FERTILIZER_FACTOR.get(fertilizer.lower(), 1.0)

    # Rainfall adjustment (optimal ~800mm)
    rain_adj = 1.0
    if rainfall:
        if rainfall < 400:
            rain_adj = 0.75
        elif rainfall > 1200:
            rain_adj = 0.85
        else:
            rain_adj = 0.85 + 0.15 * min((rainfall - 400) / 400, 1.0)

    # Temperature adjustment (optimal 25°C)
    temp_adj = 1.0
    if temperature:
        if temperature < 15 or temperature > 38:
            temp_adj = 0.75
        elif 20 <= temperature <= 30:
            temp_adj = 1.0
        else:
            temp_adj = 0.90

    # Fertilizer amount boost
    fert_boost = 1.0
    if fertilizer_amount and fertilizer.lower() != 'none':
        fert_boost = 1.0 + min(fertilizer_amount / 100, 0.25)

    yield_per_ha = base * s_fac * f_fac * rain_adj * temp_adj * fert_boost
    total_yield  = yield_per_ha * (area or 1.0)
    return round(yield_per_ha, 2), round(total_yield, 2)


def get_yield_model():
    """Load trained scikit-learn model and scaler."""
    model_path  = current_app.config['YIELD_MODEL_PATH']
    scaler_path = current_app.config['SCALER_PATH']
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        try:
            model  = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            return model, scaler
        except Exception as e:
            current_app.logger.error(f"Error loading yield model: {e}")
    return None, None


CROP_TYPES  = list(CROP_BASE_YIELD.keys())
SOIL_TYPES  = list(SOIL_FACTOR.keys())
FERTILIZERS = list(FERTILIZER_FACTOR.keys())


@yield_bp.route('/yield-prediction', methods=['GET', 'POST'])
@login_required
def predict():
    history = (YieldPrediction.query
               .filter_by(user_id=current_user.id)
               .order_by(YieldPrediction.predicted_at.desc())
               .limit(10).all())

    if request.method == 'POST':
        crop_type         = request.form.get('crop_type', 'other')
        area              = float(request.form.get('area', 1.0) or 1.0)
        rainfall          = float(request.form.get('rainfall', 800.0) or 800.0)
        temperature       = float(request.form.get('temperature', 25.0) or 25.0)
        soil_type         = request.form.get('soil_type', 'loamy')
        fertilizer        = request.form.get('fertilizer', 'npk')
        fertilizer_amount = float(request.form.get('fertilizer_amount', 0.0) or 0.0)

        model, scaler = get_yield_model()
        model_used    = 'ML Model'

        if model is None:
            # Fallback to rule-based
            model_used = 'Rule-Based Estimation'
            yield_per_ha, total_yield = rule_based_yield(
                crop_type, area, rainfall, temperature, soil_type, fertilizer, fertilizer_amount
            )
            flash('ℹ ML model not found. Using rule-based estimation. Train the ML model for better accuracy.', 'info')
        else:
            try:
                # Encode categoricals
                crop_enc  = CROP_TYPES.index(crop_type) if crop_type in CROP_TYPES else 0
                soil_enc  = SOIL_TYPES.index(soil_type) if soil_type in SOIL_TYPES else 0
                fert_enc  = FERTILIZERS.index(fertilizer) if fertilizer in FERTILIZERS else 0
                features  = np.array([[crop_enc, area, rainfall, temperature, soil_enc, fert_enc, fertilizer_amount]])
                scaled    = scaler.transform(features)
                predicted = float(model.predict(scaled)[0])
                yield_per_ha = round(predicted, 2)
                total_yield  = round(predicted * area, 2)
            except Exception as e:
                current_app.logger.error(f"Yield prediction error: {e}")
                model_used = 'Rule-Based Estimation'
                yield_per_ha, total_yield = rule_based_yield(
                    crop_type, area, rainfall, temperature, soil_type, fertilizer, fertilizer_amount
                )
                flash(f'ML model error: {e}. Using rule-based estimation.', 'warning')

        record = YieldPrediction(
            user_id           = current_user.id,
            crop_type         = crop_type,
            area              = area,
            rainfall          = rainfall,
            temperature       = temperature,
            soil_type         = soil_type,
            fertilizer        = fertilizer,
            fertilizer_amount = fertilizer_amount,
            predicted_yield   = yield_per_ha,
            yield_unit        = 'tonnes/hectare',
        )
        db.session.add(record)
        db.session.commit()

        return render_template('yield/result.html',
            record        = record,
            total_yield   = total_yield,
            model_used    = model_used,
            crop_types    = CROP_TYPES,
            soil_types    = SOIL_TYPES,
            fertilizers   = FERTILIZERS,
        )

    return render_template('yield/predict.html',
                           history    = history,
                           crop_types = CROP_TYPES,
                           soil_types = SOIL_TYPES,
                           fertilizers= FERTILIZERS)


@yield_bp.route('/yield-prediction/history')
@login_required
def yield_history():
    predictions = (YieldPrediction.query
                   .filter_by(user_id=current_user.id)
                   .order_by(YieldPrediction.predicted_at.desc())
                   .all())
    return render_template('yield/history.html', predictions=predictions)


@yield_bp.route('/yield-prediction/chart-data')
@login_required
def chart_data():
    predictions = (YieldPrediction.query
                   .filter_by(user_id=current_user.id)
                   .order_by(YieldPrediction.predicted_at.desc())
                   .limit(10).all())
    return jsonify({
        'labels': [f"{p.crop_type} ({p.predicted_at.strftime('%d %b')})" for p in reversed(predictions)],
        'yields': [p.predicted_yield for p in reversed(predictions)],
    })
