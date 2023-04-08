# Crypto Portfolio Tracker

Crypto Portfolio Tracker allows you to track your portfolio by creating an account and fill all the details of the transactions and populates summary of the portfolio as portfolio dashboard with graphs.

**You need Python 3.8 or above and PostgreSQL for this project.**

## Getting Started

Clone the repo

      $ git clone https://github.com/k-bohara/crypto_portfolio.git

Sign Up for [coinmarketCap API](https://coinmarketcap.com/api/) and get the api key.

## Create .env file

      $ cp .env.example .env

Insert your postgres database credentials and coinmarketcap API appropriately.

## Install requirements

Install and create virtualenv

      $ sudo pip3 install virtualenv
      $ virtualenv venv
      $ source venv/bin/activate
      (venv) $

Now install requirements in venv

      (venv) $ pip install -r requirements.txt

## Database

### Create a database and initialize .env file accordingly

### To run psql commandline interface in admin mode

      $ sudo -u postgres psql

### Creating database

      postgres=# create database <dbname>;

### Creating user and giving user password

      postgres=# create user <username> with encrypted password ''<password>'';

### Granting privileges on database

      postgres=# grant all privileges on database <dbname> to <username>;

Now exit the psotgres shell and go back to terminal to create tables.

Flask-Migrate handles create database tables using the below commands.

    (venv) $ flask db init
    (venv) $ flask db migrate
    (venv) $ flask db upgrade

## Run

First you need to fetch some prices from coinmarket cap api using the fetch_price.py script.

    (venv) $ python fetch_price.py

Now run the web app

    (venv) $ python app.py

Visit http://127.0.0.1:5000 to see the website. Create a user to add crypto currencies and create portfolio.

### Demo Screenshots

### Transactions

![index](/screenshots/transactions.png)

#### Dashboard

![index](/screenshots/dashboard.png)

More screenshots available inside `screenshots` directory
