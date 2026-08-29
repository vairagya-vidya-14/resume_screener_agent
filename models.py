from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    item_number = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    badge = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "item_number": self.item_number,
            "name": self.name,
            "category": self.category,
            "subcategory": self.subcategory,
            "description": self.description,
            "price": self.price,
            "badge": self.badge,
            "image_url": self.image_url
        }

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(30), nullable=False)
    items_summary = db.Column(db.Text, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='Received')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "table_number": self.table_number,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "items_summary": self.items_summary,
            "total_amount": self.total_amount,
            "status": self.status,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    special_requests = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='Confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "guests": self.guests,
            "date": self.date,
            "time": self.time,
            "special_requests": self.special_requests,
            "status": self.status,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "subject": self.subject,
            "message": self.message,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.String(50), default='Just now')
    avatar = db.Column(db.String(50), default='👨‍💼')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "author_name": self.author_name,
            "rating": self.rating,
            "comment": self.comment,
            "date_posted": self.date_posted,
            "avatar": self.avatar,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class CustomDrink(db.Model):
    __tablename__ = 'custom_drinks'
    id = db.Column(db.Integer, primary_key=True)
    base_coffee = db.Column(db.String(100), nullable=False)
    milk_type = db.Column(db.String(50), nullable=False)
    sweetener = db.Column(db.String(50), nullable=False)
    flavor_syrup = db.Column(db.String(100), nullable=True)
    toppings = db.Column(db.String(255), nullable=True)
    temperature = db.Column(db.String(20), default='Hot')
    notes = db.Column(db.Text, nullable=True)
    customer_name = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(30), default='Received')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "base_coffee": self.base_coffee,
            "milk_type": self.milk_type,
            "sweetener": self.sweetener,
            "flavor_syrup": self.flavor_syrup,
            "toppings": self.toppings,
            "temperature": self.temperature,
            "notes": self.notes,
            "customer_name": self.customer_name,
            "status": self.status,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    discount = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    badge = db.Column(db.String(50), default='Special')
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "code": self.code,
            "discount": self.discount,
            "description": self.description,
            "badge": self.badge,
            "is_active": self.is_active
        }

class GalleryItem(db.Model):
    __tablename__ = 'gallery_items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "image_url": self.image_url,
            "description": self.description
        }
