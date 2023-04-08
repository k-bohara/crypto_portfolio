# Crypto Portfolio Tracker

Crypto Portfolio Tracker allows you to track your portfolio by creating an account and fill all the details of the transactions and populates summary of the portfolio as portfolio dashboard with graphs.

## Getting Started

$ git clone url

### Sign Up for coinmarketCap API

[CoinmarketCap](https://coinmarketcap.com/api/)

## Create .env file

(venv) $ cp .env.example .env

## Install requirements

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

    (venv) $ flask db init
    (venv) $ flask db migrate
    (venv) $ flask db upgrade

## Run

### Extract coin prices from Coinmarketcap API

    (venv) $ python data.py

### Run the crypto portfolio tracker

    (venv) $ python app.py
