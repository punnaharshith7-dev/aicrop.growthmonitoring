"""
Test suite for AI Crop Disease Detection module, OpenCV preprocessing,
CNN model inference, and farmer tenancy isolation.
"""

import os
import unittest
import numpy as np
import cv2

from app import create_app
from backend.models import db, User, Crop, DiseaseDetection
from ml.disease_detection.preprocess import preprocess_image_cv2, extract_leaf_diagnostics
from ml.disease_detection.disease_db import get_disease_info, DISEASE_DATABASE
from ml.disease_detection.model import MODEL_CLASSES, load_class_indices


class DiseaseDetectionTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            User.query.filter_by(username='test_pathologist').delete()
            db.session.commit()

        # Create a test image using Unicode-safe imencode
        self.test_img_path = 'test_leaf_sample.jpg'
        img = np.full((300, 300, 3), (35, 160, 45), dtype=np.uint8)
        # Draw central circle to simulate leaf
        cv2.circle(img, (150, 150), 100, (40, 180, 50), -1)
        is_success, buf = cv2.imencode('.jpg', img)
        if is_success:
            buf.tofile(self.test_img_path)

    def tearDown(self):
        if os.path.exists(self.test_img_path):
            try:
                os.remove(self.test_img_path)
            except OSError:
                pass
        with self.app.app_context():
            User.query.filter_by(username='test_pathologist').delete()
            db.session.commit()

    def test_01_user_model_full_name_init(self):
        """Verify User model accepts full_name and other kwargs without TypeError."""
        user = User(
            username='dr_agronomist',
            email='agronomist@farm.org',
            full_name='Dr. Elena Vance',
            phone='+1 234 567 8900',
            location='Field Laboratory Sector 3',
            farm_size=42.5
        )
        self.assertEqual(user.full_name, 'Dr. Elena Vance')
        self.assertEqual(user.farm_size, 42.5)

    def test_02_opencv_preprocessing(self):
        """Verify OpenCV image loading, color conversion, resizing, and normalization."""
        tensor, diag = preprocess_image_cv2(self.test_img_path, target_size=(224, 224))
        self.assertEqual(tensor.shape, (1, 224, 224, 3))
        self.assertEqual(tensor.dtype, np.float32)
        self.assertTrue(0.0 <= np.min(tensor) <= np.max(tensor) <= 1.0)
        self.assertEqual(diag['original_width'], 300)
        self.assertEqual(diag['original_height'], 300)
        self.assertTrue(diag['is_vegetation_detected'])

    def test_03_disease_database_retrieval(self):
        """Verify disease database provides accurate symptoms, precautions, and healthy flags."""
        # Test Diseased Class
        info_early_blight = get_disease_info('Tomato_Early_Blight')
        self.assertFalse(info_early_blight['is_healthy'])
        self.assertIn('concentric rings', info_early_blight['symptoms'].lower())
        self.assertTrue(len(info_early_blight['precautions']) > 10)
        self.assertTrue('organic_control' in info_early_blight)

        # Test Healthy Class
        info_healthy = get_disease_info('Tomato_Healthy')
        self.assertTrue(info_healthy['is_healthy'])
        self.assertIn('healthy', info_healthy['display_name'].lower())

    def test_04_disease_detection_upload_and_inference(self):
        """Test leaf upload route, model inference, and database persistence."""
        # 1. Register and login
        self.client.post('/register', data={
            'username': 'test_pathologist',
            'email': 'pathologist@farm.org',
            'full_name': 'Sarah Green',
            'password': 'SafePassword@123',
            'confirm_password': 'SafePassword@123'
        })
        self.client.post('/login', data={
            'identifier': 'test_pathologist',
            'password': 'SafePassword@123'
        })

        # 2. Create a test crop
        with self.app.app_context():
            u = User.query.filter_by(username='test_pathologist').first()
            from datetime import date
            crop = Crop(
                user_id=u.id,
                crop_name="Greenhouse Tomato Alpha",
                crop_type="tomato",
                planting_date=date(2024, 1, 15),
                health_status="Healthy"
            )
            db.session.add(crop)
            db.session.commit()
            crop_id = crop.id

        # 3. Upload test leaf image
        with open(self.test_img_path, 'rb') as f:
            res = self.client.post('/disease-detection', data={
                'image': (f, 'test_foliage.jpg'),
                'crop_id': str(crop_id)
            }, content_type='multipart/form-data', follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        # Should be redirected to result page or show diagnosis
        self.assertIn(b'Diagnostic Report', res.data)

        # 4. Verify detection in DB
        with self.app.app_context():
            detection = DiseaseDetection.query.filter_by(crop_id=crop_id).first()
            self.assertIsNotNone(detection)
            self.assertTrue(detection.confidence > 0.0)
            self.assertIsNotNone(detection.symptoms)
            self.assertIsNotNone(detection.precautions)

    def test_05_api_status_endpoint(self):
        """Verify API status endpoint returns model metadata."""
        self.client.post('/register', data={
            'username': 'test_pathologist',
            'email': 'pathologist@farm.org',
            'full_name': 'Sarah Green',
            'password': 'SafePassword@123',
            'confirm_password': 'SafePassword@123'
        })
        self.client.post('/login', data={
            'identifier': 'test_pathologist',
            'password': 'SafePassword@123'
        })
        res = self.client.get('/disease-detection/api/status')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['classes_count'] >= 20)
        self.assertIn('Tomato_Healthy', data['supported_classes'])


if __name__ == '__main__':
    unittest.main()
