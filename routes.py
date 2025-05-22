from flask import render_template, redirect, url_for, flash, request, jsonify, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import app, db
from models import (User, FoodItem, Donation, FoodRequest, FoodBank, Distribution, 
                   VolunteerSlot, Event, Message, Notification, 
                   ROLE_DONOR, ROLE_BENEFICIARY, ROLE_VOLUNTEER, ROLE_PARTNER, ROLE_ADMIN)
from forms import (LoginForm, RegistrationForm, ProfileForm, PasswordChangeForm, FoodItemForm,
                  DonationForm, FoodRequestForm, VolunteerSlotForm, LogHoursForm, 
                  DistributionForm, EventForm, MessageForm, FoodBankForm, SearchForm)
from datetime import datetime
import json

# Utility function to check role
def check_role(required_roles):
    if not current_user.is_authenticated:
        return False
    if isinstance(required_roles, str):
        return current_user.role == required_roles
    return current_user.role in required_roles

# Home page
@app.route('/')
def index():
    return render_template('index.html', title='Food Bank Management System')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard')
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                   email=form.email.data,
                   role=form.role.data,
                   first_name=form.first_name.data,
                   last_name=form.last_name.data,
                   phone=form.phone.data,
                   address=form.address.data,
                   city=form.city.data,
                   state=form.state.data,
                   zip_code=form.zip_code.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Create welcome notification
        notification = Notification(
            user_id=user.id,
            title="Welcome to the Food Bank Management System",
            content=f"Thank you for registering as a {user.role}. We're glad to have you with us!",
            notification_type="info"
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Congratulations, you are now registered! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # Common data for all users
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).limit(5).all()
    messages = Message.query.filter_by(recipient_id=current_user.id, read=False).limit(5).all()
    
    # Role-specific data
    data = {}
    
    if current_user.role == ROLE_DONOR:
        data['recent_donations'] = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).limit(5).all()
        data['donation_count'] = Donation.query.filter_by(donor_id=current_user.id).count()
        
    elif current_user.role == ROLE_BENEFICIARY:
        data['recent_requests'] = FoodRequest.query.filter_by(beneficiary_id=current_user.id).order_by(FoodRequest.created_at.desc()).limit(5).all()
        data['pending_requests'] = FoodRequest.query.filter_by(beneficiary_id=current_user.id, status='pending').count()
        
    elif current_user.role == ROLE_VOLUNTEER:
        data['upcoming_slots'] = VolunteerSlot.query.filter_by(volunteer_id=current_user.id, status='filled').order_by(VolunteerSlot.date.asc()).limit(5).all()
        data['hours_logged'] = db.session.query(db.func.sum(VolunteerSlot.hours_logged)).filter_by(volunteer_id=current_user.id, verified=True).scalar() or 0
        
    elif current_user.role == ROLE_PARTNER:
        data['recent_donations'] = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).limit(5).all()
        
    elif current_user.role == ROLE_ADMIN:
        data['pending_donations'] = Donation.query.filter_by(status='pending').count()
        data['pending_requests'] = FoodRequest.query.filter_by(status='pending').count()
        data['low_inventory'] = FoodItem.query.filter(FoodItem.quantity < 10).count()
        data['open_volunteer_slots'] = VolunteerSlot.query.filter_by(status='open').count()
    
    # Common data for all users
    data['upcoming_events'] = Event.query.filter(Event.event_date > datetime.utcnow()).order_by(Event.event_date.asc()).limit(3).all()
    
    return render_template('dashboard.html', title='Dashboard', notifications=notifications, messages=messages, data=data)

# Profile management
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.zip_code = form.zip_code.data
        
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone.data = current_user.phone
        form.address.data = current_user.address
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.zip_code.data = current_user.zip_code
    
    return render_template('profile.html', title='Profile', form=form)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('change_password'))
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Your password has been updated.', 'success')
        return redirect(url_for('profile'))
    
    return render_template('change_password.html', title='Change Password', form=form)

