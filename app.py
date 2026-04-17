from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'shop.db'

# สร้างการเชื่อมต่อกับฐานข้อมูล
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# สร้างตารางหากยังไม่มี
def create_tables():
    sql_create_categories = '''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    '''

    sql_create_products = '''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        image_url TEXT,
        price REAL NOT NULL,
        size TEXT,
        stock INTEGER NOT NULL,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    );
    '''

    conn = get_db_connection()
    try:
        conn.execute(sql_create_categories)
        conn.execute(sql_create_products)
        conn.commit()
    except Error as e:
        print('Error creating tables:', e)
    finally:
        conn.close()

# เติม category ตัวอย่าง
def insert_default_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    if len(categories) == 0:
        conn.execute('INSERT INTO categories (name) VALUES (?)', ('เสื้อ',))
        conn.execute('INSERT INTO categories (name) VALUES (?)', ('กางเกง',))
        conn.commit()
    conn.close()

@app.route('/')
def product_list():
    conn = get_db_connection()
    products = conn.execute(
        'SELECT products.*, categories.name AS category_name '
        'FROM products LEFT JOIN categories ON products.category_id = categories.id'
    ).fetchall()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return render_template('product_list.html', products=products, categories=categories)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    if request.method == 'POST':
        name = request.form['name']
        image_url = request.form['image_url']
        price = request.form['price']
        size = request.form['size']
        stock = request.form['stock']
        category_id = request.form['category_id']

        if not name or not price or not stock:
            flash('กรุณากรอกชื่อ ราคา และ จำนวน stock')
            return render_template('add_product.html', categories=categories)

        conn.execute(
            'INSERT INTO products (name, image_url, price, size, stock, category_id) VALUES (?, ?, ?, ?, ?, ?)',
            (name, image_url, float(price), size, int(stock), int(category_id) if category_id else None)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('product_list'))

    conn.close()
    return render_template('add_product.html', categories=categories)

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    categories = conn.execute('SELECT * FROM categories').fetchall()

    if product is None:
        conn.close()
        return redirect(url_for('product_list'))

    if request.method == 'POST':
        name = request.form['name']
        image_url = request.form['image_url']
        price = request.form['price']
        size = request.form['size']
        stock = request.form['stock']
        category_id = request.form['category_id']

        if not name or not price or not stock:
            flash('กรุณากรอกชื่อ ราคา และ จำนวน stock')
            return render_template('edit_product.html', product=product, categories=categories)

        conn.execute(
            'UPDATE products SET name = ?, image_url = ?, price = ?, size = ?, stock = ?, category_id = ? WHERE id = ?',
            (name, image_url, float(price), size, int(stock), int(category_id) if category_id else None, product_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('product_list'))

    conn.close()
    return render_template('edit_product.html', product=product, categories=categories)

@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('product_list'))

if __name__ == '__main__':
    create_tables()
    insert_default_categories()
    app.run(debug=True)
