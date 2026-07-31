import sqlite3
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

from query_functions import (
    setup,
    customer_query,
    product_query,
    location_query,
    employee_query,
    forecast,
    update,
    delete,
)
from insertion import insert_records_orders

app = Flask(__name__)

# Frontend origin is GitHub Pages, backend is pythonanywhere

CORS(app)

DB_PATH = "./quickcast.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


#helper functions for easier data conversions

def rows_to_dicts(rows, key_a, key_b):
    return [{key_a: r[0], key_b: r[1]} for r in rows]


def divide_cents(dicts, value_key):
    for d in dicts:
        if d[value_key] is not None:
            d[value_key] = d[value_key] / 100
    return dicts


def is_currency_agg(agg, sale_profit_param):
    return sale_profit_param in ("sales", "profit") and agg.upper() != "COUNT"

#These columns are what are checked in an uploaded csv, these are the same as the guest dataset columns

UPLOAD_COLUMNS = [
    "Row ID", "Order ID", "Order Date", "Customer ID", "Customer Name",
    "Country", "City", "State", "Postal Code", "Retail Sales People",
    "Product ID", "Category", "Sub-Category", "Product Name",
    "Returned", "Sales", "Quantity", "Discount", "Profit",
]


@app.route("/api/upload", methods=["POST"])
def api_upload():
    username = request.form.get("username", "").strip()
    if not username:
        return jsonify({"error": "username is required"}), 400

    file = request.files.get("file")
    if file is None or file.filename == "":
        return jsonify({"error": "csv file is required"}), 400

    try:
        df = pd.read_csv(file, encoding="latin1")
    except Exception as e:
        return jsonify({"error": f"could not read CSV: {e}"}), 400

    missing = [c for c in UPLOAD_COLUMNS if c not in df.columns]
    if missing:
        return jsonify({"error": f"CSV missing required columns: {', '.join(missing)}"}), 400

    df = df[UPLOAD_COLUMNS].copy()
    
    df["Returned"] = df["Returned"].replace({"Not": 0, "Yes": 1})

    conn = get_conn()
    cur = conn.cursor()

    #checks to see if the user already exists
    existing = cur.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": f'username "{username}" is already taken'}), 409

    #inserts the user uploaded data
    try:
        new_user_id = insert_records_orders(cur=cur, df=df, username=username, password="")
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

    conn.close()
    return jsonify({"user_id": new_user_id, "username": username})

@app.route("/api/customers")
def api_customers():
    user_id = request.args.get("user_id", type=int)
    name = request.args.get("name", "true").lower() == "true"
    limit = request.args.get("limit", 10, type=int)
    order = request.args.get("order", "DESC")
    agg = request.args.get("agg", "COUNT")
    sale_profit_param = request.args.get("sale_profit", "off")
    sale_profit_col = sale_profit_param if sale_profit_param in ("sales", "profit") else False

    #sets up for the customer query and performs it

    conn = get_conn()
    cur = conn.cursor()
    setup(cur, user_id)
    rows = customer_query(cur, name=name, limit=limit, order=order, agg=agg, sale_profit=sale_profit_col)
    conn.close()

    data = rows_to_dicts(rows, "label", "value")
    if is_currency_agg(agg, sale_profit_param):
        data = divide_cents(data, "value")
    return jsonify(data)


@app.route("/api/products")
def api_products():
    user_id = request.args.get("user_id", type=int)
    name = request.args.get("name", "true").lower() == "true"
    limit = request.args.get("limit", 10, type=int)
    order = request.args.get("order", "DESC")
    agg = request.args.get("agg", "COUNT")
    sale_profit_param = request.args.get("sale_profit", "off")
    sale_profit_col = sale_profit_param if sale_profit_param in ("sales", "profit") else False

    #sets up for the products query and performs it

    conn = get_conn()
    cur = conn.cursor()
    setup(cur, user_id)
    rows = product_query(cur, name=name, limit=limit, order=order, agg=agg, sale_profit=sale_profit_col)
    conn.close()

    data = rows_to_dicts(rows, "label", "value")
    if is_currency_agg(agg, sale_profit_param):
        data = divide_cents(data, "value")
    return jsonify(data)


