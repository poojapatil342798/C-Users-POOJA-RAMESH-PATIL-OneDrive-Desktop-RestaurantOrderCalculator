
from flask import Flask, render_template, request
from datetime import datetime
import sqlite3
import uuid
import os

# Project folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATABASE = os.path.join(BASE_DIR, "restaurant.db")

# Configure Flask folders
app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

# Restaurant menu and prices
MENU = {
    "burger": {"name": "Veg Burger", "price": 80},
    "pizza": {"name": "Pizza", "price": 150},
    "sandwich": {"name": "Sandwich", "price": 60},
    "fries": {"name": "French Fries", "price": 70},
    "juice": {"name": "Fresh Juice", "price": 50}
}


# Create database tables
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_number TEXT PRIMARY KEY,
                order_date TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                total REAL NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL,
                item_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (order_number)
                    REFERENCES orders(order_number)
            )
        """)


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Calculate bill and save order
@app.route("/calculate", methods=["POST"])
def calculate():
    customer_name = request.form.get(
        "customer_name", ""
    ).strip()

    phone = request.form.get("phone", "").strip()

    if not customer_name:
        return "Please enter the customer's name.", 400

    if not phone.isdigit() or len(phone) != 10:
        return "Enter a valid 10-digit phone number.", 400

    order = []
    total = 0

    for key, item in MENU.items():
        try:
            quantity = int(request.form.get(key, 0))

            if quantity < 0:
                return "Quantity cannot be negative.", 400

        except (ValueError, TypeError):
            return "Enter valid whole-number quantities.", 400

        if quantity > 0:
            subtotal = quantity * item["price"]

            order.append({
                "name": item["name"],
                "price": item["price"],
                "quantity": quantity,
                "subtotal": subtotal
            })

            total += subtotal

    if not order:
        return "Please select at least one food item.", 400

    # Generate order number and date/time
    order_number = (
        "ORD-"
        + datetime.now().strftime("%Y%m%d")
        + "-"
        + uuid.uuid4().hex[:6].upper()
    )

    order_date = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    # Save order details in SQLite
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            INSERT INTO orders
            (order_number, order_date, customer_name, phone, total)
            VALUES (?, ?, ?, ?, ?)
        """, (
            order_number,
            order_date,
            customer_name,
            phone,
            total
        ))

        for item in order:
            conn.execute("""
                INSERT INTO order_items
                (order_number, item_name, price, quantity, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (
                order_number,
                item["name"],
                item["price"],
                item["quantity"],
                item["subtotal"]
            ))

    return render_template(
        "result.html",
        order=order,
        total=total,
        customer_name=customer_name,
        phone=phone,
        order_number=order_number,
        order_date=order_date
    )


# Display all saved orders
@app.route("/orders")
def order_history():
    with sqlite3.connect(DATABASE) as conn:
        orders = conn.execute("""
            SELECT order_number, order_date,
                   customer_name, phone, total
            FROM orders
            ORDER BY rowid DESC
        """).fetchall()

    return render_template("orders.html", orders=orders)


# View an individual saved order
@app.route("/order/<order_number>")
def view_order(order_number):
    with sqlite3.connect(DATABASE) as conn:
        saved_order = conn.execute("""
            SELECT order_number, order_date,
                   customer_name, phone, total
            FROM orders
            WHERE order_number = ?
        """, (order_number,)).fetchone()

        if saved_order is None:
            return "Order not found.", 404

        saved_items = conn.execute("""
            SELECT item_name, price, quantity, subtotal
            FROM order_items
            WHERE order_number = ?
            ORDER BY id
        """, (order_number,)).fetchall()

    order_items = []

    for item in saved_items:
        order_items.append({
            "name": item[0],
            "price": item[1],
            "quantity": item[2],
            "subtotal": item[3]
        })

    return render_template(
        "result.html",
        order=order_items,
        total=saved_order[4],
        customer_name=saved_order[2],
        phone=saved_order[3],
        order_number=saved_order[0],
        order_date=saved_order[1]
    )


# Restaurant dashboard
@app.route("/dashboard")
def dashboard():
    with sqlite3.connect(DATABASE) as conn:
        summary = conn.execute("""
            SELECT COUNT(*),
                   COALESCE(SUM(total), 0),
                   COALESCE(AVG(total), 0)
            FROM orders
        """).fetchone()

        recent_orders = conn.execute("""
            SELECT order_number, order_date,
                   customer_name, total
            FROM orders
            ORDER BY rowid DESC
            LIMIT 5
        """).fetchall()

    chart_orders = list(reversed(recent_orders))

    chart_labels = [
        order[0][-6:] for order in chart_orders
    ]

    chart_values = [
        order[3] for order in chart_orders
    ]

    return render_template(
        "dashboard.html",
        total_orders=summary[0],
        total_sales=summary[1],
        average_bill=summary[2],
        recent_orders=recent_orders,
        chart_labels=chart_labels,
        chart_values=chart_values
    )


# Run the application
if __name__ == "__main__":
    init_db()

    print("Project folder:", BASE_DIR)
    print("Static folder:", STATIC_DIR)
    print(
        "CSS file exists:",
        os.path.isfile(os.path.join(STATIC_DIR, "style.css"))
    )

    app.run(debug=True)
