from flask import render_template, redirect, url_for, request, flash, jsonify, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from . import db, login_manager
from .models import User, AdminUser, Restaurant, FoodItem, Order
from .forms import RestaurantForm, UserForm, FoodItemForm

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

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

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    orders_today = Order.query.filter(db.func.date(Order.order_date) == db.func.current_date()).count()
    orders_month = Order.query.filter(db.func.extract('month', Order.order_date) == db.func.extract('month', db.func.current_date())).count()
    sales_today = db.session.query(db.func.sum(Order.total_price)).filter(db.func.date(Order.order_date) == db.func.current_date()).scalar() or 0.0
    sales_month = db.session.query(db.func.sum(Order.total_price)).filter(db.func.extract('month', Order.order_date) == db.func.extract('month', db.func.current_date())).scalar() or 0.0
    return render_template('admin_dashboard.html', orders_today=orders_today, orders_month=orders_month, sales_today=sales_today, sales_month=sales_month)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# CRUD Operations for Restaurants
@app.route('/restaurants')
@login_required
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
        try:
            db.session.commit()
            app.logger.info('Restaurant added: %s', restaurant.name)
            flash('Restaurant added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error('Error adding restaurant: %s', e)
            flash('Error: {}'.format(e), 'danger')
        return redirect(url_for('list_restaurants'))
    return render_template('add_restaurant.html', form=form)

@app.route('/restaurant/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    form = RestaurantForm()
    if form.validate_on_submit():
        restaurant.name = form.name.data
        restaurant.address = form.address.data
        restaurant.latitude = form.latitude.data
        restaurant.longitude = form.longitude.data
        restaurant.image_url = form.image_url.data
        try:
            db.session.commit()
            app.logger.info('Restaurant updated: %s', restaurant.name)
            flash('Restaurant updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error('Error updating restaurant: %s', e)
            flash('Error: {}'.format(e), 'danger')
        return redirect(url_for('list_restaurants'))
    elif request.method == 'GET':
        form.name.data = restaurant.name
        form.address.data = restaurant.address
        form.latitude.data = restaurant.latitude
        form.longitude.data = restaurant.longitude
        form.image_url.data = restaurant.image_url
    return render_template('edit_restaurant.html', form=form)

@app.route('/restaurant/delete/<int:id>', methods=['POST'])
@login_required
def delete_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    db.session.delete(restaurant)
    try:
        db.session.commit()
        app.logger.info('Restaurant deleted: %s', restaurant.name)
        flash('Restaurant deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error deleting restaurant: %s', e)
        flash('Error: {}'.format(e), 'danger')
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
        try:
            db.session.commit()
            app.logger.info('Food item added: %s', fooditem.name)
            flash('Food item added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error('Error adding food item: %s', e)
            flash('Error: {}'.format(e), 'danger')
        return redirect(url_for('manage_fooditems', restaurant_id=restaurant_id))
    return render_template('add_fooditem.html', form=form, restaurant_id=restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/fooditem/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_fooditem(restaurant_id, id):
    fooditem = FoodItem.query.get_or_404(id)
    form = FoodItemForm()
    if form.validate_on_submit():
        fooditem.name = form.name.data
        fooditem.price = form.price.data
        try:
            db.session.commit()
            app.logger.info('Food item updated: %s', fooditem.name)
            flash('Food item updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error('Error updating food item: %s', e)
            flash('Error: {}'.format(e), 'danger')
        return redirect(url_for('manage_fooditems', restaurant_id=restaurant_id))
    elif request.method == 'GET':
        form.name.data = fooditem.name
        form.price.data = fooditem.price
    return render_template('edit_fooditem.html', form=form, restaurant_id=restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/fooditem/delete/<int:id>', methods=['POST'])
@login_required
def delete_fooditem(restaurant_id, id):
    fooditem = FoodItem.query.get_or_404(id)
    db.session.delete(fooditem)
    try:
        db.session.commit()
        app.logger.info('Food item deleted: %s', fooditem.name)
        flash('Food item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error deleting food item: %s', e)
        flash('Error: {}'.format(e), 'danger')
    return redirect(url_for('manage_fooditems', restaurant_id=restaurant_id))

# CRUD Operations for Users
@app.route('/users')
@login_required
def list_users():
    users = User.query.all()
    return render_template('list_users.html', users=users)

@app.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            app.logger.info('User added: %s', user.username)
            flash('User added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error('Error adding user: %s', e)
            flash('Error: {}'.format(e), 'danger')
        return redirect(url_for('list_users'))
    return render_template('add_user.html', form=form)

@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm()
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        try:
            db.session.commit()
            app.logger.info('User updated: %s', user.username)
            flash('User updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error('Error updating user: %s', e)
            flash('Error: {}'.format(e), 'danger')
        return redirect(url_for('list_users'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
    return render_template('edit_user.html', form=form)

@app.route('/user/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    try:
        db.session.commit()
        app.logger.info('User deleted: %s', user.username)
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error deleting user: %s', e)
        flash('Error: {}'.format(e), 'danger')
    return redirect(url_for('list_users'))

# API Endpoints

# API Endpoint for listing all restaurants
@app.route('/api/restaurants', methods=['GET'])
@login_required
def api_list_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = []
    for restaurant in restaurants:
        restaurant_data = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'latitude': restaurant.latitude,
            'longitude': restaurant.longitude,
            'image_url': restaurant.image_url
        }
        restaurant_list.append(restaurant_data)
    return jsonify({'restaurants': restaurant_list})

# API Endpoint for retrieving a specific restaurant
@app.route('/api/restaurant/<int:id>', methods=['GET'])
@login_required
def api_get_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    restaurant_data = {
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address,
        'latitude': restaurant.latitude,
        'longitude': restaurant.longitude,
        'image_url': restaurant.image_url
    }
    return jsonify(restaurant_data)

# API Endpoint for adding a restaurant
@app.route('/api/restaurant/add', methods=['POST'])
@login_required
def api_add_restaurant():
    data = request.get_json()
    restaurant = Restaurant(
        name=data['name'],
        address=data['address'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        image_url=data['image_url']
    )
    db.session.add(restaurant)
    try:
        db.session.commit()
        app.logger.info('Restaurant added via API: %s', restaurant.name)
        return jsonify({'message': 'Restaurant added successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error adding restaurant via API: %s', e)
        return jsonify({'error': str(e)}), 500

# API Endpoint for editing a restaurant
@app.route('/api/restaurant/edit/<int:id>', methods=['PUT'])
@login_required
def api_edit_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    data = request.get_json()
    restaurant.name = data['name']
    restaurant.address = data['address']
    restaurant.latitude = data['latitude']
    restaurant.longitude = data['longitude']
    restaurant.image_url = data['image_url']
    try:
        db.session.commit()
        app.logger.info('Restaurant updated via API: %s', restaurant.name)
        return jsonify({'message': 'Restaurant updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error updating restaurant via API: %s', e)
        return jsonify({'error': str(e)}), 500

# API Endpoint for deleting a restaurant
@app.route('/api/restaurant/delete/<int:id>', methods=['DELETE'])
@login_required
def api_delete_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    db.session.delete(restaurant)
    try:
        db.session.commit()
        app.logger.info('Restaurant deleted via API: %s', restaurant.name)
        return jsonify({'message': 'Restaurant deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error deleting restaurant via API: %s', e)
        return jsonify({'error': str(e)}), 500

# API Endpoint for listing all food items of a restaurant
@app.route('/api/restaurants/<int:restaurant_id>/fooditems', methods=['GET'])
@login_required
def api_list_fooditems(restaurant_id):
    fooditems = FoodItem.query.filter_by(restaurant_id=restaurant_id).all()
    fooditem_list = []
    for fooditem in fooditems:
        fooditem_data = {
            'id': fooditem.id,
            'name': fooditem.name,
            'price': fooditem.price,
            'restaurant_id': fooditem.restaurant_id
        }
        fooditem_list.append(fooditem_data)
    return jsonify({'fooditems': fooditem_list})

# API Endpoint for retrieving a specific food item
@app.route('/api/restaurants/<int:restaurant_id>/fooditem/<int:id>', methods=['GET'])
@login_required
def api_get_fooditem(restaurant_id, id):
    fooditem = FoodItem.query.filter_by(restaurant_id=restaurant_id, id=id).first_or_404()
    fooditem_data = {
        'id': fooditem.id,
        'name': fooditem.name,
        'price': fooditem.price,
        'restaurant_id': fooditem.restaurant_id
    }
    return jsonify(fooditem_data)

# API Endpoint for adding a food item to a restaurant
@app.route('/api/restaurants/<int:restaurant_id>/fooditem/add', methods=['POST'])
@login_required
def api_add_fooditem(restaurant_id):
    data = request.get_json()
    fooditem = FoodItem(
        name=data['name'],
        price=data['price'],
        restaurant_id=restaurant_id
    )
    db.session.add(fooditem)
    try:
        db.session.commit()
        app.logger.info('Food item added via API: %s', fooditem.name)
        return jsonify({'message': 'Food item added successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error adding food item via API: %s', e)
        return jsonify({'error': str(e)}), 500

# API Endpoint for editing a food item
@app.route('/api/restaurants/<int:restaurant_id>/fooditem/edit/<int:id>', methods=['PUT'])
@login_required
def api_edit_fooditem(restaurant_id, id):
    fooditem = FoodItem.query.filter_by(restaurant_id=restaurant_id, id=id).first_or_404()
    data = request.get_json()
    fooditem.name = data['name']
    fooditem.price = data['price']
    try:
        db.session.commit()
        app.logger.info('Food item updated via API: %s', fooditem.name)
        return jsonify({'message': 'Food item updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error updating food item via API: %s', e)
        return jsonify({'error': str(e)}), 500

# API Endpoint for deleting a food item
@app.route('/api/restaurants/<int:restaurant_id>/fooditem/delete/<int:id>', methods=['DELETE'])
@login_required
def api_delete_fooditem(restaurant_id, id):
    fooditem = FoodItem.query.filter_by(restaurant_id=restaurant_id, id=id).first_or_404()
    db.session.delete(fooditem)
    try:
        db.session.commit()
        app.logger.info('Food item deleted via API: %s', fooditem.name)
        return jsonify({'message': 'Food item deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error deleting food item via API: %s', e)
        return jsonify({'error': str(e)}), 500

# API Endpoint for listing all users
@app.route('/api/users', methods=['GET'])
@login_required
def api_list_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
        user_list.append(user_data)
    return jsonify({'users': user_list})

# API Endpoint for retrieving a specific user
@app.route('/api/user/<int:id>', methods=['GET'])
@login_required
def api_get_user(id):
    user = User.query.get_or_404(id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }
    return jsonify(user_data)

# API Endpoint for adding a user
@app.route('/api/user/add', methods=['POST'])
@login_required
def api_add_user():
    data = request.get_json()
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password']  # Note: In practice, password handling should be more secure (e.g., hashing)
    )
    db.session.add(user)
    try:
        db.session.commit()
        app.logger.info('User added via API: %s', user.username)
        return jsonify({'message': 'User added successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error adding user via API: %s', e)
        return jsonify({'error': str(e)}), 500

# API Endpoint for editing a user
@app.route('/api/user/edit/<int:id>', methods=['PUT'])
@login_required
def api_edit_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    user.username = data['username']
    user.email = data['email']
    user.password = data['password']  # Note: Handle password securely in production
    try:
        db.session.commit()
        app.logger.info('User updated via API: %s', user.username)
        return jsonify({'message': 'User updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error updating user via API: %s', e)
        return jsonify({'error': str(e)}), 500

# API Endpoint for deleting a user
@app.route('/api/user/delete/<int:id>', methods=['DELETE'])
@login_required
def api_delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    try:
        db.session.commit()
        app.logger.info('User deleted via API: %s', user.username)
        return jsonify({'message': 'User deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error deleting user via API: %s', e)
        return jsonify({'error': str(e)}), 500

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
