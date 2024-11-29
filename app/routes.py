from flask import render_template, redirect, url_for, request, flash, jsonify, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from . import db, login_manager
from .models import User, AdminUser, Restaurant, FoodItem, Order
from .forms import RestaurantForm, UserForm, FoodItemForm
from geopy.distance import geodesic

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

# General Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.password == password:  # Plain text comparison
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin Dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    orders_today = Order.query.filter(db.func.date(Order.order_date) == db.func.current_date()).count()
    orders_month = Order.query.filter(db.func.extract('month', Order.order_date) == db.func.extract('month', db.func.current_date())).count()
    sales_today = db.session.query(db.func.sum(Order.total_price)).filter(db.func.date(Order.order_date) == db.func.current_date()).scalar() or 0.0
    sales_month = db.session.query(db.func.sum(Order.total_price)).filter(db.func.extract('month', Order.order_date) == db.func.extract('month', db.func.current_date())).scalar() or 0.0
    return render_template('admin_dashboard.html', orders_today=orders_today, orders_month=orders_month, sales_today=sales_today, sales_month=sales_month)

# CRUD Operations for Restaurants
@app.route('/restaurants')
def list_restaurants():
    restaurants = Restaurant.query.all()
    return render_template('list_restaurants.html', restaurants=restaurants)

@app.route('/restaurant/add', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    form = RestaurantForm()
    if form.validate_on_submit():
        restaurant = Restaurant(
            name=form.name.data,
            address=form.address.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            image_url=form.image_url.data
        )
        db.session.add(restaurant)
        db.session.commit()
        flash('Restaurant added successfully!', 'success')
        return redirect(url_for('list_restaurants'))
    return render_template('add_restaurant.html', form=form)

@app.route('/restaurant/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    form = RestaurantForm(obj=restaurant)
    if form.validate_on_submit():
        form.populate_obj(restaurant)
        db.session.commit()
        flash('Restaurant updated successfully!', 'success')
        return redirect(url_for('list_restaurants'))
    return render_template('edit_restaurant.html', form=form)

@app.route('/restaurant/delete/<int:id>', methods=['POST'])
@login_required
def delete_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    db.session.delete(restaurant)
    db.session.commit()
    flash('Restaurant deleted successfully!', 'success')
    return redirect(url_for('list_restaurants'))

# CRUD Operations for Food Items
@app.route('/restaurants/<int:restaurant_id>/fooditems')
@login_required
def manage_fooditems(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    fooditems = FoodItem.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('manage_fooditems.html', restaurant=restaurant, fooditems=fooditems)

@app.route('/restaurants/<int:restaurant_id>/fooditem/add', methods=['GET', 'POST'])
@login_required
def add_fooditem(restaurant_id):
    form = FoodItemForm()
    if form.validate_on_submit():
        fooditem = FoodItem(name=form.name.data, price=form.price.data, restaurant_id=restaurant_id)
        db.session.add(fooditem)
        db.session.commit()
        flash('Food item added successfully!', 'success')
        return redirect(url_for('manage_fooditems', restaurant_id=restaurant_id))
    return render_template('add_fooditem.html', form=form, restaurant_id=restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/fooditem/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_fooditem(restaurant_id, id):
    fooditem = FoodItem.query.get_or_404(id)
    form = FoodItemForm(obj=fooditem)
    if form.validate_on_submit():
        form.populate_obj(fooditem)
        db.session.commit()
        flash('Food item updated successfully!', 'success')
        return redirect(url_for('manage_fooditems', restaurant_id=restaurant_id))
    return render_template('edit_fooditem.html', form=form, restaurant_id=restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/fooditem/delete/<int:id>', methods=['POST'])
@login_required
def delete_fooditem(restaurant_id, id):
    fooditem = FoodItem.query.get_or_404(id)
    db.session.delete(fooditem)
    db.session.commit()
    flash('Food item deleted successfully!', 'success')
    return redirect(url_for('manage_fooditems', restaurant_id=restaurant_id))

# API Endpoints
@app.route('/api/restaurants/nearby', methods=['POST'])
def api_nearby_restaurants():
    data = request.get_json()
    user_location = (data['lat'], data['lng'])
    max_distance = 10000000 # kilometers
    nearby_restaurants = []

    print(f"User location: {user_location}")  # Debugging

    all_restaurants = Restaurant.query.all()
    print(f"Found {len(all_restaurants)} restaurants in the database.")  # Debugging

    for restaurant in all_restaurants:
        restaurant_location = (restaurant.latitude, restaurant.longitude)
        distance = geodesic(user_location, restaurant_location).kilometers
        print(f"Checking restaurant: {restaurant.name}, Distance: {distance} km")  # Debugging

        if distance <= max_distance:
            nearby_restaurants.append({
                'id': restaurant.id,
                'name': restaurant.name,
                'address': restaurant.address,
                'latitude': restaurant.latitude,
                'longitude': restaurant.longitude,
                'image_url': restaurant.image_url,
                'distance': distance
            })

    print(f"Nearby restaurants: {nearby_restaurants}")  # Debugging
    return jsonify({'nearby_restaurants': nearby_restaurants})


