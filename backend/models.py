from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# ──────────────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False, index=True)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name     = db.Column(db.String(120))
    phone         = db.Column(db.String(20))
    location      = db.Column(db.String(150))
    farm_size     = db.Column(db.Float)
    profile_image = db.Column(db.String(200))
    reset_token   = db.Column(db.String(200))
    reset_expiry  = db.Column(db.DateTime)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Scoped relationships ensuring each farmer owns their data
    crops              = db.relationship('Crop',              backref='farmer', lazy=True, cascade='all, delete-orphan')
    disease_detections = db.relationship('DiseaseDetection',  backref='farmer', lazy=True, cascade='all, delete-orphan')
    environmental_data = db.relationship('EnvironmentalData', backref='farmer', lazy=True, cascade='all, delete-orphan')
    yield_predictions  = db.relationship('YieldPrediction',   backref='farmer', lazy=True, cascade='all, delete-orphan')
    recommendations    = db.relationship('Recommendation',    backref='farmer', lazy=True, cascade='all, delete-orphan')

    def __init__(self, username=None, email=None, password=None, password_hash=None,
                 full_name=None, phone=None, location=None, farm_size=None,
                 profile_image=None, reset_token=None, reset_expiry=None, **kwargs):
        super().__init__(**kwargs)
        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
        if full_name is not None:
            self.full_name = full_name
        if phone is not None:
            self.phone = phone
        if location is not None:
            self.location = location
        if farm_size is not None:
            self.farm_size = farm_size
        if profile_image is not None:
            self.profile_image = profile_image
        if reset_token is not None:
            self.reset_token = reset_token
        if reset_expiry is not None:
            self.reset_expiry = reset_expiry
        if password is not None:
            self.set_password(password)
        elif password_hash is not None:
            self.password_hash = password_hash

    def set_password(self, password):
        """Securely hash password using modern salted PBKDF2."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verify candidate password against stored hash."""
        if not self.password_hash or not password:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# ──────────────────────────────────────────────────────────────────────────────
class Crop(db.Model):
    __tablename__ = 'crops'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    crop_name     = db.Column(db.String(100), nullable=False)
    crop_type     = db.Column(db.String(100))
    crop_variety  = db.Column(db.String(100))
    planting_date = db.Column(db.Date, nullable=False)
    field_area    = db.Column(db.Float)
    location      = db.Column(db.String(150))
    growth_stage  = db.Column(db.String(100))
    health_status = db.Column(db.String(50), default='Healthy')
    notes         = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    disease_detections = db.relationship('DiseaseDetection', backref='crop', lazy=True)
    environmental_data = db.relationship('EnvironmentalData', backref='crop', lazy=True)

    def __init__(self, user_id=None, crop_name=None, crop_type=None, crop_variety=None,
                 planting_date=None, field_area=None, location=None, growth_stage=None,
                 health_status='Healthy', notes=None, **kwargs):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if crop_name is not None:
            self.crop_name = crop_name
        if crop_type is not None:
            self.crop_type = crop_type
        if crop_variety is not None:
            self.crop_variety = crop_variety
        if planting_date is not None:
            self.planting_date = planting_date
        if field_area is not None:
            self.field_area = field_area
        if location is not None:
            self.location = location
        if growth_stage is not None:
            self.growth_stage = growth_stage
        if health_status is not None:
            self.health_status = health_status
        if notes is not None:
            self.notes = notes

    def __repr__(self):
        return f'<Crop {self.crop_name}>'


