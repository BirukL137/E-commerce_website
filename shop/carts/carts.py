# Import necessary modules
from flask import render_template,session, request,redirect,url_for,flash,current_app
from shop import db , app
from shop.products.models import Addproduct
from shop.products.routes import brands, categories
import json

def MagerDicts(dict1, dict2):
    # Check if both inputs are lists
    if isinstance(dict1, list) and isinstance(dict2,list):
        # Concatenate the lists and return the result
        return dict1  + dict2
    # Check if both inputs are dictionaries
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        # Merge the two dictionaries into a new dictionary
        merged_dict = dict(list(dict1.items()) + list(dict2.items()))
        # Return the merged dictionary
        return merged_dict

@app.route('/addcart', methods=['POST'])
def AddCart():
    try:
        # Get the product ID, quantity, and color from the form data
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        color = request.form.get('colors')
        
        # Get the product object from the database based on the product ID
        product = Addproduct.query.filter_by(id=product_id).first()

        # Check if the request method is POST
        if request.method =="POST":
            # Create a dictionary of the product details
            DictItems = {product_id:{'name':product.name,'price':float(product.price),'discount':product.discount,'color':color,'quantity':quantity,'image':product.image_1, 'colors':product.colors}}
            
            # Check if the shopping cart is already in the session
            if 'Shoppingcart' in session:
                # If the product is already in the shopping cart, increment its quantity
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                # If the product is not already in the shopping cart, add it to the cart
                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            # If the shopping cart is not in the session, create a new cart with the product
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
              
    except Exception as e:
        print(e)
    finally:
        # Redirect the user back to the previous page
        return redirect(request.referrer)

@app.route('/carts')
def getCart():
    # Check if there is a shopping cart in session or if it's empty
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        # Redirect to home page if shopping cart is empty or not found in session
        return redirect(url_for('home'))
    
    # Initialize subtotal and grandtotal to zero
    subtotal = 0
    grandtotal = 0
    
    # Loop through each item in the shopping cart
    for key,product in session['Shoppingcart'].items():
        # Calculate the discount
        discount = (product['discount']/100) * float(product['price'])
        
        # Calculate the subtotal by multiplying the price and quantity of each item, and subtracting the discount
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
        
        # Calculate the tax and format it to two decimal places
        tax =("%.2f" %(.06 * float(subtotal)))
        
        # Calculate the grandtotal by adding the subtotal and tax, and format it to two decimal places
        grandtotal = float("%.2f" % (1.06 * subtotal))
    
    # Render the carts.html template with the tax, grandtotal, brands, and categories
    return render_template('products/carts.html',tax=tax, grandtotal=grandtotal,brands=brands(),categories=categories())



@app.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    # check if there are items in the shopping cart or not
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method =="POST":
        # get the new quantity and color from the form
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            # set session.modified to True to indicate that the session has been modified
            session.modified = True
            # loop through the shopping cart to find the item with the specified code
            for key , item in session['Shoppingcart'].items():
                if int(key) == code:
                    # update the quantity and color of the item
                    item['quantity'] = quantity
                    item['color'] = color
                    flash('Item is updated!')
                    # redirect the user to the shopping cart page
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            # if there is an error, redirect the user to the shopping cart page
            return redirect(url_for('getCart'))


@app.route('/deleteitem/<int:id>')  # define a route for deleting an item from the shopping cart based on its ID
def deleteitem(id):  # define a function to handle the deletion of the item
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:  # check if the shopping cart exists in the session and is not empty
        return redirect(url_for('home'))  # if not, redirect to the home page
    try:  # try to delete the item from the shopping cart
        session.modified = True  # mark the session as modified
        for key , item in session['Shoppingcart'].items():  # iterate over the items in the shopping cart
            if int(key) == id:  # if the item ID matches the ID passed to the function
                session['Shoppingcart'].pop(key, None)  # remove the item from the shopping cart
                return redirect(url_for('getCart'))  # redirect to the shopping cart page
    except Exception as e:  # if an error occurs while deleting the item
        print(e)  # print the error to the console
        return redirect(url_for('getCart'))  # redirect to the shopping cart page


@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None) # remove the 'Shoppingcart' key from the session dictionary
        return redirect(url_for('home')) # redirect the user to the home page
    except Exception as e:
        print(e) # if an error occurs, print it to the console
