from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from app.models import User, AdminUser, Restaurant, FoodItem, Order
from app.forms import RestaurantForm, UserForm, FoodItemForm

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
            flash('Login Unsuccessful. Please check username and password', 'password')
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
        db.session.commit()
        flash('Restaurant added successfully!', 'success')
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
        db.session.commit()
        flash('Restaurant updated successfully!', 'success')
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
    form = FoodItemForm()
    if form.validate_on_submit():
        fooditem.name = form.name.data
        fooditem.price = form.price.data
        db.session.commit()
        flash('Food item updated successfully!', 'success')
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
    db.session.commit()
    flash('Food item deleted successfully!', 'success')
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
        db.session.commit()
        flash('User added successfully!', 'success')
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
        db.session.commit()
        flash('User updated successfully!', 'success')
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
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('list_users'))
