# -*- coding: UTF-8 -*-
import os
import uuid
import settings
from flask import Flask, g, render_template, request, jsonify, url_for, send_file, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
from distutils.util import strtobool
##from models import db_session, User, Cloth, Category, OrderCloth


app = Flask(__name__, template_folder="templates")

app.config['SECRET_KEY'] = settings.SECRET_KEY

app.config['SECRET_KEY'] = str(uuid.uuid4())
manager = LoginManager(app)


@app.route('/registration/', methods = ['GET', 'POST'])
def register():
    from models import db_session, User
    if request.method == 'GET':
        return render_template('registration.htm')
    elif request.method == 'POST':
       surname = request.form.get('surname')
       name = request.form.get('name')
       phone = request.form.get('phone')
       address = request.form.get('address')
       email = request.form.get('email')
       password = request.form.get('password')
       new_user = User(surname = surname, name = name, phone = phone, address = address, email = email, password = password)
       db_session.add(new_user)
       db_session.commit()
       login_user(new_user)
       return redirect(url_for('woman'))
       return render_template('woman.htm')

@app.route("/login/", methods=['GET', 'POST'])
def login():
    from models import db_session, User
    username = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=username).first()
    if user and user.password == password:
        login_user(user)
        return redirect(url_for('woman', page_name='index'))  # Измените на вашу главную страницу
    else:
        return render_template('login.htm', error='Invalid username or password')
    return render_template("login.htm")

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('woman'))

@manager.user_loader
def load_user(id):
    from models import User
    return User.query.get(id)

@app.route("/<page_name>/")
def main(page_name):
    return render_template(page_name + ".htm")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.htm"), 404

@app.route('/woman/')
def woman():
    from models import db_session, Cloth, Category
    data = db_session.query(Cloth).filter(Cloth.sex == 0)
    data2 = db_session.query(Category).all()
    return render_template("woman.htm", page_name = "Woman", categories = data2, clothes = data)

@app.route('/man/')
def man():
    from models import db_session, Cloth, Category
    data = db_session.query(Cloth).filter(Cloth.sex == 1)
    data2 = db_session.query(Category).all()
    return render_template("man.htm", page_name = "Man", categories = data2, clothes = data)

@app.route('/account/')
def account():
    from models import db_session, User
    data = db_session.query(User).all()
    return render_template("account.htm", page_name = "Account", user = data)

@app.route("/clothes/<int:id>/")
def clothes(id):
    from models import db_session, Cloth
    data = db_session.query(Cloth).filter(Cloth.id == id).first()
    return render_template("clothes.htm", cloth=data)

@app.route("/woman/<int:id>/")
def woman_category(id):
    from models import db_session, Cloth, Category
    data = db_session.query(Cloth).filter(Cloth.sex == 0, Cloth.category_type == id)
    data2 = db_session.query(Category).all()
    return render_template("woman.htm", page_name = "Woman", categories = data2, clothes = data)

@app.route("/man/<int:id>/")
def man_category(id):
    from models import db_session, Cloth, Category
    data = db_session.query(Cloth).filter(Cloth.sex == 1, Cloth.category_type == id)
    data2 = db_session.query(Category).all()
    return render_template("man.htm", page_name = "Man", categories = data2, clothes = data)

@app.route("/add/")
def add():
    from models import db_session, Cloth, OrderCloth
    cloth_id = request.args.get("id")
    user_id = current_user.id
    existing = db_session.query(OrderCloth).filter(OrderCloth.cloth_id == cloth_id).first()

    if existing:
        pass
    else:
        cloth = db_session.query(Cloth).filter(Cloth.id == cloth_id).first()
        new_pos = OrderCloth(cloth_id=cloth_id, total=cloth.price, quantity = 1)
        db_session.add(new_pos)
        db_session.commit()
    return redirect(request.referrer)

@app.route("/cart/")
def cart():
    from models import db_session, Cloth, OrderCloth, Shop
    shops = db_session.query(Shop).all()
    cart = db_session.query(OrderCloth).all()
    total = sum(cloth.total for cloth in cart)
    return render_template("cart.htm", cart=cart, total=total, shops=shops)

@app.route("/cart/", methods=['POST'])
def cart_order():
    from models import db_session, Cloth, OrderCloth, Shop, Order
    if request.method == 'POST':
        order_type = strtobool(request.form.get('type'))
        order_address = request.form.get('address')
        name = request.form.get('name')
        order_date_str = request.form.get('order_date')
        order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()

        cart = db_session.query(OrderCloth).all()
        total = sum([cloth.cloth.price * cloth.quantity for cloth in cart])

        new_order = Order(order_type=order_type, order_address=order_address, order_date=order_date, total=total)

        db_session.add(new_order)
        db_session.flush()
        db_session.query(OrderCloth).delete()
        db_session.commit()
    return redirect(url_for("woman"))

@app.route("/remove/<int:id>", methods=['POST'])
def remove(id):
    from models import db_session, Cloth, OrderCloth
    cloth = db_session.query(OrderCloth).filter(OrderCloth.cloth_id == id).first()
    db_session.delete(cloth)
    db_session.commit()
    return redirect(url_for('cart'))

@app.route("/change_quantity/<int:id>", methods=['POST'])
def change_quantity(id):
    from models import db_session, OrderCloth
    cart = db_session.query(OrderCloth).filter(OrderCloth.cloth_id == id).first()
    new_quantity = int(request.form[f'quantity_{ id }'])
##    data = request.get_json()
##    new_quantity = int(data['newQuantity'])
    new_total = new_quantity * cart.cloth.price

    if cart:
        cart.quantity = new_quantity
        cart.total = new_total
        db_session.commit()
        return redirect(url_for('cart'))

##@app.after_request
##def redirect_to_sign(response):
##    if response.status_code == 401:
##        return redirect(url_for('register'))
##    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5057, debug=True)
