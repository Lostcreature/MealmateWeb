from app import app, db
from app.models import AdminUser

def insert_default_admin():
    # Check if the default admin user already exists
    if not AdminUser.query.filter_by(username='admin').first():
        # If not, create the default admin user
        admin_user = AdminUser(username='admin', password='admin_password')
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created.")
    else:
        print("Default admin user already exists.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        insert_default_admin()  # Insert default admin user
    app.run(debug=True)
