import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sOjyXr849M1hFIW219XGIa1AICizBd5Q4wrwDP3'

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            image TEXT NOT NULL,
            price REAL NOT NULL,
            units INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            position INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('PRAGMA table_info(products)')
    columns = [column[1] for column in cursor.fetchall()]
    if 'position' not in columns:
        cursor.execute('ALTER TABLE products ADD COLUMN position INTEGER DEFAULT 0')
        cursor.execute('UPDATE products SET position = id')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY position')
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Account created successfully')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
        conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    data = request.get_json()
    name = data['name']
    image = data['image']
    price = data['price']
    units = data['units']
    unit_price = data['unit_price']
    position = data['position']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name, image, price, units, unit_price, position)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, image, price, units, unit_price, position))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})

@app.route('/update_product/<int:id>', methods=['POST'])
def update_product(id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    data = request.get_json()
    name = data['name']
    image = data['image']
    price = data['price']
    units = data['units']
    unit_price = data['unit_price']
    position = data['position']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE products
        SET name = ?, image = ?, price = ?, units = ?, unit_price = ?, position = ?
        WHERE id = ?
    ''', (name, image, price, units, unit_price, position, id))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})

@app.route('/delete_product/<int:id>', methods=['DELETE'])
def delete_product(id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/get_product/<int:id>', methods=['GET'])
def get_product(id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (id,))
    product = cursor.fetchone()
    conn.close()
    if product:
        return jsonify({
            'id': product[0],
            'name': product[1],
            'image': product[2],
            'price': product[3],
            'units': product[4],
            'unit_price': product[5],
            'position': product[6]
        })
    return jsonify({'status': 'error', 'message': 'Product not found'}), 404

@app.route('/reorder_products', methods=['POST'])
def reorder_products():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    data = request.get_json()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    for position, product_id in enumerate(data):
        cursor.execute('''
            UPDATE products
            SET position = ?
            WHERE id = ?
        ''', (position, product_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/print')
def print_page():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY position')
    products = cursor.fetchall()
    conn.close()
    return render_template('print.html', products=products)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
