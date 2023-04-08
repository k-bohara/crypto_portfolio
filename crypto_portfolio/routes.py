from datetime import datetime
from crypto_portfolio import bcrypt
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, current_user, logout_user
from crypto_portfolio import app
from crypto_portfolio import db
from crypto_portfolio.forms import RegistrationForm, LoginForm
from crypto_portfolio.models import User, Transactions, Coins, Balance
from sqlalchemy import text


@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html', title='Home', user=current_user)


@app.route("/register", methods=['GET', "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account Created', category='success')
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form, user=current_user)


@app.route('/login', methods=['GET', "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('login unsuccessful', category="danger")

    return render_template("login.html", title="Login", form=form, user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/create-portfolio", methods=['GET', 'POST'])
@login_required
def create_portfolio():
    all_coins = Coins.query.all()
    if request.method == 'POST':
        name = request.form.get('coin')
        quantity = request.form.get('quantity')
        txn_type = request.form.get('type')
        price = request.form.get('price')
        date = datetime.strptime(request.form.get('date'), "%Y-%m-%dT%H:%M")
        fee = request.form.get('fee')
        notes = request.form.get('notes')

        coin = Coins.query.filter_by(name=name).first()
        if coin:
            transactions = Transactions(name=name, quantity=quantity, txn_type=txn_type,
                                        price=price, date=date, fee=fee, notes=notes, user_id=current_user.id,
                                        coin_id=coin.id)
            db.session.add(transactions)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('create_portfolio.html', title='Create Portfolio', all_coins=all_coins, user=current_user)


@app.route("/transaction/<username>")
@login_required
def transaction(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found', category='danger')
    transactions = user.transactions
    return render_template('transaction.html', title='Transactions', user=current_user, transactions=transactions,
                           username=username)


@app.route('/update/<transaction_id>', methods=['GET', 'POST'])
@login_required
def update_transaction(transaction_id):
    all_coins = Coins.query.all()
    transaction_log = Transactions.query.filter_by(id=transaction_id).first()
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        date = datetime.strptime(request.form.get('date'), "%Y-%m-%dT%H:%M")
        fee = request.form.get('fee')
        notes = request.form.get('notes')
        transaction_log.quantity = quantity
        transaction_log.price = price
        transaction_log.date = date
        transaction_log.fee = fee
        transaction_log.notes = notes
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('update.html', transaction_log=transaction_log,
                           all_coins=all_coins, title="Update", user=current_user)


@app.route("/delete/<transaction_id>")
@login_required
def delete_transaction(transaction_id):
    transaction_log = Transactions.query.filter_by(id=transaction_id).first()
    if not transaction_log:
        flash('Transaction logs does not exist', category='error')
    elif current_user.id != transaction_log.user_id:
        flash('You do not have permission to delete this transaction log.', category='error')
    else:
        db.session.delete(transaction_log)
        db.session.commit()
    return redirect(url_for('home'))


# determine best performing coin
def best_performer(value):
    return max(value, key=value.get)


@app.route("/portfolio-statistics/<username>")
@login_required
def statistics(username):
    user = User.query.filter_by(username=username).first()
    user_id = user.id

    if not user:
        flash('User not found', category='error')

    #  query for extracting the total amount of coins bought
    sql_1 = text(f"SELECT sum(quantity), name FROM transactions WHERE user_id={user_id} AND txn_type='Buy' GROUP BY "
                 f"name ORDER BY name")
    result = db.engine.execute(sql_1)
    buy = {row[1]: row[0] for row in result}

    #  query for extracting the total amount of coins sold
    sql_2 = text(f"SELECT sum(quantity), name FROM transactions WHERE user_id={user_id} AND txn_type='Sell' GROUP BY "
                 f"name ORDER BY name")
    result2 = db.engine.execute(sql_2)
    sell = {row[1]: row[0] for row in result2}

    # calculating the remaining amount of coins after sale
    coin_quantity = {}
    for coin in buy:
        if coin in sell:
            coin_quantity[coin] = buy[coin] - sell[coin]
        else:
            coin_quantity[coin] = buy[coin]

    coin_name_list = list(coin_quantity.keys())
    coin_quantity_list = list(coin_quantity.values())

    # extracting all the data from the Coins table
    coin = Coins.query.all()

    # extracting current price of coin from Coins table and finding the current value of the coin
    coin_current_price = {}
    coin_current_value = {}
    for name, value in coin_quantity.items():
        for c in coin:
            if name == c.name:
                coin_current_price[c.name] = c.current_price
                coin_current_value[c.name] = c.current_price * value

    # query for extracting total purchase amount and quantity
    sql_3 = text(f"SELECT sum(quantity*price), "
                 f"name FROM transactions WHERE user_id={user_id} AND txn_type='Buy' GROUP  BY name ORDER BY name")
    result3 = db.engine.execute(sql_3)
    total_purchase = {row[1]: row[0] for row in result3}

    # query for extracting average buy price of coins
    sql_4 = text(f"SELECT avg(price), name FROM transactions WHERE  user_id={user_id}  AND  txn_type='Buy' GROUP  BY "
                 f"name ORDER BY name")
    result4 = db.engine.execute(sql_4)
    average_buy_price = {row[1]: row[0] for row in result4}

    # query for extracting total sale amount and quantity
    sql_5 = text(f"SELECT avg(price), name FROM transactions WHERE  user_id={user_id}  AND  txn_type='Sell' GROUP  BY "
                 f"name ORDER BY name")
    result5 = db.engine.execute(sql_5)
    total_sale = {row[1]: row[0] for row in result5}

    #  calculating the value of remaining asset after sale
    coin_value = {}
    for coin in total_purchase:
        if coin in total_sale:
            coin_value[coin] = total_purchase[coin] - total_sale[coin]
        else:
            coin_value[coin] = total_purchase[coin]

    # Current total value of coins
    current_balance = sum(coin_current_value.values())

    # create balance table:
    balance = Balance(current_balance=current_balance,
                      user_id=user_id)
    db.session.add(balance)
    db.session.commit()

    # query to extract current_balance and date from balance table for the particular user
    sql_6 = text(f'SELECT current_balance, date FROM balance where  user_id={user_id}')
    result6 = db.engine.execute(sql_6)

    # balance_details = {row[1]: row[0] for row in result6}
    current_balance_details = []
    current_balance_date = []
    for row in result6:
        current_balance_details.append(row[0])
        current_balance_date.append(datetime.strptime(str(row[1]), "%Y-%m-%d %H:%M:%S.%f").strftime("%A, %b %d, %H:%M"))

    # Total amount invested
    total_amount_invested = sum(total_purchase.values())

    # Total profit/loss
    if total_sale is not None:
        current_value = current_balance - (total_amount_invested - sum(total_sale.values()))
        try:
            current_status = (current_value / total_amount_invested) * 100

        except ZeroDivisionError:
            current_status = 0
    else:
        current_value = current_balance - total_amount_invested
        try:
            current_status = (current_value / total_amount_invested) * 100
        except ZeroDivisionError:
            current_status = 0

    # calculating profit/loss percent
    profit_loss_value = {}
    profit_loss_percent = {}
    for coin_name in coin_current_value:
        profit_loss_value[coin_name] = coin_current_value[coin_name] - coin_value[coin_name]
        try:
            profit_loss_percent[coin_name] = (profit_loss_value[coin_name] / total_purchase[coin_name]) * 100
        except ZeroDivisionError:
            profit_loss_percent[coin_name] = 0

    # best performing coin
    try:
        top_coin = best_performer(profit_loss_value)
    except:
        top_coin = 'Empty'

    return render_template('statistics.html', title='Statistics',
                           profit_loss_value=profit_loss_value,
                           profit_loss_percent=profit_loss_percent,
                           coin_current_price=coin_current_price,
                           coin_current_value=coin_current_value,
                           coin_quantity=coin_quantity,
                           current_balance=current_balance,
                           total_amount_invested=total_amount_invested,
                           current_value=current_value,
                           current_status=current_status, user=current_user,
                           coin=coin, average_buy_price=average_buy_price,
                           coin_name_list=coin_name_list,
                           coin_quantity_list=coin_quantity_list,
                           best=top_coin, current_balance_details=current_balance_details,
                           current_balance_date=current_balance_date)


@app.route("/remove_asset/<coin_name>")
@login_required
def remove_asset(coin_name):
    coin = Coins.query.filter_by(name=coin_name).first()
    transaction_log = Transactions.query.filter_by(coin_id=coin.id).all()
    if transaction_log:
        for transactions in transaction_log:
            db.session.delete(transactions)
            db.session.commit()
    return redirect(url_for('home'))
