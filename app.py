from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

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
    cursor.execute('PRAGMA table_info(products)')
    columns = [column[1] for column in cursor.fetchall()]
    if 'position' not in columns:
        cursor.execute('ALTER TABLE products ADD COLUMN position INTEGER DEFAULT 0')
        cursor.execute('UPDATE products SET position = id')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY position')
    products = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
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
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/get_product/<int:id>', methods=['GET'])
def get_product(id):
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
    app.run(debug=True)
