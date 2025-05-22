from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms import IntegerField, DateField, DateTimeField, FloatField, TimeField, HiddenField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from models import User, ROLE_DONOR, ROLE_BENEFICIARY, ROLE_VOLUNTEER, ROLE_PARTNER, ROLE_ADMIN

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        (ROLE_DONOR, 'Donor'),
        (ROLE_BENEFICIARY, 'Beneficiary'),
        (ROLE_VOLUNTEER, 'Volunteer'),
        (ROLE_PARTNER, 'Partner Organization')
    ])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('ZIP Code', validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('ZIP Code', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class FoodItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('canned', 'Canned Goods'),
        ('dry', 'Dry Goods'),
        ('produce', 'Fresh Produce'),
        ('dairy', 'Dairy'),
        ('protein', 'Protein'),
        ('beverages', 'Beverages'),
        ('snacks', 'Snacks'),
        ('hygiene', 'Hygiene Products'),
        ('other', 'Other')
    ])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    unit = SelectField('Unit', choices=[
        ('items', 'Items'),
        ('lbs', 'Pounds'),
        ('kg', 'Kilograms'),
        ('boxes', 'Boxes'),
        ('cases', 'Cases')
    ])
    expiry_date = DateField('Expiration Date', validators=[Optional()])
    location = StringField('Storage Location')
    nutritional_info = TextAreaField('Nutritional Information')
    allergens = StringField('Allergens')
    barcode = StringField('Barcode')
    submit = SubmitField('Save Item')

class DonationForm(FlaskForm):
    donation_type = SelectField('Donation Type', choices=[
        ('food', 'Food Donation'),
        ('money', 'Monetary Donation'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    amount = FloatField('Amount ($)', validators=[Optional()])
    pickup_date = DateTimeField('Pickup Date and Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    pickup_address = StringField('Pickup Address')
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit Donation')

class FoodRequestForm(FlaskForm):
    household_size = IntegerField('Household Size', validators=[DataRequired(), NumberRange(min=1)])
    request_items = TextAreaField('Requested Items', validators=[DataRequired()])
    emergency = BooleanField('This is an emergency request')
    notes = TextAreaField('Additional Notes')
    appointment_date = DateTimeField('Preferred Pickup Date/Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Submit Request')

class VolunteerSlotForm(FlaskForm):
    food_bank_id = SelectField('Food Bank', coerce=int, validators=[DataRequired()])
    role = SelectField('Volunteer Role', choices=[
        ('sorter', 'Food Sorter'),
        ('packer', 'Food Packer'),
        ('driver', 'Delivery Driver'),
        ('greeter', 'Greeter'),
        ('cleaner', 'Cleaner'),
        ('admin', 'Administrative Help'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Sign Up')

class LogHoursForm(FlaskForm):
    slot_id = HiddenField('Slot ID', validators=[DataRequired()])
    hours_logged = FloatField('Hours Worked', validators=[DataRequired(), NumberRange(min=0.5)])
    notes = TextAreaField('Notes')
    submit = SubmitField('Log Hours')

class DistributionForm(FlaskForm):
    food_bank_id = SelectField('Food Bank', coerce=int, validators=[DataRequired()])
    name = StringField('Distribution Name', validators=[DataRequired()])
    distribution_date = DateTimeField('Distribution Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1)])
    notes = TextAreaField('Notes')
    submit = SubmitField('Create Distribution')

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    event_date = DateTimeField('Event Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    event_type = SelectField('Event Type', choices=[
        ('fundraiser', 'Fundraiser'),
        ('food_drive', 'Food Drive'),
        ('community', 'Community Outreach'),
        ('volunteer', 'Volunteer Appreciation'),
        ('workshop', 'Workshop/Training'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    max_participants = IntegerField('Maximum Participants', validators=[Optional(), NumberRange(min=1)])
    registration_required = BooleanField('Registration Required')
    registration_link = StringField('Registration Link', validators=[Optional()])
    submit = SubmitField('Create Event')

class MessageForm(FlaskForm):
    recipient_id = SelectField('Recipient', coerce=int, validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class FoodBankForm(FlaskForm):
    name = StringField('Food Bank Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('ZIP Code', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    website = StringField('Website', validators=[Optional()])
    hours = TextAreaField('Operating Hours', validators=[DataRequired()])
    services = TextAreaField('Services Offered', validators=[DataRequired()])
    requirements = TextAreaField('Requirements for Beneficiaries', validators=[Optional()])
    latitude = FloatField('Latitude', validators=[Optional()])
    longitude = FloatField('Longitude', validators=[Optional()])
    submit = SubmitField('Save Food Bank')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