@app.route("/api/locations")
def api_locations():
    user_id = request.args.get("user_id", type=int)
    limit = request.args.get("limit", 10, type=int)
    order = request.args.get("order", "DESC")
    agg = request.args.get("agg", "COUNT")
    level = request.args.get("level", "city")

    #sets up the locations query and performs it

    conn = get_conn()
    cur = conn.cursor()
    setup(cur, user_id)
    rows = location_query(cur, limit=limit, order=order, agg=agg, level=level)
    conn.close()

    data = rows_to_dicts(rows, "label", "value")
    return jsonify(data)


@app.route("/api/employees")
def api_employees():
    user_id = request.args.get("user_id", type=int)
    name = request.args.get("name", "true").lower() == "true"
    limit = request.args.get("limit", 10, type=int)
    order = request.args.get("order", "DESC")
    agg = request.args.get("agg", "COUNT")
    sales_profit_param = request.args.get("sales_profit", "off")
    sales_profit_col = sales_profit_param if sales_profit_param in ("sales", "profit") else False

    #sets up the employee query and performs it

    conn = get_conn()
    cur = conn.cursor()
    setup(cur, user_id)
    rows = employee_query(cur, name=name, limit=limit, order=order, agg=agg, sales_profit=sales_profit_col)
    conn.close()

    data = rows_to_dicts(rows, "label", "value")
    if is_currency_agg(agg, sales_profit_param):
        data = divide_cents(data, "value")
    return jsonify(data)


@app.route("/api/forecast")
def api_forecast():
    user_id = request.args.get("user_id", type=int)
    name_chosen = request.args.get("name_chosen")
    product_name = request.args.get("product_name", "true").lower() == "true"

    #sets up the forecast query and performs it

    conn = get_conn()
    cur = conn.cursor()
    setup(cur, user_id)
    rows = forecast(cur, name_chosen, product_name=product_name)
    conn.close()

    data = rows_to_dicts(rows, "month", "quantity")
    return jsonify(data)


@app.route("/api/order/<int:row_id>")
def api_get_order(row_id):
    conn = get_conn()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT row_id, quantity, sales, discount, profit, returned FROM orders WHERE row_id = ?",
        (row_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": f"no order with row_id {row_id}"}), 404

    #grabs the values from the database to fill the front end values for easier editing

    return jsonify({
        "row_id": row[0],
        "quantity": row[1],
        "sales": row[2] / 100,
        "discount": row[3] / 100,
        "profit": row[4] / 100 if row[4] is not None else None,
        "returned": row[5],
    })


@app.route("/api/order/<int:row_id>", methods=["POST"])
def api_update_order(row_id):

    #checks the database for the row, and if it exists, uses the update function to update the row

    data = request.get_json(silent=True) or {}
    try:
        quantity = int(data["quantity"])
        sales = float(data["sales"])
        discount = float(data["discount"])
        profit = float(data["profit"])
        returned = int(data["returned"])
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"error": f"invalid or missing field: {e}"}), 400

    if returned not in (0, 1):
        return jsonify({"error": "returned must be 0 or 1"}), 400

    conn = get_conn()
    cur = conn.cursor()

    exists = cur.execute("SELECT 1 FROM orders WHERE row_id = ?", (row_id,)).fetchone()
    if not exists:
        conn.close()
        return jsonify({"error": f"no order with row_id {row_id}"}), 404

    try:
        update(cur, row_id, quantity, sales, discount, profit, returned)
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

    conn.close()
    return jsonify({"row_id": row_id, "status": "updated"})

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):

    #checks to see if the user is the guest user

    if user_id == 1:
        return jsonify({"error": "the seeded Guest account (user_id 1) can't be deleted"}), 403

    conn = get_conn()
    cur = conn.cursor()

    #if the user exists, uses the delete function and deletes the user records

    exists = cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not exists:
        conn.close()
        return jsonify({"error": f"no user with user_id {user_id}"}), 404

    try:
        delete(cur, user_id)
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

    conn.close()
    return jsonify({"user_id": user_id, "status": "deleted"})

#runs the app and uses non-debug mode to ensure security

if __name__ == "__main__":
    app.run(port=5000, debug=False)
