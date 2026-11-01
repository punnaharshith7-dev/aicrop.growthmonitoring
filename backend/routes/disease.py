import os
import uuid
import numpy as np
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import cv2

from backend.models import db, DiseaseDetection, Crop
from ml.disease_detection.disease_db import DISEASE_DATABASE, get_disease_info
from ml.disease_detection.preprocess import preprocess_image_cv2, preprocess_for_pytorch
from ml.disease_detection.model import MODEL_CLASSES, load_class_indices, build_pytorch_cnn

disease_bp = Blueprint('disease', __name__)

# Cached model instance in memory
_CACHED_MODEL = None
_CACHED_MODEL_TYPE = None


def allowed_file(filename):
    """Verify uploaded file extension against whitelist."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def get_trained_model():
    """
    Load trained CNN model. Supports:
    1. Keras/TensorFlow .h5 model (Config.DISEASE_MODEL_PATH)
    2. PyTorch .pth model (ml/disease_detection/disease_model.pth)
    3. OpenCV DNN .onnx model (ml/disease_detection/disease_model.onnx)
    Returns (model, model_type) or (None, None).
    """
    global _CACHED_MODEL, _CACHED_MODEL_TYPE

    if _CACHED_MODEL is not None:
        return _CACHED_MODEL, _CACHED_MODEL_TYPE

    # Check 1: Keras H5 model
    h5_path = current_app.config.get('DISEASE_MODEL_PATH', '')
    if h5_path and os.path.exists(h5_path):
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(h5_path)
            _CACHED_MODEL = model
            _CACHED_MODEL_TYPE = 'keras'
            current_app.logger.info(f"Loaded Keras CNN model from {h5_path}")
            return _CACHED_MODEL, _CACHED_MODEL_TYPE
        except Exception as e:
            current_app.logger.warning(f"Failed to load Keras model from {h5_path}: {e}")

    # Check 2: PyTorch .pth model
    pth_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'disease_detection', 'disease_model.pth')
    pth_path = os.path.abspath(pth_path)
    if os.path.exists(pth_path):
        try:
            import torch
            mapping_path = os.path.join(os.path.dirname(pth_path), 'class_indices.json')
            class_map = load_class_indices(mapping_path)
            num_classes = len(class_map) if class_map else len(MODEL_CLASSES)

            model = build_pytorch_cnn(num_classes=num_classes)
            model.load_state_dict(torch.load(pth_path, map_location='cpu'))
            model.eval()
            _CACHED_MODEL = model
            _CACHED_MODEL_TYPE = 'pytorch'
            current_app.logger.info(f"Loaded PyTorch CNN model from {pth_path}")
            return _CACHED_MODEL, _CACHED_MODEL_TYPE
        except Exception as e:
            current_app.logger.warning(f"Failed to load PyTorch model from {pth_path}: {e}")

    # Check 3: OpenCV DNN ONNX model
    onnx_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'disease_detection', 'disease_model.onnx')
    onnx_path = os.path.abspath(onnx_path)
    if os.path.exists(onnx_path):
        try:
            net = cv2.dnn.readNetFromONNX(onnx_path)
            _CACHED_MODEL = net
            _CACHED_MODEL_TYPE = 'opencv_onnx'
            current_app.logger.info(f"Loaded OpenCV DNN model from {onnx_path}")
            return _CACHED_MODEL, _CACHED_MODEL_TYPE
        except Exception as e:
            current_app.logger.warning(f"Failed to load OpenCV ONNX model: {e}")

    return None, None


def run_model_inference(image_path):
    """
    Execute CNN prediction using the trained model.
    Returns prediction dictionary or raises RuntimeError if no model is trained.
    DOES NOT GENERATE RANDOM OR FAKE PREDICTIONS.
    """
    model, model_type = get_trained_model()
    if model is None:
        raise RuntimeError(
            "Trained CNN model is not available. Predictions require an authentic trained model. "
            "Please run: python ml/disease_detection/train.py"
        )

    # Load class mapping
    mapping_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'ml', 'disease_detection', 'class_indices.json'
    )
    class_map = load_class_indices(mapping_path)

    if model_type == 'keras':
        tensor, diagnostics = preprocess_image_cv2(image_path, target_size=(224, 224))
        raw_preds = model.predict(tensor)[0]
        class_idx = int(np.argmax(raw_preds))
        confidence = float(raw_preds[class_idx]) * 100.0

    elif model_type == 'pytorch':
        import torch
        tensor, diagnostics = preprocess_for_pytorch(image_path, target_size=(224, 224))
        torch_tensor = torch.from_numpy(tensor)
        with torch.no_grad():
            outputs = model(torch_tensor)
            probs = torch.softmax(outputs, dim=1)[0]
            class_idx = int(torch.argmax(probs).item())
            confidence = float(probs[class_idx].item()) * 100.0

    elif model_type == 'opencv_onnx':
        tensor, diagnostics = preprocess_image_cv2(image_path, target_size=(224, 224))
        # cv2.dnn expects NCHW format
        blob = np.transpose(tensor, (0, 3, 1, 2))
        model.setInput(blob)
        preds = model.forward()[0]
        # Softmax
        exp_preds = np.exp(preds - np.max(preds))
        probs = exp_preds / np.sum(exp_preds)
        class_idx = int(np.argmax(probs))
        confidence = float(probs[class_idx]) * 100.0

    else:
        raise ValueError(f"Unknown model type: {model_type}")

    # Map predicted index to class key
    class_key = class_map.get(class_idx, MODEL_CLASSES[class_idx % len(MODEL_CLASSES)])
    disease_info = get_disease_info(class_key)

    return {
        'class_key': class_key,
        'disease_name': disease_info['display_name'],
        'confidence': round(confidence, 1),
        'symptoms': disease_info['symptoms'],
        'precautions': disease_info['precautions'],
        'organic_control': disease_info.get('organic_control', ''),
        'chemical_control': disease_info.get('chemical_control', ''),
        'is_healthy': disease_info['is_healthy'],
        'diagnostics': diagnostics
    }


# ── Routes ───────────────────────────────────────────────────────────────────

@disease_bp.route('/disease-detection', methods=['GET', 'POST'])
@disease_bp.route('/disease-detection/detect', methods=['GET', 'POST'])
@login_required
def detect():
    """
    Primary leaf upload and disease diagnosis interface.
    Validates uploaded foliage, preprocesses with OpenCV, and runs CNN inference.
    """
    crops = Crop.query.filter_by(user_id=current_user.id).order_by(Crop.crop_name.asc()).all()

    # Determine Model Availability
    model, model_type = get_trained_model()
    model_status = {
        'available': model is not None,
        'type': model_type,
        'supported_classes_count': len(MODEL_CLASSES),
        'training_command': 'python ml/disease_detection/train.py --epochs 15'
    }

    if request.method == 'POST':
        if 'image' not in request.files:
            flash('Please upload an image file.', 'danger')
            return redirect(request.url)

        file = request.files['image']
        if not file or not file.filename:
            flash('No image file selected. Please select a valid foliage photo.', 'danger')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Allowed image formats: PNG, JPG, JPEG, GIF, BMP.', 'danger')
            return redirect(request.url)

        # Enforce tenancy isolation on optional linked crop
        crop_id = request.form.get('crop_id')
        linked_crop = None
        if crop_id:
            try:
                linked_crop = Crop.query.filter_by(id=int(crop_id), user_id=current_user.id).first()
            except (ValueError, TypeError):
                linked_crop = None

        # Save uploaded image to static/uploads/disease
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'disease')
        os.makedirs(upload_dir, exist_ok=True)
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        saved_path = os.path.join(upload_dir, filename)
        file.save(saved_path)

        # Check model availability before attempting inference
        if not model_status['available']:
            # STRICT POLICY: Do not generate random predictions
            flash(
                '⚠ Predictions require a trained CNN model. No trained weights file (disease_model.h5 / .pth) was found. '
                'Please run the training pipeline first: "python ml/disease_detection/train.py"',
                'warning'
            )
            return redirect(url_for('disease.detect'))

        # Run Real CNN Model Inference
        try:
            pred = run_model_inference(saved_path)

            # Store detection record in MySQL
            record = DiseaseDetection(
                user_id      = current_user.id,
                crop_id      = linked_crop.id if linked_crop else None,
                image_path   = f'uploads/disease/{filename}',
                disease_name = pred['disease_name'],
                confidence   = pred['confidence'],
                symptoms     = pred['symptoms'],
                precautions  = pred['precautions'],
                is_healthy   = pred['is_healthy']
            )
            db.session.add(record)

            # Update crop health status if linked
            if linked_crop:
                linked_crop.health_status = 'Healthy' if pred['is_healthy'] else 'Diseased'

            db.session.commit()

            status_str = "Healthy foliage confirmed" if pred['is_healthy'] else f"Pathogen detected: {pred['disease_name']}"
            flash(f"Diagnosis complete ({pred['confidence']}% confidence): {status_str}.", 'success')
            return redirect(url_for('disease.result', detection_id=record.id))

        except Exception as e:
            current_app.logger.error(f"Inference error during diagnostic scan: {e}")
            flash(f"Error during computer vision analysis: {str(e)}", 'danger')
            return redirect(request.url)

    # GET request: fetch recent scans for current farmer
    history = (DiseaseDetection.query
               .filter_by(user_id=current_user.id)
               .order_by(DiseaseDetection.detected_at.desc())
               .limit(10)
               .all())

    return render_template(
        'disease/detect.html',
        crops=crops,
        history=history,
        model_status=model_status,
        classes=MODEL_CLASSES
    )


@disease_bp.route('/disease-detection/result/<int:detection_id>')
@login_required
def result(detection_id):
    """
    Detailed agronomic diagnostic report with symptoms and precautions.
    Enforces multi-tenant data isolation: farmer can only view their own scan.
    """
    detection = DiseaseDetection.query.filter_by(
        id=detection_id, user_id=current_user.id
    ).first_or_404()

    # Look up treatment info from disease database
    info = get_disease_info(detection.disease_name)

    return render_template('disease/result.html', detection=detection, info=info)


@disease_bp.route('/disease-detection/history')
@login_required
def history():
    """
    Historical log of computer vision leaf diagnostic scans.
    Strictly isolated to current farmer's records.
    """
    detections = (DiseaseDetection.query
                  .filter_by(user_id=current_user.id)
                  .order_by(DiseaseDetection.detected_at.desc())
                  .all())

    return render_template('disease/history.html', detections=detections)


@disease_bp.route('/disease-detection/api/status')
@login_required
def api_status():
    """
    JSON API reporting model status, active framework, and supported classes.
    """
    model, model_type = get_trained_model()
    return jsonify({
        'model_available': model is not None,
        'model_type': model_type,
        'classes_count': len(MODEL_CLASSES),
        'supported_classes': MODEL_CLASSES,
        'training_command': 'python ml/disease_detection/train.py --epochs 15'
    })
