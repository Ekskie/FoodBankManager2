from flask import flash
from app import db
from models import User, Notification
from datetime import datetime, timedelta

def send_notification(user_id, title, content, notification_type='info'):
    """
    Create and save a notification for a specific user
    
    Args:
        user_id (int): The ID of the user to notify
        title (str): The title of the notification
        content (str): The content of the notification
        notification_type (str): The type of notification (info, success, warning, error)
    
    Returns:
        bool: True if notification was created, False otherwise
    """
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            notification_type=notification_type
        )
        db.session.add(notification)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {str(e)}")
        return False

def notify_admins(title, content, notification_type='info'):
    """
    Send notifications to all admin users
    
    Args:
        title (str): The title of the notification
        content (str): The content of the notification
        notification_type (str): The type of notification (info, success, warning, error)
    
    Returns:
        int: Number of admins notified
    """
    admin_users = User.query.filter_by(role='admin').all()
    count = 0
    
    for admin in admin_users:
        if send_notification(admin.id, title, content, notification_type):
            count += 1
    
    return count

def check_expiring_inventory(days=7):
    """
    Check for food items that will expire within the specified number of days
    and create notifications for admins
    
    Args:
        days (int): Number of days to look ahead for expirations
    
    Returns:
        int: Number of expiring items found
    """
    from models import FoodItem
    
    expiry_date = datetime.utcnow().date() + timedelta(days=days)
    expiring_items = FoodItem.query.filter(
        FoodItem.expiry_date <= expiry_date,
        FoodItem.expiry_date >= datetime.utcnow().date()
    ).all()
    
    if expiring_items:
        item_list = ", ".join([f"{item.name} (Expires: {item.expiry_date})" for item in expiring_items[:5]])
        if len(expiring_items) > 5:
            item_list += f", and {len(expiring_items) - 5} more items"
        
        notify_admins(
            title=f"{len(expiring_items)} food items expiring soon",
            content=f"The following items are expiring within {days} days: {item_list}",
            notification_type="warning"
        )
    
    return len(expiring_items)

def format_date(date):
    """Format a date object as a readable string"""
    if isinstance(date, datetime):
        return date.strftime("%b %d, %Y %I:%M %p")
    return date.strftime("%b %d, %Y") if date else ""

def format_currency(amount):
    """Format a number as currency"""
    return f"${amount:.2f}" if amount is not None else "$0.00"

def calculate_impact_metrics(user_id=None):
    """
    Calculate impact metrics for a specific user or the entire system
    
    Args:
        user_id (int, optional): The ID of the user to calculate metrics for.
            If None, calculates metrics for the entire system.
    
    Returns:
        dict: A dictionary containing various impact metrics
    """
    from models import Donation, FoodRequest, VolunteerSlot
    
    metrics = {}
    
    # Donation metrics
    donation_query = Donation.query.filter_by(status='approved')
    if user_id:
        donation_query = donation_query.filter_by(donor_id=user_id)
    
    metrics['donations_count'] = donation_query.count()
    
    # Sum monetary donations
    monetary_donations = donation_query.filter_by(donation_type='money')
    metrics['total_monetary'] = db.session.query(
        db.func.sum(Donation.amount)
    ).filter(
        Donation.id.in_([d.id for d in monetary_donations])
    ).scalar() or 0
    
    # Beneficiary metrics
    request_query = FoodRequest.query.filter_by(status='fulfilled')
    if user_id:
        request_query = request_query.filter_by(beneficiary_id=user_id)
    
    metrics['people_helped'] = db.session.query(
        db.func.sum(FoodRequest.household_size)
    ).filter(
        FoodRequest.id.in_([r.id for r in request_query])
    ).scalar() or 0
    
    metrics['requests_fulfilled'] = request_query.count()
    
    # Volunteer metrics
    volunteer_query = VolunteerSlot.query.filter_by(status='completed', verified=True)
    if user_id:
        volunteer_query = volunteer_query.filter_by(volunteer_id=user_id)
    
    metrics['volunteer_hours'] = db.session.query(
        db.func.sum(VolunteerSlot.hours_logged)
    ).filter(
        VolunteerSlot.id.in_([v.id for v in volunteer_query])
    ).scalar() or 0
    
    # Calculate estimated meals provided (rough estimate)
    # Assuming $1 = 3 meals for monetary donations
    metrics['estimated_meals'] = int(metrics['total_monetary'] * 3)
    
    return metrics
