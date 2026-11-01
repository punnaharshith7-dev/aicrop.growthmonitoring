"""
Test suite for Crop Growth Monitoring module, configurable agronomic profiles,
biological 6-stage progression tracking, and harvest date estimation.
"""

import unittest
from datetime import date, timedelta
from app import create_app
from backend.models import db, User, Crop
from backend.crop_config import (
    CROP_PROFILES, GROWTH_STAGES, STAGE_METADATA,
    calculate_crop_growth, get_crop_profile
)


class CropGrowthMonitoringTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            User.query.filter_by(username='farmer_charlie').delete()
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            User.query.filter_by(username='farmer_charlie').delete()
            db.session.commit()

    def test_01_crop_growth_calculation_engine(self):
        """Test calculation of elapsed days, progress percentage, and expected harvest date."""
        today = date.today()
        # Planted 30 days ago
        planted = today - timedelta(days=30)

        # Test Tomato: 90 days total cycle
        growth = calculate_crop_growth('tomato', planted, 'Roma VF')
        self.assertEqual(growth['elapsed_days'], 30)
        self.assertEqual(growth['total_days'], 90)
        self.assertAlmostEqual(growth['progress'], 33.3, places=1)
        self.assertEqual(growth['harvest_date'], planted + timedelta(days=90))
        self.assertEqual(growth['days_remaining'], 60)
        self.assertFalse(growth['is_harvest_ready'])

        # Verify 6 standard stages are present
        stage_names = [s['name'] for s in growth['stages']]
        self.assertEqual(stage_names, GROWTH_STAGES)

        # At Day 30 for Tomato (Germination 8d, Seedling 16d = 24d), it should be in Vegetative stage
        self.assertEqual(growth['current_stage'], 'Vegetative')

    def test_02_stages_milestone_progression(self):
        """Verify completed, current, and upcoming statuses across the 6 stages."""
        today = date.today()
        # Rice: 120 days total. Germination: 10d, Seedling: 15d, Vegetative: 30d, Flowering: 25d, Fruiting: 25d, Harvesting: 15d
        # Planted 70 days ago -> In Flowering stage (10 + 15 + 30 = 55 to 80)
        planted = today - timedelta(days=70)
        growth = calculate_crop_growth('rice', planted, 'Basmati 370')

        self.assertEqual(growth['current_stage'], 'Flowering')
        stages = growth['stages']
        self.assertEqual(stages[0]['status'], 'completed')  # Germination
        self.assertEqual(stages[1]['status'], 'completed')  # Seedling
        self.assertEqual(stages[2]['status'], 'completed')  # Vegetative
        self.assertEqual(stages[3]['status'], 'current')    # Flowering
        self.assertEqual(stages[4]['status'], 'upcoming')   # Fruiting
        self.assertEqual(stages[5]['status'], 'upcoming')   # Harvesting

        # Test physiological maturity reached (> 120 days)
        planted_old = today - timedelta(days=130)
        growth_mature = calculate_crop_growth('rice', planted_old)
        self.assertEqual(growth_mature['progress'], 100.0)
        self.assertEqual(growth_mature['current_stage'], 'Harvesting')
        self.assertTrue(growth_mature['is_harvest_ready'])
        self.assertEqual(growth_mature['days_remaining'], 0)

    def test_03_add_crop_with_variety_and_area(self):
        """Test adding a crop with name, planting date, land area, and crop variety."""
        # 1. Register & login farmer
        self.client.post('/register', data={
            'username': 'farmer_charlie',
            'email': 'charlie@farm.org',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        })
        self.client.post('/login', data={
            'identifier': 'farmer_charlie',
            'password': 'Password@123'
        })

        # 2. Add crop field
        res = self.client.post('/crops/add', data={
            'crop_name': 'Valley Gold Wheat Sector 2',
            'crop_type': 'wheat',
            'crop_variety': 'Sharbati Gold',
            'planting_date': str(date.today() - timedelta(days=15)),
            'field_area': '12.5',
            'location': 'Northern Plateau Sector 2',
            'notes': 'Loamy soil with drip irrigation installed'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Valley Gold Wheat Sector 2', res.data)
        self.assertIn(b'Sharbati Gold', res.data)

        # 3. Verify in database
        with self.app.app_context():
            u = User.query.filter_by(username='farmer_charlie').first()
            crop = Crop.query.filter_by(user_id=u.id, crop_name='Valley Gold Wheat Sector 2').first()
            self.assertIsNotNone(crop)
            self.assertEqual(crop.crop_type, 'wheat')
            self.assertEqual(crop.crop_variety, 'Sharbati Gold')
            self.assertEqual(crop.field_area, 12.5)
            self.assertEqual(crop.growth_stage, 'Seedling')

    def test_04_crop_detail_and_charts_api(self):
        """Test detail page and growth-data telemetry API endpoint."""
        # Login
        self.client.post('/register', data={
            'username': 'farmer_charlie',
            'email': 'charlie@farm.org',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        })
        self.client.post('/login', data={
            'identifier': 'farmer_charlie',
            'password': 'Password@123'
        })

        with self.app.app_context():
            u = User.query.filter_by(username='farmer_charlie').first()
            crop = Crop(
                user_id=u.id,
                crop_name='Test Corn Field',
                crop_type='corn',
                crop_variety='Golden Bantam',
                planting_date=date.today() - timedelta(days=40),
                field_area=5.0
            )
            db.session.add(crop)
            db.session.commit()
            crop_id = crop.id

        # 1. Detail page request
        res_detail = self.client.get(f'/crops/{crop_id}')
        self.assertEqual(res_detail.status_code, 200)
        self.assertIn(b'Test Corn Field', res_detail.data)
        self.assertIn(b'Golden Bantam', res_detail.data)
        self.assertIn(b'Growth Progress', res_detail.data)

        # 2. Growth telemetry JSON API request
        res_api = self.client.get(f'/crops/{crop_id}/growth-data')
        self.assertEqual(res_api.status_code, 200)
        data = res_api.get_json()
        self.assertEqual(data['crop_name'], 'Test Corn Field')
        self.assertEqual(data['crop_variety'], 'Golden Bantam')
        self.assertEqual(len(data['stages']), 6)
        self.assertTrue('chart' in data)
        self.assertTrue('expected_curve' in data['chart'])

    def test_05_edit_crop_variety_and_stage(self):
        """Test editing crop variety, land area, and confirmed growth stage."""
        self.client.post('/register', data={
            'username': 'farmer_charlie',
            'email': 'charlie@farm.org',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        })
        self.client.post('/login', data={
            'identifier': 'farmer_charlie',
            'password': 'Password@123'
        })

        with self.app.app_context():
            u = User.query.filter_by(username='farmer_charlie').first()
            crop = Crop(
                user_id=u.id,
                crop_name='Initial Crop',
                crop_type='tomato',
                crop_variety='Roma VF',
                planting_date=date.today() - timedelta(days=10),
                field_area=2.0
            )
            db.session.add(crop)
            db.session.commit()
            crop_id = crop.id

        # Edit crop
        res = self.client.post(f'/crops/{crop_id}/edit', data={
            'crop_name': 'Updated Heirloom Tomato',
            'crop_type': 'tomato',
            'crop_variety': 'San Marzano',
            'field_area': '3.25',
            'growth_stage': 'Vegetative',
            'health_status': 'Healthy'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        with self.app.app_context():
            updated = Crop.query.get(crop_id)
            self.assertEqual(updated.crop_name, 'Updated Heirloom Tomato')
            self.assertEqual(updated.crop_variety, 'San Marzano')
            self.assertEqual(updated.field_area, 3.25)
            self.assertEqual(updated.growth_stage, 'Vegetative')


if __name__ == '__main__':
    unittest.main()

