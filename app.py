from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json

mydb = mysql.connector.connect(
# insert your database credentials here
)

cursor = mydb.cursor()
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "secret key"

# inventoryID = None
class Inventory:
    def __init__(self, id, name, quantity, price):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price

class Customer:
    def __init__(self, id, name, address, phone_number):
        self.id = id
        self.name = name
        self.address = address
        self.phone_number = phone_number

class Order:
    def __init__(self, order_id, product_id, customer_id, date, total_price):
        self.order_id = order_id
        self.product_id = product_id
        self.customer_id = customer_id
        self.date = date
        self.total_price = total_price


product_orders_dict = {}
customer_dict = {}

@app.route('/')
def index():
    inventory_list = []
    cursor.execute("SELECT * FROM sys.inventory;")
    result = cursor.fetchall()
    for row in result:
        inventory_list.append(Inventory(row[0], row[1], row[2], float(row[3])))
    print(inventory_list)
    return render_template('index.html', data=inventory_list)

@app.route('/input', methods=['GET', 'POST'])
def input_data():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']

        cursor.execute("INSERT INTO sys.inventory (name, quantity, price) VALUES (%s, %s, %s)", (name, quantity, price))
        mydb.commit()
        flash("Input Data Success", "Success:")

        return redirect(url_for('index'))

    return render_template('input.html')

@app.route('/edit/<int:id>')
def edit_data(id):
    cursor.execute("SELECT * FROM sys.inventory WHERE id = %s", (id,))
    result = cursor.fetchone()
    item = Inventory(result[0], result[1], result[2], float(result[3]))
    return render_template('edit.html', data=item)

@app.route('/process_edit/<int:id>', methods=['POST', 'GET'])
def process_edit(id):
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']

        cursor.execute("UPDATE sys.inventory SET name = %s, quantity = %s, price = %s WHERE id = %s", (name, quantity, price, id))
        mydb.commit()
        flash("Edit Data Success", "Success:")

    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    cursor.execute("DELETE FROM sys.inventory WHERE id = %s", (id,))
    mydb.commit()

    flash('Delete Data Success', "Success:")

    return redirect(url_for('index'))

@app.route('/order/<int:id>')
def order_data(id):
    cursor.execute("SELECT * FROM sys.inventory WHERE id = %s", (id,))
    result = cursor.fetchone()
    item = Inventory(result[0], result[1], result[2], float(result[3]))
    return render_template('order.html', data=item)

@app.route('/process_order/<int:id>', methods=['POST', 'GET'])
def process_order(id):
    if request.method == 'POST':
        # decrease the product quantity if there is enough in stock
        cursor.execute("SELECT id, quantity FROM sys.inventory WHERE id = %s", (id,))
        result = cursor.fetchone()

        product_id = result[0]
        oldQuantity = int(result[1])
        quantity = oldQuantity - int(request.form['quantity'])

        if quantity < 0:
            flash("Not enough products in stock", "Error:")
            return redirect(url_for('index'))

        cursor.execute("UPDATE sys.inventory SET quantity = %s WHERE id = %s", (quantity, id))

        # add the customer information to the customer table
        customer = []
        name = request.form['fname'] + ' ' + request.form['lname']
        customer_id = len(customer_dict) + 1
        customer.append(name)
        customer.append(request.form['address'])
        customer.append(request.form['phone_number'])
        if (customer not in customer_dict.values()):
            customer_dict[customer_id] = customer
        else:
            for index, cust in customer_dict.items():
                if cust == customer:
                    customer_id = index

        # add the order information to the order table
        product_order = []
        order_id = len(product_orders_dict) + 1
        product_order.append(product_id)
        product_order.append(customer_id)
        product_order.append(request.form['order_date'])
        product_order.append(request.form['total_price'])
        product_orders_dict[order_id] = product_order

        mydb.commit()
        flash("Order Success", "Success:")

    return redirect(url_for('index'))

@app.route('/customers')
def customers():
    customer_list = []

    for index, customer in customer_dict.items():
        customer_list.append(Customer(index, customer[0], customer[1], customer[2]))

    print(customer_list)
    return render_template('customers.html', data=customer_list)
    
@app.route('/product_orders')
def product_orders():
    order_list = []

    for index, prodOrder in product_orders_dict.items():
        print((index, prodOrder[0], prodOrder[1], prodOrder[2], float(prodOrder[3])))
        order_list.append(Order(index, prodOrder[0], prodOrder[1], prodOrder[2], float(prodOrder[3])))

    print(order_list)
    return render_template('product_orders.html', data=order_list)

if __name__ == '__main__':
    app.run(debug=True)