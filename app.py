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
        flash("Input Data Success")

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
        flash("Edit Data Success")

    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    cursor.execute("DELETE FROM sys.inventory WHERE id = %s", (id,))
    mydb.commit()

    flash('Delete Data Success')

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
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']

        # cursor.execute("UPDATE sys.inventory SET name = %s, quantity = %s, price = %s WHERE id = %s", (name, quantity, price, id))
        # mydb.commit()
        # flash("Order Success")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)