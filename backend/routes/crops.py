import os
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.models import db, Crop
from backend.crop_config import (
    CROP_PROFILES, GROWTH_STAGES, STAGE_METADATA,
    calculate_crop_growth, get_crop_profile
)

crops_bp = Blueprint('crops', __name__)

# Legacy compatibility mapping
CROP_INFO = {k: {'stages': GROWTH_STAGES, 'total_days': v['total_days']} for k, v in CROP_PROFILES.items()}


def get_growth_info(crop_type, planting_date, custom_variety=None):
    """
    Calculate and return complete growth telemetry:
    - 6 standard stages (Germination, Seedling, Vegetative, Flowering, Fruiting, Harvesting)
    - Elapsed days, progress percentage, expected harvest date
    - Stage sub-progress, milestones, and S-curve data points
    """
    return calculate_crop_growth(crop_type, planting_date, custom_variety)


@crops_bp.route('/crops')
@login_required
def list_crops():
    """List all registered crops for the authenticated farmer with growth progress."""
    crops = Crop.query.filter_by(user_id=current_user.id).order_by(Crop.created_at.desc()).all()
    crop_data = []

    # Aggregated farm analytics
    total_area = 0.0
    stage_counts = {st: 0 for st in GROWTH_STAGES}
    approaching_harvest = 0

    for c in crops:
        g = get_growth_info(c.crop_type or 'other', c.planting_date, c.crop_variety)
        crop_data.append({'crop': c, 'growth': g})

        if c.field_area:
            total_area += float(c.field_area)

        curr_st = g['current_stage']
        if curr_st in stage_counts:
            stage_counts[curr_st] += 1

        if g['days_remaining'] <= 14:
            approaching_harvest += 1

    summary_stats = {
        'total_crops': len(crops),
        'total_area': round(total_area, 2),
        'stage_counts': stage_counts,
        'approaching_harvest': approaching_harvest
    }

    return render_template(
        'crops/list.html',
        crop_data=crop_data,
        crop_types=list(CROP_PROFILES.keys()),
        crop_profiles=CROP_PROFILES,
        summary_stats=summary_stats
    )


