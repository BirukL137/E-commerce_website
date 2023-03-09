# Import necessary modules
from flask import render_template,session, request,redirect,url_for,flash,current_app,make_response
from flask_login import login_required, current_user, logout_user, login_user
from shop import app,db,photos, search,bcrypt,login_manager
from .forms import CustomerRegisterForm, CustomerLoginFrom
from .model import Register,CustomerOrder
import secrets
import pdfkit
import stripe

# Set Stripe API keys
buplishable_key ='pk_test_MaILxTYQ15v5Uhd6NKI9wPdD00qdL0QZSl'
stripe.api_key ='sk_test_9JlhVB6qwjcRdYzizjdwgIo0Dt00N55uxbWy'

@app.route('/payment',methods=['POST'])
def payment():
    # get the invoice and amount from the form data
    invoice = request.get('invoice')
    amount = request.form.get('amount')
    
    # create a Stripe customer using the email and token from the form
    customer = stripe.Customer.create(
      email=request.form['stripeEmail'],
      source=request.form['stripeToken'],
    )
    
    # create a Stripe charge using the customer id, description, amount, and currency
    charge = stripe.Charge.create(
      customer=customer.id,
      description='Myshop',
      amount=amount,
      currency='usd',
    )
    
    # find the latest order with the given invoice and customer id, and mark it as paid
    orders =  CustomerOrder.query.filter_by(customer_id = current_user.id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    
    # redirect to the thank you page
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    # render the thank you page
    return render_template('customer/thank.html')


# Customer Registration and Login Routes
# These routes handle customer registration and login functionality for the web application.

@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    # Initialize the registration form and check for validation on submission
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        # Generate a hashed password from the user's input
        hash_password = bcrypt.generate_password_hash(form.password.data)
        # Create a new user record in the database with the hashed password and other form data
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data,password=hash_password,country=form.country.data, city=form.city.data,contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data)
        # Add the new user record to the database, commit the transaction, and redirect to the login page
        db.session.add(register)
        flash(f'Welcome {form.name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('login'))
    # If the form is not submitted or fails validation, render the registration form template with the form object
    return render_template('customer/register.html', form=form)

@app.route('/customer/login', methods=['GET','POST'])
def customerLogin():
    # Initialize the login form and check for validation on submission
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        # Query the database for a user record with the provided email address
        user = Register.query.filter_by(email=form.email.data).first()
        # If the user record exists and the provided password matches the stored hash, log the user in and redirect to the home page
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are login now!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        # If the user record does not exist or the password does not match, display an error message and redirect to the login page
        flash('Incorrect email and password','danger')
        return redirect(url_for('customerLogin'))
    # If the form is not submitted or fails validation, render the login form template with the form object
    return render_template('customer/login.html', form=form)


# Customer Logout Route
# This route logs out the current user and redirects to the home page.

@app.route('/customer/logout')
def customer_logout():
    # Log out the current user and redirect to the home page
    logout_user()
    return redirect(url_for('home'))

# Update Shopping Cart Function
# This function updates the shopping cart by removing unnecessary data from the cart session.

def updateshoppingcart():
    # Iterate over each item in the shopping cart session
    for key, shopping in session['Shoppingcart'].items():
        # Set the session modification flag to True
        session.modified = True
        # Remove the image and color information from the shopping cart item
        del shopping['image']
        del shopping['colors']
    # Return the updated shopping cart
    return updateshoppingcart


# Get Order Route
# This route handles placing a new order for the current user.

@app.route('/getorder')
@login_required
def get_order():
    # Check if the current user is authenticated
    if current_user.is_authenticated:
        # Get the customer ID of the current user
        customer_id = current_user.id
        # Generate a unique invoice ID using the secrets module
        invoice = secrets.token_hex(5)
        # Call the updateshoppingcart function to remove unnecessary data from the shopping cart session
        updateshoppingcart
        # Attempt to add a new order to the database
        try:
            # Create a new CustomerOrder object with the invoice ID, customer ID, and orders from the shopping cart session
            order = CustomerOrder(invoice=invoice,customer_id=customer_id,orders=session['Shoppingcart'])
            # Add the order to the database
            db.session.add(order)
            db.session.commit()
            # Clear the shopping cart session
            session.pop('Shoppingcart')
            # Display a success message and redirect to the orders page for the new order
            flash('Your order has been sent successfully','success')
            return redirect(url_for('orders',invoice=invoice))
        # Handle any exceptions that occur during the order placement process
        except Exception as e:
            # Print the exception to the console for debugging purposes
            print(e)
            # Display an error message and redirect to the shopping cart page
            flash('Some thing went wrong while get order', 'danger')
            return redirect(url_for('getCart'))


@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    # If the user is authenticated
    if current_user.is_authenticated:
        # Initialize variables for subTotal, grandTotal, and customer ID
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        
        # Query the Register model to get the customer details
        customer = Register.query.filter_by(id=customer_id).first()
        
        # Query the CustomerOrder model to get the customer's orders with the specified invoice number
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        
        # Loop through each item in the customer's orders
        for _key, product in orders.orders.items():
            # Calculate the discount and subtract it from the subtotal
            discount = (product['discount']/100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            
            # Calculate the tax and grand total
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))
            
    # If the user is not authenticated, redirect to the customer login page
    else:
        return redirect(url_for('customerLogin'))
    
    # Render the order.html template with the invoice number, tax, subTotal, grandTotal, customer details, and customer's orders
    return render_template('customer/order.html', invoice=invoice, tax=tax,subTotal=subTotal,grandTotal=grandTotal,customer=customer,orders=orders)




@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    # If the user is authenticated
    if current_user.is_authenticated:
        # Initialize variables for subTotal, grandTotal, and customer ID
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        
        # If the request method is POST
        if request.method =="POST":
            # Query the Register model to get the customer details
            customer = Register.query.filter_by(id=customer_id).first()
            
            # Query the CustomerOrder model to get the customer's orders with the specified invoice number
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            
            # Loop through each item in the customer's orders
            for _key, product in orders.orders.items():
                # Calculate the discount and subtract it from the subtotal
                discount = (product['discount']/100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                
                # Calculate the tax and grand total
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = float("%.2f" % (1.06 * subTotal))
            
            # Render the pdf.html template with the necessary variables
            rendered = render_template('customer/pdf.html', invoice=invoice, tax=tax,grandTotal=grandTotal,customer=customer,orders=orders)
            
            # Convert the rendered template to PDF using pdfkit
            pdf = pdfkit.from_string(rendered, False)
            
            # Create a Flask response object for the PDF file
            response = make_response(pdf)
            response.headers['content-Type'] ='application/pdf'
            response.headers['content-Disposition'] ='inline; filename='+invoice+'.pdf'
            
            # Return the response object
            return response
    
    # If the user is not authenticated, redirect to the customer's orders page
    return request(url_for('orders'))
