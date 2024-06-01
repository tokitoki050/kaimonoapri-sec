import os
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from data_manager import load_data, save_data

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理用の秘密鍵

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
    data = load_data()
    shopping_list = data['shopping_list']
    purchase_history = data['purchase_history']
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
        data = load_data()
        data['shopping_list'].append({
            "id": len(data['shopping_list']) + 1,
            "item_name": item_name,
            "item_quantity": item_quantity,
            "current_stock": current_stock,
            "purchase_deadline": purchase_deadline,
            "memo": memo
        })
        save_data(data)
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")  # ログにエラーメッセージを出力
        return render_template('error.html', error_message=str(e))  # エラーページを表示

    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        data = load_data()
        item = next((item for item in data['shopping_list'] if item['id'] == id), None)
        if item:
            purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data['purchase_history'].append({
                "id": len(data['purchase_history']) + 1,
                "item_name": item['item_name'],
                "item_quantity": item['item_quantity'],
                "purchase_date": purchase_date
            })
            data['shopping_list'] = [i for i in data['shopping_list'] if i['id'] != id]
            save_data(data)
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return render_template('error.html', error_message=str(e))

    return redirect(url_for('index'))

@app.route('/delete_purchase/<int:id>', methods=('POST',))
def delete_purchase(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        data = load_data()
        data['purchase_history'] = [i for i in data['purchase_history'] if i['id'] != id]
        save_data(data)
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return render_template('error.html', error_message=str(e))

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