@crops_bp.route('/crops/add', methods=['GET', 'POST'])
@login_required
def add_crop():
    """Register a new crop field with variety, planting date, and area."""
    if request.method == 'POST':
        crop_name    = request.form.get('crop_name', '').strip()
        crop_type    = request.form.get('crop_type', 'other').strip().lower()
        crop_variety = request.form.get('crop_variety', '').strip()
        planting_str = request.form.get('planting_date', '')
        field_area   = request.form.get('field_area')
        location     = request.form.get('location', '').strip()
        notes        = request.form.get('notes', '').strip()

        if not crop_name or not planting_str:
            flash('Crop name and planting date are required.', 'danger')
            return render_template('crops/add.html', crop_types=list(CROP_PROFILES.keys()), crop_profiles=CROP_PROFILES)

        try:
            planting_date = datetime.strptime(planting_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid planting date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('crops/add.html', crop_types=list(CROP_PROFILES.keys()), crop_profiles=CROP_PROFILES)

        try:
            field_area_val = float(field_area) if field_area else None
            if field_area_val is not None and field_area_val < 0:
                flash('Land area cannot be negative.', 'danger')
                return render_template('crops/add.html', crop_types=list(CROP_PROFILES.keys()), crop_profiles=CROP_PROFILES)
        except ValueError:
            field_area_val = None

        # Auto-calculate growth stage and expected harvest
        g = get_growth_info(crop_type, planting_date, crop_variety)

        crop = Crop(
            user_id       = current_user.id,
            crop_name     = crop_name,
            crop_type     = crop_type,
            crop_variety  = crop_variety or (g['available_varieties'][0] if g['available_varieties'] else None),
            planting_date = planting_date,
            field_area    = field_area_val,
            location      = location or None,
            growth_stage  = g['current_stage'],
            health_status = 'Healthy',
            notes         = notes or None,
        )
        db.session.add(crop)
        db.session.commit()
        flash(f'Crop "{crop_name}" added successfully! Target harvest: {g["harvest_date"].strftime("%d %B %Y")}.', 'success')
        return redirect(url_for('crops.crop_detail', crop_id=crop.id))

    return render_template(
        'crops/add.html',
        crop_types=list(CROP_PROFILES.keys()),
        crop_profiles=CROP_PROFILES,
        growth_stages=GROWTH_STAGES
    )


@crops_bp.route('/crops/<int:crop_id>')
@login_required
def crop_detail(crop_id):
    """Detailed crop growth monitoring dashboard with milestone progress and charts."""
    crop = Crop.query.filter_by(id=crop_id, user_id=current_user.id).first_or_404()
    growth = get_growth_info(crop.crop_type or 'other', crop.planting_date, crop.crop_variety)

    return render_template(
        'crops/detail.html',
        crop=crop,
        growth=growth,
        growth_stages=GROWTH_STAGES,
        stage_metadata=STAGE_METADATA
    )


@crops_bp.route('/crops/<int:crop_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_crop(crop_id):
    """Update crop specifications, variety, planting date, or confirmed stage."""
    crop = Crop.query.filter_by(id=crop_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        crop.crop_name     = request.form.get('crop_name', crop.crop_name or '').strip()
        crop.crop_type     = (request.form.get('crop_type') or crop.crop_type or 'other').strip().lower()
        crop.crop_variety  = (request.form.get('crop_variety') or crop.crop_variety or '').strip()
        crop.health_status = request.form.get('health_status') or crop.health_status or 'Healthy'

        loc_val = request.form.get('location')
        if loc_val is not None:
            crop.location = loc_val.strip() or None

        notes_val = request.form.get('notes')
        if notes_val is not None:
            crop.notes = notes_val.strip() or None

        planting_str = request.form.get('planting_date')
        if planting_str:
            try:
                crop.planting_date = datetime.strptime(planting_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        try:
            crop.field_area = float(request.form.get('field_area', crop.field_area))
        except (ValueError, TypeError):
            pass

        # Allow manual stage confirmation or auto-calculate
        manual_stage = request.form.get('growth_stage')
        if manual_stage and manual_stage in GROWTH_STAGES:
            crop.growth_stage = manual_stage
        else:
            g = get_growth_info(crop.crop_type or 'other', crop.planting_date, crop.crop_variety)
            crop.growth_stage = g['current_stage']

        db.session.commit()
        flash('Crop field parameters updated successfully!', 'success')
        return redirect(url_for('crops.crop_detail', crop_id=crop.id))

    growth = get_growth_info(crop.crop_type or 'other', crop.planting_date, crop.crop_variety)
    return render_template(
        'crops/edit.html',
        crop=crop,
        growth=growth,
        crop_types=list(CROP_PROFILES.keys()),
        crop_profiles=CROP_PROFILES,
        growth_stages=GROWTH_STAGES
    )


@crops_bp.route('/crops/<int:crop_id>/delete', methods=['POST'])
@login_required
def delete_crop(crop_id):
    """Delete a crop field and all cascade records."""
    crop = Crop.query.filter_by(id=crop_id, user_id=current_user.id).first_or_404()
    crop_name = crop.crop_name
    db.session.delete(crop)
    db.session.commit()
    flash(f'Crop record "{crop_name}" deleted.', 'info')
    return redirect(url_for('crops.list_crops'))


@crops_bp.route('/crops/<int:crop_id>/growth-data')
@login_required
def growth_data(crop_id):
    """API endpoint providing comprehensive telemetry for interactive charts."""
    crop = Crop.query.filter_by(id=crop_id, user_id=current_user.id).first_or_404()
    g = get_growth_info(crop.crop_type or 'other', crop.planting_date, crop.crop_variety)

    # Convert date objects to string for JSON serialization
    clean_stages = []
    for s in g['stages']:
        sc = dict(s)
        sc['start_date'] = sc['start_date'].strftime('%Y-%m-%d')
        sc['end_date']   = sc['end_date'].strftime('%Y-%m-%d')
        clean_stages.append(sc)

    return jsonify({
        'crop_id': crop.id,
        'crop_name': crop.crop_name,
        'crop_type': crop.crop_type,
        'crop_variety': crop.crop_variety,
        'planting_date': crop.planting_date.strftime('%Y-%m-%d'),
        'harvest_date': g['harvest_date'].strftime('%Y-%m-%d'),
        'elapsed_days': g['elapsed_days'],
        'total_days': g['total_days'],
        'days_remaining': g['days_remaining'],
        'progress': g['progress'],
        'current_stage': g['current_stage'],
        'current_stage_index': g['current_stage_index'],
        'stage_progress_percent': g['stage_progress_percent'],
        'stages': clean_stages,
        'chart': g['chart']
    })


@crops_bp.route('/crops/api/profile/<crop_type>')
@login_required
def api_crop_profile(crop_type):
    """API returning configurable varieties and duration for frontend dynamic selection."""
    profile = get_crop_profile(crop_type)
    return jsonify({
        'crop_type': crop_type,
        'display_name': profile['display_name'],
        'category': profile['category'],
        'total_days': profile['total_days'],
        'varieties': profile['varieties'],
        'stage_durations': profile['stage_durations']
    })
