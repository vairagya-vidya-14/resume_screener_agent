import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from models import db, MenuItem, Reservation, ContactMessage, Review, CustomDrink, Offer, GalleryItem, Order
from init_db import ensure_mysql_database, seed_database

load_dotenv()

# Serve static assets (css, images) directly from project directory
app = Flask(__name__, static_folder='.', static_url_path='', template_folder='templates')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'viyora_cafe_secret_key_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = ensure_mysql_database()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ensure tables & seed data on startup
with app.app_context():
    seed_database(app)

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def index_html():
    return render_template('index.html')

@app.route('/about')
@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/menu')
@app.route('/menu.html')
def menu():
    return render_template('menu.html')

@app.route('/order', methods=['POST'])
def place_order():
    table_number = request.form.get('table_number', 'Table 1')
    customer_name = request.form.get('customer_name', 'Guest')
    customer_email = request.form.get('customer_email', '')
    customer_phone = request.form.get('customer_phone', '')
    items_summary = request.form.get('items_summary', '')
    total_amount_raw = request.form.get('total_amount', '0.00')

    try:
        total_amount = float(total_amount_raw.replace('$', '').strip())
    except Exception:
        total_amount = 0.0

    if customer_name and table_number:
        new_order = Order(
            table_number=table_number,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            items_summary=items_summary,
            total_amount=total_amount,
            status='Received',
            created_at=datetime.now()
        )
        db.session.add(new_order)
        db.session.commit()

    return redirect('/menu#order-confirmed')

@app.route('/build', methods=['GET', 'POST'])
@app.route('/build.html', methods=['GET', 'POST'])
def build():
    if request.method == 'POST':
        base_coffee = request.form.get('coffee-base', 'Double Espresso')
        milk_type = request.form.get('milk', 'Whole Milk')
        sweetener = request.form.get('sugar', 'Organic Sugar')
        flavor_syrups = request.form.getlist('syrup')
        toppings = request.form.getlist('top')
        customer_name = request.form.get('customer_name', 'Guest')
        notes = request.form.get('notes', '')

        drink = CustomDrink(
            base_coffee=base_coffee,
            milk_type=milk_type,
            sweetener=sweetener,
            flavor_syrup=", ".join(flavor_syrups) if flavor_syrups else "None",
            toppings=", ".join(toppings) if toppings else "None",
            temperature="Hot",
            notes=notes,
            customer_name=customer_name,
            status='Received',
            created_at=datetime.now()
        )
        db.session.add(drink)
        db.session.commit()
        return redirect('/build#custom-ordered')

    return render_template('build.html')

@app.route('/gallery')
@app.route('/gallery.html')
def gallery():
    return render_template('gallery.html')

@app.route('/offers')
@app.route('/offers.html')
def offers():
    return render_template('offers.html')

@app.route('/reviews', methods=['GET', 'POST'])
@app.route('/reviews.html', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        author_name = request.form.get('author_name', 'Valued Customer')
        rating = int(request.form.get('rate', request.form.get('rating', 5)))
        comment = request.form.get('comment', 'Great coffee!')

        if author_name and comment:
            rev = Review(
                author_name=author_name,
                rating=rating,
                comment=comment,
                date_posted=datetime.now().strftime('%Y-%m-%d'),
                avatar="☕",
                created_at=datetime.now()
            )
            db.session.add(rev)
            db.session.commit()
            return redirect('/reviews#review-thanks')

    return render_template('reviews.html')

@app.route('/reservation', methods=['GET', 'POST'])
@app.route('/reservation.html', methods=['GET', 'POST'])
def reservation():
    if request.method == 'POST':
        name = request.form.get('name', 'Guest')
        email = request.form.get('email', '')
        phone = request.form.get('phone', 'N/A')
        guests_raw = request.form.get('guests', '2')
        try:
            guests = int(guests_raw.split()[0])
        except Exception:
            guests = 2
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        time = request.form.get('time', '07:00 PM')
        special_requests = request.form.get('special_requests', '')

        res = Reservation(
            name=name,
            email=email,
            phone=phone,
            guests=guests,
            date=date,
            time=time,
            special_requests=special_requests,
            created_at=datetime.now()
        )
        db.session.add(res)
        db.session.commit()
        return redirect('/reservation#booked')

    return render_template('reservation.html')

@app.route('/contact', methods=['GET', 'POST'])
@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', 'Visitor')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        subject = request.form.get('subject', 'General Inquiry')
        message = request.form.get('message', '')

        msg = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            created_at=datetime.now()
        )
        db.session.add(msg)
        db.session.commit()
        return redirect('/contact#message-sent')

    return render_template('contact.html')

