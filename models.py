from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Define user roles as constants
ROLE_DONOR = 'donor'
ROLE_BENEFICIARY = 'beneficiary'
ROLE_VOLUNTEER = 'volunteer'
ROLE_PARTNER = 'partner'
ROLE_ADMIN = 'admin'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(256))
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    zip_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    donations = db.relationship('Donation', backref='donor', lazy='dynamic')
    requests = db.relationship('FoodRequest', backref='beneficiary', lazy='dynamic')
    volunteer_slots = db.relationship('VolunteerSlot', backref='volunteer', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}, Role: {self.role}>'

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20), default='items')
    expiry_date = db.Column(db.Date, nullable=True)
    location = db.Column(db.String(128))
    nutritional_info = db.Column(db.Text)
    allergens = db.Column(db.String(256))
    barcode = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    donation_id = db.Column(db.Integer, db.ForeignKey('donation.id'), nullable=True)
    distribution_id = db.Column(db.Integer, db.ForeignKey('distribution.id'), nullable=True)
    
    def __repr__(self):
        return f'<FoodItem {self.name}, Qty: {self.quantity} {self.unit}>'

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    donation_type = db.Column(db.String(20), nullable=False)  # food, money, other
    status = db.Column(db.String(20), default='pending')  # pending, approved, received, declined
    amount = db.Column(db.Float, nullable=True)  # for monetary donations
    pickup_date = db.Column(db.DateTime, nullable=True)
    pickup_address = db.Column(db.String(256), nullable=True)
    notes = db.Column(db.Text)
    tax_receipt_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('FoodItem', backref='donation', lazy='dynamic')
    
    def __repr__(self):
        return f'<Donation from User {self.donor_id}, Type: {self.donation_type}, Status: {self.status}>'

class FoodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, fulfilled, declined
    request_items = db.Column(db.Text, nullable=False)  # JSON string of requested items and quantities
    household_size = db.Column(db.Integer, nullable=False)
    emergency = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    appointment_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FoodRequest from User {self.beneficiary_id}, Status: {self.status}>'

class FoodBank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(256))
    hours = db.Column(db.Text)  # JSON string of operating hours
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    services = db.Column(db.Text)  # JSON string of services offered
    requirements = db.Column(db.Text)  # Requirements for beneficiaries
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    distributions = db.relationship('Distribution', backref='food_bank', lazy='dynamic')
    volunteer_slots = db.relationship('VolunteerSlot', backref='food_bank', lazy='dynamic')
    
    def __repr__(self):
        return f'<FoodBank {self.name}, {self.city}, {self.state}>'

class Distribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_bank_id = db.Column(db.Integer, db.ForeignKey('food_bank.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    distribution_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(256))
    status = db.Column(db.String(20), default='planned')  # planned, in-progress, completed, cancelled
    capacity = db.Column(db.Integer)
    current_reservations = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('FoodItem', backref='distribution', lazy='dynamic')
    
    def __repr__(self):
        return f'<Distribution {self.name}, Date: {self.distribution_date}>'

class VolunteerSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_bank_id = db.Column(db.Integer, db.ForeignKey('food_bank.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    role = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, filled, completed, cancelled
    hours_logged = db.Column(db.Float, default=0)
    verified = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<VolunteerSlot {self.role}, Date: {self.date}, Status: {self.status}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(256))
    event_type = db.Column(db.String(64))  # fundraiser, food drive, community outreach, etc.
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='upcoming')  # upcoming, in-progress, completed, cancelled
    max_participants = db.Column(db.Integer)
    registration_required = db.Column(db.Boolean, default=False)
    registration_link = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organizer = db.relationship('User', backref='organized_events')
    
    def __repr__(self):
        return f'<Event {self.title}, Date: {self.event_date}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(128))
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    
    def __repr__(self):
        return f'<Message from {self.sender_id} to {self.recipient_id}, Subject: {self.subject}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20))  # info, success, warning, error
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification for {self.user_id}, Type: {self.notification_type}>'