# Inventory Management
@app.route('/inventory')
@login_required
def inventory():
    if not check_role([ROLE_ADMIN, ROLE_VOLUNTEER]):
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    items = FoodItem.query.order_by(FoodItem.category, FoodItem.name).all()
    categories = db.session.query(FoodItem.category).distinct().all()
    expiring_soon = FoodItem.query.filter(FoodItem.expiry_date != None).order_by(FoodItem.expiry_date.asc()).limit(10).all()
    from datetime import date
    today = date.today()
    return render_template('inventory.html', 
                          title='Food Inventory', 
                          items=items, 
                          categories=[c[0] for c in categories],
                          expiring_soon=expiring_soon,
                          today=today)

@app.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if not check_role([ROLE_ADMIN, ROLE_VOLUNTEER]):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = FoodItemForm()
    
    if form.validate_on_submit():
        item = FoodItem(
            name=form.name.data,
            category=form.category.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            expiry_date=form.expiry_date.data,
            location=form.location.data,
            nutritional_info=form.nutritional_info.data,
            allergens=form.allergens.data,
            barcode=form.barcode.data
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash('Item added successfully!', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('item_form.html', title='Add Inventory Item', form=form)

@app.route('/inventory/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    if not check_role([ROLE_ADMIN, ROLE_VOLUNTEER]):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    item = FoodItem.query.get_or_404(item_id)
    form = FoodItemForm()
    
    if form.validate_on_submit():
        item.name = form.name.data
        item.category = form.category.data
        item.quantity = form.quantity.data
        item.unit = form.unit.data
        item.expiry_date = form.expiry_date.data
        item.location = form.location.data
        item.nutritional_info = form.nutritional_info.data
        item.allergens = form.allergens.data
        item.barcode = form.barcode.data
        
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('inventory'))
    
    elif request.method == 'GET':
        form.name.data = item.name
        form.category.data = item.category
        form.quantity.data = item.quantity
        form.unit.data = item.unit
        form.expiry_date.data = item.expiry_date
        form.location.data = item.location
        form.nutritional_info.data = item.nutritional_info
        form.allergens.data = item.allergens
        form.barcode.data = item.barcode
    
    return render_template('item_form.html', title='Edit Inventory Item', form=form, item=item)

# Donation Management
@app.route('/donations')
@login_required
def donations():
    if current_user.role == ROLE_ADMIN:
        # Admin sees all donations
        donations = Donation.query.order_by(Donation.created_at.desc()).all()
    elif current_user.role in [ROLE_DONOR, ROLE_PARTNER]:
        # Donors and partners see their own donations
        donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).all()
    else:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('donations.html', title='Donations', donations=donations)

@app.route('/donations/new', methods=['GET', 'POST'])
@login_required
def new_donation():
    if not check_role([ROLE_DONOR, ROLE_PARTNER]):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = DonationForm()
    
    if form.validate_on_submit():
        donation = Donation(
            donor_id=current_user.id,
            donation_type=form.donation_type.data,
            amount=form.amount.data if form.donation_type.data == 'money' else None,
            pickup_date=form.pickup_date.data,
            pickup_address=form.pickup_address.data,
            notes=form.notes.data
        )
        
        db.session.add(donation)
        db.session.commit()
        
        # Create notification for admins
        admin_users = User.query.filter_by(role=ROLE_ADMIN).all()
        for admin in admin_users:
            notification = Notification(
                user_id=admin.id,
                title="New Donation Received",
                content=f"A new {form.donation_type.data} donation has been submitted and is pending approval.",
                notification_type="info"
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash('Thank you for your donation! We will process it shortly.', 'success')
        return redirect(url_for('donations'))
    
    return render_template('donation_form.html', title='Make a Donation', form=form)

@app.route('/donations/view/<int:donation_id>')
@login_required
def view_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    
    # Check permissions
    if current_user.role != ROLE_ADMIN and donation.donor_id != current_user.id:
        flash('You do not have permission to view this donation.', 'danger')
        return redirect(url_for('donations'))
    
    # Get donation items if it's a food donation
    items = FoodItem.query.filter_by(donation_id=donation_id).all() if donation.donation_type == 'food' else []
    
    # Prepare form for adding food items if donation is approved
    from forms import FoodItemForm
    form = FoodItemForm()
    
    return render_template('donation_detail.html', title='Donation Details', donation=donation, items=items, form=form)
    
@app.route('/donations/<int:donation_id>/add_item', methods=['GET', 'POST'])
@login_required
def add_donation_item(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    
    # Only donor who owns the donation or admin can add items
    if current_user.role != ROLE_ADMIN and donation.donor_id != current_user.id:
        flash('You do not have permission to add items to this donation.', 'danger')
        return redirect(url_for('donations'))
    
    # Only allow adding items if donation is approved
    if donation.status != 'approved':
        flash('You can only add items to approved donations.', 'warning')
        return redirect(url_for('view_donation', donation_id=donation_id))
    
    form = FoodItemForm()
    if form.validate_on_submit():
        item = FoodItem(
            name=form.name.data,
            category=form.category.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            expiry_date=form.expiry_date.data,
            location=form.location.data,
            nutritional_info=form.nutritional_info.data,
            allergens=form.allergens.data,
            barcode=form.barcode.data,
            donation_id=donation_id
        )
        db.session.add(item)
        db.session.commit()
        flash('Food item added successfully!', 'success')
        return redirect(url_for('view_donation', donation_id=donation_id))
    
    return render_template('item_form.html', title='Add Food Item', form=form, donation=donation)

@app.route('/donations/approve/<int:donation_id>', methods=['POST'])
@login_required
def approve_donation(donation_id):
    if not check_role(ROLE_ADMIN):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    donation = Donation.query.get_or_404(donation_id)
    
    if donation.status != 'pending':
        flash('This donation has already been processed.', 'warning')
        return redirect(url_for('view_donation', donation_id=donation_id))
    
    donation.status = 'approved'
    db.session.commit()
    
    # Create notification for donor
    notification = Notification(
        user_id=donation.donor_id,
        title="Donation Approved",
        content="Your donation has been approved. Thank you for your contribution!",
        notification_type="success"
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Donation has been approved.', 'success')
    return redirect(url_for('view_donation', donation_id=donation_id))

# Beneficiary Services
@app.route('/beneficiaries')
@login_required
def beneficiaries():
    if current_user.role == ROLE_ADMIN:
        # Admin sees all requests
        requests = FoodRequest.query.order_by(FoodRequest.created_at.desc()).all()
    elif current_user.role == ROLE_BENEFICIARY:
        # Beneficiaries see their own requests
        requests = FoodRequest.query.filter_by(beneficiary_id=current_user.id).order_by(FoodRequest.created_at.desc()).all()
    else:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('beneficiaries.html', title='Beneficiary Services', requests=requests)

@app.route('/beneficiaries/request', methods=['GET', 'POST'])
@login_required
def request_food():
    if not check_role(ROLE_BENEFICIARY):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = FoodRequestForm()
    
    if form.validate_on_submit():
        food_request = FoodRequest(
            beneficiary_id=current_user.id,
            household_size=form.household_size.data,
            request_items=form.request_items.data,
            emergency=form.emergency.data,
            notes=form.notes.data,
            appointment_date=form.appointment_date.data
        )
        
        db.session.add(food_request)
        db.session.commit()
        
        # Create notification for admins
        admin_users = User.query.filter_by(role=ROLE_ADMIN).all()
        for admin in admin_users:
            notification = Notification(
                user_id=admin.id,
                title="New Food Request",
                content=f"A new food request has been submitted" + (" (EMERGENCY)" if form.emergency.data else ""),
                notification_type="info" if not form.emergency.data else "warning"
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash('Your request has been submitted. We will process it as soon as possible.', 'success')
        return redirect(url_for('beneficiaries'))
    
    # Show available food categories
    categories = db.session.query(FoodItem.category).distinct().all()
    
    return render_template('request_form.html', 
                          title='Request Food', 
                          form=form, 
                          categories=[c[0] for c in categories])

@app.route('/beneficiaries/view/<int:request_id>')
@login_required
def view_request(request_id):
    food_request = FoodRequest.query.get_or_404(request_id)
    
    # Check permissions
    if current_user.role != ROLE_ADMIN and food_request.beneficiary_id != current_user.id:
        flash('You do not have permission to view this request.', 'danger')
        return redirect(url_for('beneficiaries'))
    
    beneficiary = User.query.get(food_request.beneficiary_id)
    
    return render_template('request_detail.html', 
                          title='Request Details', 
                          request=food_request, 
                          beneficiary=beneficiary)

@app.route('/beneficiaries/approve/<int:request_id>', methods=['POST'])
@login_required
def approve_request(request_id):
    if not check_role(ROLE_ADMIN):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    food_request = FoodRequest.query.get_or_404(request_id)
    
    if food_request.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('view_request', request_id=request_id))
    
    food_request.status = 'approved'
    db.session.commit()
    
    # Create notification for beneficiary
    notification = Notification(
        user_id=food_request.beneficiary_id,
        title="Food Request Approved",
        content="Your food request has been approved. Please check your appointment date.",
        notification_type="success"
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Request has been approved.', 'success')
    return redirect(url_for('view_request', request_id=request_id))

# Food Bank Locations
@app.route('/locations')
def locations():
    food_banks = FoodBank.query.all()
    return render_template('locations.html', title='Food Bank Locations', food_banks=food_banks)

@app.route('/locations/<int:food_bank_id>')
def food_bank_detail(food_bank_id):
    food_bank = FoodBank.query.get_or_404(food_bank_id)
    return render_template('food_bank_detail.html', title=food_bank.name, food_bank=food_bank)

@app.route('/locations/add', methods=['GET', 'POST'])
@login_required
def add_food_bank():
    if not check_role(ROLE_ADMIN):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = FoodBankForm()
    
    if form.validate_on_submit():
        food_bank = FoodBank(
            name=form.name.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            phone=form.phone.data,
            email=form.email.data,
            website=form.website.data,
            hours=form.hours.data,
            services=form.services.data,
            requirements=form.requirements.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data
        )
        
        db.session.add(food_bank)
        db.session.commit()
        
        flash('Food bank added successfully!', 'success')
        return redirect(url_for('locations'))
    
    return render_template('food_bank_form.html', title='Add Food Bank', form=form)

# Partner Portal
@app.route('/partners')
@login_required
def partners():
    if not check_role([ROLE_PARTNER, ROLE_ADMIN]):
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    if current_user.role == ROLE_ADMIN:
        partners = User.query.filter_by(role=ROLE_PARTNER).all()
        return render_template('partners_admin.html', title='Partner Organizations', partners=partners)
    else:
        # Partner sees their own dashboard
        donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).limit(5).all()
        return render_template('partners.html', title='Partner Portal', donations=donations)

@app.route('/partners/surplus', methods=['GET', 'POST'])
@login_required
def declare_surplus():
    if not check_role(ROLE_PARTNER):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = DonationForm()
    
    if form.validate_on_submit():
        donation = Donation(
            donor_id=current_user.id,
            donation_type='food',
            pickup_date=form.pickup_date.data,
            pickup_address=form.pickup_address.data,
            notes=form.notes.data
        )
        
        db.session.add(donation)
        db.session.commit()
        
        # Create notification for admins
        admin_users = User.query.filter_by(role=ROLE_ADMIN).all()
        for admin in admin_users:
            notification = Notification(
                user_id=admin.id,
                title="New Surplus Declaration",
                content=f"Partner {current_user.username} has declared surplus food for pickup.",
                notification_type="info"
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash('Surplus food has been declared. We will arrange pickup.', 'success')
        return redirect(url_for('partners'))
    
    return render_template('surplus_form.html', title='Declare Surplus Food', form=form)

# Volunteer Management
@app.route('/volunteers')
@login_required
def volunteers():
    if current_user.role == ROLE_ADMIN:
        # Admin sees all volunteers
        volunteers = User.query.filter_by(role=ROLE_VOLUNTEER).all()
        slots = VolunteerSlot.query.order_by(VolunteerSlot.date.asc()).all()
        return render_template('volunteers_admin.html', 
                              title='Volunteer Management', 
                              volunteers=volunteers, 
                              slots=slots)
    elif current_user.role == ROLE_VOLUNTEER:
        # Volunteer sees their own shifts
        upcoming_slots = VolunteerSlot.query.filter_by(
            volunteer_id=current_user.id, 
            status='filled'
        ).filter(
            VolunteerSlot.date >= datetime.utcnow().date()
        ).order_by(VolunteerSlot.date.asc()).all()
        
        completed_slots = VolunteerSlot.query.filter_by(
            volunteer_id=current_user.id, 
            status='completed'
        ).order_by(VolunteerSlot.date.desc()).all()
        
        available_slots = VolunteerSlot.query.filter_by(
            status='open'
        ).filter(
            VolunteerSlot.date >= datetime.utcnow().date()
        ).order_by(VolunteerSlot.date.asc()).all()
        
        return render_template('volunteers.html', 
                              title='Volunteer Portal', 
                              upcoming_slots=upcoming_slots, 
                              completed_slots=completed_slots,
                              available_slots=available_slots)
    else:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/volunteers/create_slot', methods=['GET', 'POST'])
@login_required
def create_volunteer_slot():
    if not check_role(ROLE_ADMIN):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = VolunteerSlotForm()
    form.food_bank_id.choices = [(fb.id, fb.name) for fb in FoodBank.query.all()]
    
    if form.validate_on_submit():
        slot = VolunteerSlot(
            food_bank_id=form.food_bank_id.data,
            role=form.role.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            notes=form.notes.data
        )
        
        db.session.add(slot)
        db.session.commit()
        
        flash('Volunteer opportunity created successfully!', 'success')
        return redirect(url_for('volunteers'))
    
    return render_template('volunteer_slot_form.html', title='Create Volunteer Opportunity', form=form)

@app.route('/volunteers/sign_up/<int:slot_id>', methods=['POST'])
@login_required
def volunteer_sign_up(slot_id):
    if not check_role(ROLE_VOLUNTEER):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    slot = VolunteerSlot.query.get_or_404(slot_id)
    
    if slot.status != 'open':
        flash('This volunteer opportunity is no longer available.', 'warning')
        return redirect(url_for('volunteers'))
    
    slot.volunteer_id = current_user.id
    slot.status = 'filled'
    db.session.commit()
    
    flash('You have successfully signed up for this volunteer opportunity!', 'success')
    return redirect(url_for('volunteers'))

@app.route('/volunteers/log_hours/<int:slot_id>', methods=['GET', 'POST'])
@login_required
def log_volunteer_hours(slot_id):
    if not check_role(ROLE_VOLUNTEER):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    slot = VolunteerSlot.query.get_or_404(slot_id)
    
    if slot.volunteer_id != current_user.id:
        flash('You are not assigned to this volunteer slot.', 'danger')
        return redirect(url_for('volunteers'))
    
    form = LogHoursForm()
    form.slot_id.data = slot_id
    
    if form.validate_on_submit():
        slot.hours_logged = form.hours_logged.data
        slot.status = 'completed'
        slot.notes = form.notes.data
        db.session.commit()
        
        # Create notification for admins
        admin_users = User.query.filter_by(role=ROLE_ADMIN).all()
        for admin in admin_users:
            notification = Notification(
                user_id=admin.id,
                title="Volunteer Hours Logged",
                content=f"{current_user.username} has logged {form.hours_logged.data} hours for {slot.role} on {slot.date}.",
                notification_type="info"
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash('Your volunteer hours have been logged successfully!', 'success')
        return redirect(url_for('volunteers'))
    
    return render_template('log_hours_form.html', title='Log Volunteer Hours', form=form, slot=slot)

# Admin Control Center
@app.route('/admin')
@login_required
def admin():
    if not check_role(ROLE_ADMIN):
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get summary statistics
    stats = {
        'total_users': User.query.count(),
        'total_donors': User.query.filter_by(role=ROLE_DONOR).count(),
        'total_beneficiaries': User.query.filter_by(role=ROLE_BENEFICIARY).count(),
        'total_volunteers': User.query.filter_by(role=ROLE_VOLUNTEER).count(),
        'total_partners': User.query.filter_by(role=ROLE_PARTNER).count(),
        'total_inventory_items': FoodItem.query.count(),
        'total_inventory_quantity': db.session.query(db.func.sum(FoodItem.quantity)).scalar() or 0,
        'total_donations': Donation.query.count(),
        'pending_donations': Donation.query.filter_by(status='pending').count(),
        'total_requests': FoodRequest.query.count(),
        'pending_requests': FoodRequest.query.filter_by(status='pending').count(),
        'total_food_banks': FoodBank.query.count(),
        'total_volunteer_hours': db.session.query(db.func.sum(VolunteerSlot.hours_logged)).filter_by(verified=True).scalar() or 0
    }
    
    # Query pending donations, requests, and unverified volunteer hours for approval queue
    pending_donations = Donation.query.filter_by(status='pending').order_by(Donation.created_at.desc()).limit(10).all()
    pending_requests = FoodRequest.query.filter_by(status='pending').order_by(FoodRequest.created_at.desc()).limit(10).all()
    unverified_volunteer_hours = VolunteerSlot.query.filter_by(status='completed', verified=False).order_by(VolunteerSlot.date.desc()).limit(10).all()
    
    return render_template('admin.html', title='Admin Control Center', stats=stats,
                           pending_donations=pending_donations,
                           pending_requests=pending_requests,
                           unverified_volunteer_hours=unverified_volunteer_hours)

@app.route('/admin/users')
@login_required
def admin_users():
    if not check_role(ROLE_ADMIN):
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin_users.html', title='User Management', users=users)

@app.route('/admin/verify_hours/<int:slot_id>', methods=['POST'])
@login_required
def verify_volunteer_hours(slot_id):
    if not check_role(ROLE_ADMIN):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    slot = VolunteerSlot.query.get_or_404(slot_id)
    
    if slot.status != 'completed':
        flash('This volunteer shift has not been completed yet.', 'warning')
        return redirect(url_for('volunteers'))
    
    slot.verified = True
    db.session.commit()
    
    # Create notification for volunteer
    notification = Notification(
        user_id=slot.volunteer_id,
        title="Volunteer Hours Verified",
        content=f"Your {slot.hours_logged} hours for {slot.role} on {slot.date} have been verified.",
        notification_type="success"
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Volunteer hours have been verified.', 'success')
    return redirect(url_for('volunteers'))

# Distribution Planning
@app.route('/distribution')
@login_required
def distribution():
    if not check_role([ROLE_ADMIN, ROLE_VOLUNTEER]):
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    distributions = Distribution.query.order_by(Distribution.distribution_date.asc()).all()
    upcoming = [d for d in distributions if d.distribution_date > datetime.utcnow()]
    past = [d for d in distributions if d.distribution_date <= datetime.utcnow()]
    
    return render_template('distribution.html', 
                          title='Distribution Planning', 
                          upcoming_distributions=upcoming, 
                          past_distributions=past)

@app.route('/distribution/create', methods=['GET', 'POST'])
@login_required
def create_distribution():
    if not check_role(ROLE_ADMIN):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = DistributionForm()
    form.food_bank_id.choices = [(fb.id, fb.name) for fb in FoodBank.query.all()]
    
    if form.validate_on_submit():
        distribution = Distribution(
            food_bank_id=form.food_bank_id.data,
            name=form.name.data,
            distribution_date=form.distribution_date.data,
            location=form.location.data,
            capacity=form.capacity.data,
            notes=form.notes.data
        )
        
        db.session.add(distribution)
        db.session.commit()
        
        flash('Distribution event created successfully!', 'success')
        return redirect(url_for('distribution'))
    
    return render_template('distribution_form.html', title='Create Distribution Event', form=form)

@app.route('/distribution/<int:distribution_id>')
@login_required
def distribution_detail(distribution_id):
    if not check_role([ROLE_ADMIN, ROLE_VOLUNTEER]):
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    distribution = Distribution.query.get_or_404(distribution_id)
    items = FoodItem.query.filter_by(distribution_id=distribution_id).all()
    food_bank = FoodBank.query.get(distribution.food_bank_id)
    
    return render_template('distribution_detail.html', 
                          title=f'Distribution: {distribution.name}', 
                          distribution=distribution, 
                          items=items,
                          food_bank=food_bank)

# Community Engagement
@app.route('/community')
def community():
    events = Event.query.order_by(Event.event_date.asc()).all()
    upcoming_events = [e for e in events if e.event_date > datetime.utcnow()]
    past_events = [e for e in events if e.event_date <= datetime.utcnow()]
    
    return render_template('community.html', 
                          title='Community Engagement', 
                          upcoming_events=upcoming_events, 
                          past_events=past_events)

@app.route('/community/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if not check_role([ROLE_ADMIN, ROLE_PARTNER]):
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = EventForm()
    
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            event_date=form.event_date.data,
            location=form.location.data,
            event_type=form.event_type.data,
            organizer_id=current_user.id,
            max_participants=form.max_participants.data,
            registration_required=form.registration_required.data,
            registration_link=form.registration_link.data if form.registration_required.data else None
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('community'))
    
    return render_template('event_form.html', title='Create Community Event', form=form)

@app.route('/community/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    organizer = User.query.get(event.organizer_id)
    
    return render_template('event_detail.html', 
                          title=f'Event: {event.title}', 
                          event=event, 
                          organizer=organizer)

# Notifications and Messages
@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read
    for notification in notifications:
        notification.read = True
    
    db.session.commit()
    
    return render_template('components/notification.html', notifications=notifications)

@app.route('/notifications/mark_read', methods=['POST'])
@login_required
def mark_notifications_read():
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()
    for notification in notifications:
        notification.read = True
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/notifications/count')
@login_required
def notifications_count():
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, read=False).count()
    unread_messages = Message.query.filter_by(recipient_id=current_user.id, read=False).count()

    return jsonify({
        "notifications": unread_notifications,
        "messages": unread_messages
    })


@app.route('/messages')
@login_required
def messages():
    received = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).all()
    sent = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at.desc()).all()
    
    # Mark received messages as read
    for message in received:
        message.read = True
    
    db.session.commit()
    
    return render_template('components/message.html', received=received, sent=sent)

@app.route('/messages/new', methods=['GET', 'POST'])
@login_required
def new_message():
    form = MessageForm()
    
    # Get all users for recipient selection, excluding current user
    users = User.query.filter(User.id != current_user.id).all()
    form.recipient_id.choices = [(u.id, f"{u.username} ({u.role})") for u in users]
    
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=form.recipient_id.data,
            subject=form.subject.data,
            content=form.content.data
        )
        
        db.session.add(message)
        db.session.commit()
        
        flash('Message sent successfully!', 'success')
        return redirect(url_for('messages'))
    
    return render_template('message_form.html', title='New Message', form=form)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error_code=403, error_message="Access forbidden"), 403
