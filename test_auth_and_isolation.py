import unittest
from datetime import date
from app import create_app
from backend.models import db, User, Crop, DiseaseDetection, EnvironmentalData, YieldPrediction, Recommendation

class AuthAndIsolationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            # Clear test users if exist
            users_to_clean = User.query.filter(User.username.in_(['farmer_alice', 'farmer_bob', 'bad_user'])).all()
            for u in users_to_clean:
                db.session.delete(u)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            users_to_clean = User.query.filter(User.username.in_(['farmer_alice', 'farmer_bob', 'bad_user'])).all()
            for u in users_to_clean:
                db.session.delete(u)
            db.session.commit()

    def test_01_protected_routes_redirect_unauthenticated(self):
        """Ensure all protected routes redirect unauthenticated users to login."""
        protected_urls = [
            '/dashboard',
            '/dashboard/chart-data',
            '/crops',
            '/crops/add',
            '/crops/1',
            '/crops/1/edit',
            '/disease-detection/detect',
            '/disease-detection/history',
            '/environment',
            '/yield-prediction',
            '/yield-prediction/history',
            '/recommendations',
            '/reports',
            '/profile',
        ]
        for url in protected_urls:
            response = self.client.get(url, follow_redirects=False)
            self.assertEqual(response.status_code, 302, f"URL {url} should redirect")
            self.assertIn('/login', response.headers['Location'], f"URL {url} should redirect to login")

    def test_02_registration_validation(self):
        """Test validation rules for registration."""
        # 1. Short username
        res = self.client.post('/register', data={
            'username': 'ab',
            'email': 'valid@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Username must be between 3 and 30 characters', res.data)

        # 2. Invalid username characters
        res = self.client.post('/register', data={
            'username': 'john farmer!',
            'email': 'valid@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Username may only contain letters', res.data)

        # 3. Invalid email format
        res = self.client.post('/register', data={
            'username': 'farmer_alice',
            'email': 'not-an-email',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'valid email address', res.data)

        # 4. Password too short
        res = self.client.post('/register', data={
            'username': 'farmer_alice',
            'email': 'alice@example.com',
            'password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)
        self.assertIn(b'at least 6 characters', res.data)

        # 5. Password mismatch
        res = self.client.post('/register', data={
            'username': 'farmer_alice',
            'email': 'alice@example.com',
            'password': 'password123',
            'confirm_password': 'mismatch123'
        }, follow_redirects=True)
        self.assertIn(b'Passwords do not match', res.data)

        # 6. Negative farm size
        res = self.client.post('/register', data={
            'username': 'farmer_alice',
            'email': 'alice@example.com',
            'farm_size': '-5.0',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Farm acreage cannot be negative', res.data)

    def test_03_registration_success_and_duplicate_prevention(self):
        """Test successful registration and rejection of duplicates."""
        # Valid registration
        res = self.client.post('/register', data={
            'username': 'farmer_alice',
            'email': 'alice@farm.com',
            'full_name': 'Alice Farmer',
            'phone': '+1 555 123 4567',
            'location': 'Green Valley Sector 4',
            'farm_size': '25.5',
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123'
        }, follow_redirects=True)
        self.assertIn(b'Account created successfully', res.data)

        # Verify password is hashed in MySQL database
        with self.app.app_context():
            user = User.query.filter_by(username='farmer_alice').first()
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password_hash, 'SecurePassword@123')
            self.assertTrue(user.check_password('SecurePassword@123'))
            self.assertFalse(user.check_password('WrongPassword'))

        # Duplicate username attempt
        res = self.client.post('/register', data={
            'username': 'Farmer_Alice',  # case-insensitive check
            'email': 'different_alice@farm.com',
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123'
        }, follow_redirects=True)
        self.assertIn(b'already taken', res.data)

        # Duplicate email attempt
        res = self.client.post('/register', data={
            'username': 'alice_second',
            'email': 'ALICE@FARM.COM',  # case-insensitive check
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123'
        }, follow_redirects=True)
        self.assertIn(b'already registered', res.data)

    def test_04_login_and_logout(self):
        """Test login with username or email, session persistence, and logout."""
        # Register alice
        self.client.post('/register', data={
            'username': 'farmer_alice',
            'email': 'alice@farm.com',
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123'
        })

        # 1. Invalid password
        res = self.client.post('/login', data={
            'identifier': 'farmer_alice',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username/email or password', res.data)

        # 2. Valid login by username
        res = self.client.post('/login', data={
            'identifier': 'farmer_alice',
            'password': 'SecurePassword@123',
            'remember': 'on'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, farmer_alice', res.data)
        self.assertIn(b'Dashboard', res.data)

        # Verify access to protected dashboard
        res_dash = self.client.get('/dashboard')
        self.assertEqual(res_dash.status_code, 200)

        # Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out securely', res_logout.data)

        # Verify cannot access dashboard after logout
        res_after = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(res_after.status_code, 302)

        # 3. Valid login by email
        res_email = self.client.post('/login', data={
            'identifier': 'alice@farm.com',
            'password': 'SecurePassword@123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back', res_email.data)

    def test_05_farmer_data_isolation(self):
        """Verify each farmer can access ONLY their own crops and telemetry data."""
        # Create Farmer Alice and Farmer Bob
        self.client.post('/register', data={
            'username': 'farmer_alice',
            'email': 'alice@farm.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })
        self.client.post('/register', data={
            'username': 'farmer_bob',
            'email': 'bob@farm.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })

        with self.app.app_context():
            alice = User.query.filter_by(username='farmer_alice').first()
            bob = User.query.filter_by(username='farmer_bob').first()

            # Create Crop for Alice
            crop_alice = Crop(
                user_id=alice.id,
                crop_name="Alice's Golden Rice",
                crop_type='rice',
                planting_date=date(2024, 2, 1),
                field_area=5.0,
                location="Alice North Sector",
                growth_stage="Tillering",
                health_status="Healthy"
            )
            # Create Crop for Bob
            crop_bob = Crop(
                user_id=bob.id,
                crop_name="Bob's Sweet Corn",
                crop_type='corn',
                planting_date=date(2024, 3, 1),
                field_area=10.0,
                location="Bob South Sector",
                growth_stage="Vegetative",
                health_status="Healthy"
            )
            db.session.add_all([crop_alice, crop_bob])
            db.session.commit()
            alice_crop_id = crop_alice.id
            bob_crop_id = crop_bob.id

        # Log in as Alice
        self.client.post('/login', data={'identifier': 'farmer_alice', 'password': 'Password123'})

        # 1. Alice views crop list -> Sees Alice's crop, does NOT see Bob's crop
        res_list = self.client.get('/crops')
        self.assertIn(b"Alice&#39;s Golden Rice", res_list.data)
        self.assertNotIn(b"Bob&#39;s Sweet Corn", res_list.data)

        # 2. Alice views Alice's crop detail -> 200 OK
        res_detail = self.client.get(f'/crops/{alice_crop_id}')
        self.assertEqual(res_detail.status_code, 200)

        # 3. Alice attempts to view Bob's crop detail -> 404 Not Found
        res_bob_detail = self.client.get(f'/crops/{bob_crop_id}')
        self.assertEqual(res_bob_detail.status_code, 404, "Alice should not be able to view Bob's crop")

        # 4. Alice attempts to edit Bob's crop -> 404 Not Found
        res_bob_edit = self.client.get(f'/crops/{bob_crop_id}/edit')
        self.assertEqual(res_bob_edit.status_code, 404, "Alice should not be able to edit Bob's crop")

        # 5. Alice attempts to delete Bob's crop -> 404 Not Found
        res_bob_del = self.client.post(f'/crops/{bob_crop_id}/delete')
        self.assertEqual(res_bob_del.status_code, 404, "Alice should not be able to delete Bob's crop")

        # Verify Bob's crop is still intact in database
        with self.app.app_context():
            intact_crop = Crop.query.get(bob_crop_id)
            self.assertIsNotNone(intact_crop)

        # 6. Alice attempts to get Bob's growth data -> 404
        res_growth = self.client.get(f'/crops/{bob_crop_id}/growth-data')
        self.assertEqual(res_growth.status_code, 404, "Alice should not access Bob's growth data")

        # Log out Alice and log in as Bob
        self.client.get('/logout')
        self.client.post('/login', data={'identifier': 'farmer_bob', 'password': 'Password123'})

        # Bob views crop list -> Sees Bob's crop, does NOT see Alice's crop
        res_bob_list = self.client.get('/crops')
        self.assertIn(b"Bob&#39;s Sweet Corn", res_bob_list.data)
        self.assertNotIn(b"Alice&#39;s Golden Rice", res_bob_list.data)

        # Bob attempts to view Alice's crop -> 404
        res_alice_by_bob = self.client.get(f'/crops/{alice_crop_id}')
        self.assertEqual(res_alice_by_bob.status_code, 404)

if __name__ == '__main__':
    unittest.main()

