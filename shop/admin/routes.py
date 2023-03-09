# Import necessary modules
from flask import render_template,session, request,redirect,url_for,flash
from shop import app,db,bcrypt
from .forms import RegistrationForm,LoginForm
from .models import User
from shop.products.models import Addproduct,Category,Brand

@app.route('/admin')
def admin():
    # Retrieve all products from the Addproduct table using query.all()
    products = Addproduct.query.all()
    # Render the admin/index.html template with the title 'Admin page' and the retrieved products
    return render_template('admin/index.html', title='Admin page', products=products)

@app.route('/brands')
def brands():
    # Retrieve all brands from the Brand table using query.order_by(Brand.id.desc()).all()
    brands = Brand.query.order_by(Brand.id.desc()).all()
    # Render the admin/brand.html template with the title 'brands' and the retrieved brands
    return render_template('admin/brand.html', title='brands', brands=brands)

@app.route('/categories')
def categories():
    # Retrieve all categories from the Category table using query.order_by(Category.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    # Render the admin/brand.html template with the title 'categories' and the retrieved categories
    return render_template('admin/brand.html', title='categories', categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Create a RegistrationForm object
    form = RegistrationForm()
    # Check if the form is valid after the user submits the form
    if form.validate_on_submit():
        # Hash the password using bcrypt
        hash_password = bcrypt.generate_password_hash(form.password.data)
        # Create a new User object with the form data and hashed password
        user = User(name=form.name.data, username=form.username.data, email=form.email.data,
                    password=hash_password)
        # Add the new user to the database session
        db.session.add(user)
        # Flash a success message and commit the changes to the database
        flash(f'welcome {form.name.data} Thanks for registering', 'success')
        db.session.commit()
        # Redirect the user to the login page after successful registration
        return redirect(url_for('login'))
    # Render the admin/register.html template with the title 'Register user' and the RegistrationForm object
    return render_template('admin/register.html', title='Register user', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    # create an instance of the LoginForm
    form = LoginForm()
    # check if the form is submitted and validated
    if form.validate_on_submit():
        # query the user from the database using the email
        user = User.query.filter_by(email=form.email.data).first()
        # check if the user exists and the password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # create a session for the user using the email
            session['email'] = form.email.data
            # flash a success message
            flash(f'welcome {form.email.data} you are logedin now','success')
            # redirect the user to the admin page
            return redirect(url_for('admin'))
        else:
            # flash an error message
            flash(f'Wrong email and password', 'success')
            # redirect the user to the login page
            return redirect(url_for('login'))
    # render the login page
    return render_template('admin/login.html',title='Login page',form=form)