# ──────────────────────────────────────────────────────────────────────────────
class DiseaseDetection(db.Model):
    __tablename__ = 'disease_detections'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    crop_id      = db.Column(db.Integer, db.ForeignKey('crops.id', ondelete='SET NULL'), nullable=True)
    image_path   = db.Column(db.String(300))
    disease_name = db.Column(db.String(150))
    confidence   = db.Column(db.Float)
    symptoms     = db.Column(db.Text)
    precautions  = db.Column(db.Text)
    is_healthy   = db.Column(db.Boolean, default=False)
    detected_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id=None, crop_id=None, image_path=None, disease_name=None,
                 confidence=None, symptoms=None, precautions=None, is_healthy=False,
                 detected_at=None, **kwargs):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if crop_id is not None:
            self.crop_id = crop_id
        if image_path is not None:
            self.image_path = image_path
        if disease_name is not None:
            self.disease_name = disease_name
        if confidence is not None:
            self.confidence = confidence
        if symptoms is not None:
            self.symptoms = symptoms
        if precautions is not None:
            self.precautions = precautions
        if is_healthy is not None:
            self.is_healthy = is_healthy
        if detected_at is not None:
            self.detected_at = detected_at


# ──────────────────────────────────────────────────────────────────────────────
class EnvironmentalData(db.Model):
    __tablename__ = 'environmental_data'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    crop_id       = db.Column(db.Integer, db.ForeignKey('crops.id', ondelete='SET NULL'), nullable=True)
    temperature   = db.Column(db.Float)
    humidity      = db.Column(db.Float)
    rainfall      = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)
    reading_date  = db.Column(db.DateTime, default=datetime.utcnow)
    notes         = db.Column(db.String(300))

    def __init__(self, user_id=None, crop_id=None, temperature=None, humidity=None,
                 rainfall=None, soil_moisture=None, reading_date=None, notes=None, **kwargs):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if crop_id is not None:
            self.crop_id = crop_id
        if temperature is not None:
            self.temperature = temperature
        if humidity is not None:
            self.humidity = humidity
        if rainfall is not None:
            self.rainfall = rainfall
        if soil_moisture is not None:
            self.soil_moisture = soil_moisture
        if reading_date is not None:
            self.reading_date = reading_date
        if notes is not None:
            self.notes = notes


# ──────────────────────────────────────────────────────────────────────────────
class YieldPrediction(db.Model):
    __tablename__ = 'yield_predictions'

    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    crop_type         = db.Column(db.String(100))
    area              = db.Column(db.Float)
    rainfall          = db.Column(db.Float)
    temperature       = db.Column(db.Float)
    soil_type         = db.Column(db.String(100))
    fertilizer        = db.Column(db.String(100))
    fertilizer_amount = db.Column(db.Float)
    predicted_yield   = db.Column(db.Float)
    yield_unit        = db.Column(db.String(50), default='tonnes/hectare')
    predicted_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id=None, crop_type=None, area=None, rainfall=None,
                 temperature=None, soil_type=None, fertilizer=None,
                 fertilizer_amount=None, predicted_yield=None, yield_unit='tonnes/hectare',
                 predicted_at=None, **kwargs):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if crop_type is not None:
            self.crop_type = crop_type
        if area is not None:
            self.area = area
        if rainfall is not None:
            self.rainfall = rainfall
        if temperature is not None:
            self.temperature = temperature
        if soil_type is not None:
            self.soil_type = soil_type
        if fertilizer is not None:
            self.fertilizer = fertilizer
        if fertilizer_amount is not None:
            self.fertilizer_amount = fertilizer_amount
        if predicted_yield is not None:
            self.predicted_yield = predicted_yield
        if yield_unit is not None:
            self.yield_unit = yield_unit
        if predicted_at is not None:
            self.predicted_at = predicted_at


# ──────────────────────────────────────────────────────────────────────────────
class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    crop_id        = db.Column(db.Integer, db.ForeignKey('crops.id', ondelete='SET NULL'), nullable=True)
    rec_type       = db.Column(db.String(100))
    recommendation = db.Column(db.Text)
    priority       = db.Column(db.String(20), default='Normal')
    is_read        = db.Column(db.Boolean, default=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id=None, crop_id=None, rec_type=None,
                 recommendation=None, priority='Normal', is_read=False,
                 created_at=None, **kwargs):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if crop_id is not None:
            self.crop_id = crop_id
        if rec_type is not None:
            self.rec_type = rec_type
        if recommendation is not None:
            self.recommendation = recommendation
        if priority is not None:
            self.priority = priority
        if is_read is not None:
            self.is_read = is_read
        if created_at is not None:
            self.created_at = created_at