# ==================== ADMIN MANAGEMENT DASHBOARD ====================

@app.route('/admin')
def admin():
    show_all = request.args.get('all', '0') == '1'
    selected_date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

    # All records from DB
    all_orders = Order.query.order_by(Order.id.desc()).all()
    all_reservations = Reservation.query.order_by(Reservation.id.desc()).all()
    all_messages = ContactMessage.query.order_by(ContactMessage.id.desc()).all()
    all_custom_drinks = CustomDrink.query.order_by(CustomDrink.id.desc()).all()
    all_reviews = Review.query.order_by(Review.id.desc()).all()

    if show_all:
        active_orders = [o for o in all_orders if o.status != 'Served']
        served_orders = [o for o in all_orders if o.status == 'Served']
        reservations = all_reservations
        messages = all_messages
        custom_drinks = all_custom_drinks
        reviews = all_reviews
    else:
        # STRICT DATE FILTERING: ONLY records belonging to selected_date_str
        active_orders = [o for o in all_orders if o.status != 'Served' and o.created_at and o.created_at.strftime('%Y-%m-%d') == selected_date_str]
        served_orders = [o for o in all_orders if o.status == 'Served' and o.created_at and o.created_at.strftime('%Y-%m-%d') == selected_date_str]
        reservations = [r for r in all_reservations if (r.created_at and r.created_at.strftime('%Y-%m-%d') == selected_date_str) or r.date == selected_date_str]
        messages = [m for m in all_messages if m.created_at and m.created_at.strftime('%Y-%m-%d') == selected_date_str]
        custom_drinks = [d for d in all_custom_drinks if d.created_at and d.created_at.strftime('%Y-%m-%d') == selected_date_str]
        reviews = [rev for rev in all_reviews if (rev.created_at and rev.created_at.strftime('%Y-%m-%d') == selected_date_str) or rev.date_posted == selected_date_str]

    daily_revenue = sum(o.total_amount for o in served_orders)

    return render_template('admin.html',
                           active_orders=active_orders,
                           served_orders=served_orders,
                           daily_revenue=daily_revenue,
                           selected_date=selected_date_str,
                           show_all=show_all,
                           reservations=reservations,
                           messages=messages,
                           reviews=reviews,
                           custom_drinks=custom_drinks)

@app.route('/admin/order/<int:order_id>/served', methods=['POST'])
def mark_order_served(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Served'
    db.session.commit()
    return redirect(request.referrer or '/admin')

@app.route('/admin/custom-drink/<int:drink_id>/served', methods=['POST'])
def mark_custom_drink_served(drink_id):
    drink = CustomDrink.query.get_or_404(drink_id)
    drink.status = 'Served'
    db.session.commit()
    return redirect(request.referrer or '/admin')

# ==================== JSON REST APIs ====================

@app.route('/api/menu', methods=['GET'])
def api_menu():
    items = MenuItem.query.order_by(MenuItem.item_number).all()
    return jsonify([i.to_dict() for i in items])

@app.route('/api/order', methods=['POST'])
def api_order():
    data = request.get_json() or request.form
    new_order = Order(
        table_number=data.get('table_number', 'Table 1'),
        customer_name=data.get('customer_name', 'Guest'),
        customer_email=data.get('customer_email', ''),
        customer_phone=data.get('customer_phone', ''),
        items_summary=data.get('items_summary', ''),
        total_amount=float(data.get('total_amount', 0.0)),
        status='Received',
        created_at=datetime.now()
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"status": "success", "message": "Order saved successfully!", "data": new_order.to_dict()}), 201

if __name__ == '__main__':
    print("[STARTING] Viyora Cafe Backend running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
