import os
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理用の秘密鍵

# デプロイ環境用のデータベースファイルのパスを設定
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'shopping_list_app.db')

def get_db_connection():
    if not os.path.exists(DATABASE_PATH):
        app.logger.error(f"Database file does not exist: {DATABASE_PATH}")
        raise FileNotFoundError(f"Database file does not exist: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                item_quantity INTEGER NOT NULL,
                current_stock INTEGER,
                purchase_deadline TEXT,
                memo TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS purchase_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                item_quantity INTEGER NOT NULL,
                purchase_date TEXT NOT NULL
            )
        ''')
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'tokiyu':
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    shopping_list = conn.execute('SELECT * FROM shopping_list').fetchall()
    purchase_history = conn.execute('SELECT * FROM purchase_history').fetchall()
    conn.close()
    return render_template('index.html', shopping_list=shopping_list, purchase_history=purchase_history)

@app.route('/add', methods=('POST',))
def add():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    item_name = request.form['item_name']
    item_quantity = request.form['item_quantity']
    current_stock = request.form.get('current_stock')
    purchase_deadline = request.form['purchase_deadline']
    memo = request.form['memo']

    if not item_name or not item_quantity:
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO shopping_list (item_name, item_quantity, current_stock, purchase_deadline, memo)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_name, item_quantity, current_stock, purchase_deadline, memo))
        conn.commit()
    except Exception as e:
        conn.rollback()  # ロールバックしてデータベースの一貫性を保つ
        app.logger.error(f"An error occurred: {e}")  # ログにエラーメッセージを出力
        return render_template('error.html', error_message=str(e))  # エラーページを表示
    finally:
        conn.close()

    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM shopping_list WHERE id = ?', (id,)).fetchone()

    if item:
        item_name, item_quantity = item['item_name'], item['item_quantity']
        purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            conn.execute('''
                INSERT INTO purchase_history (item_name, item_quantity, purchase_date)
                VALUES (?, ?, ?)
            ''', (item_name, item_quantity, purchase_date))
            conn.execute('DELETE FROM shopping_list WHERE id = ?', (id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            app.logger.error(f"An error occurred: {e}")
            return render_template('error.html', error_message=str(e))
        finally:
            conn.close()

    return redirect(url_for('index'))

@app.route('/delete_purchase/<int:id>', methods=('POST',))
def delete_purchase(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM purchase_history WHERE id = ?', (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        app.logger.error(f"An error occurred: {e}")
        return render_template('error.html', error_message=str(e))
    finally:
        conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
