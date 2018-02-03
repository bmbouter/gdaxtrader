# GDAX Trader
Automated and manual cryptocurrency trading on the GDAX exchange without fees.

!DANGER!

You could loose money. Use `gdaxtrader` at your own risk! I do not accept any responsibility for any
losses.

Gdaxtrader is Alpha quality! Use at your own risk.


# Features

* Supports: Bitcoin, Ethereum, Litecoin, and Bitcoin Cash

* Avoid fees. Avoids fees by ensuring all orders are "market maker" orders. See more on
  [Avoiding Fees].

* Multiple Funds within one GDAX account. All manual or bot trading is associated with a Fund which
  is a certain amount of value (USD, BTC, ETH, LTC, BCH) and a history of trades. Manual and bot
  trades cannot spend more than is in the Fund.

* Manual trading with buy/sell orders. These are "market maker" orders versus the GDAX web interface
  which only places "market taker" orders.

* [Experimental] Market Maker Bot. An automated trading strategy described
  [here](https://en.wikipedia.org/wiki/Market_maker) and also some in this crypto automated trading
  video on youtube [here](https://www.youtube.com/watch?v=b-8ciz6w9Xo).


# Installation

`gdaxtrader` is a Django app, but it only uses the Django ORM and the Django management commands.
Below is the minimal install info, for a complete guide see the full install.

## Install the app

Install the library from pip:

`pip install gdaxtrader`

Install the library from source:

`pip install develop`

## Enable the app

Once installed, enable it in your Django's settings.py file by adding an entry like:

```
INSTALLED_APPS = [
    ...
    'gdaxtrader',
    ...
]
```

## Apply the migrations

`gdaxtrader` uses the Django database, so apply the database migrations with:

`python manage.py migrate gdaxtrader`


## Configure the credentials

Set your API credentials as environment variables. Create a file with the following contents:

```
#! /usr/bin/bash
export GDAX_KEY='...'
export GDAX_B64SECRET='...'
export GDAX_PASSPHRASE='...'
```

Assuming your file is called `my_secrets.sh`, you can load those variables into your environment
using: `source my_secrets.sh`.


# Quick Start

## Create a Fund

1. Transfer some funds into your GDAX wallet. You can "deposit" a variety of ways through the web
interface.

2. Create a "Fund" in the system, which is a specific amount of a variety of currencies (USD,ETC,
BTC, etc). For example create a Fund with $30 USD by starting a django-aware shell with
`python manage.py shell` and running:

```python
>>> from gdaxtrader.models import Fund
>>> my_fund = Fund(name="Test Fund", usd_balance=30)
>>> my_fund.save()
```

### Viewing a Fund's value

As orders associated with a `Fund` are completed the value as measured in various currencies
chages. View the current state of the Fund, including it's current value and any associated and
unfilled buy or sell orders. View a fund by running:

`python manage.py orders`

You should see output like:

```
(gdaxtrader) [bmbouter@localhost cryptosite]$ python manage.py orders

Fund "Test Fund": USD=30.000000000000:
No Open Orders
```

### Trading

A few rules should always true withing the system:

* All trades come in the form of a buy or sell order and are represented in the database as a
`BuyOrder` or `SellOrder` respectively.

* All orders must be associated with a `Fund`. Orders not associated with a `Fund` won't save in
the database.

* Outstanding orders are called 'unfilled'.

* All unfilled orders encumber the corresponding amount of value from the `Fund`. This prevents
additional trades from using that same currency twice for another buy or sell order. For each
currency, a `Fund` has an available and a total value. Each currency is the total value minus
encumbered value.

* Prior to placing an order, all orders are checked that the corresponding `Fund` has enough
available currency to place the order.

* As orders are 'filled' they update the associated `Fund`'s available and total currency values.


### Manual Trading

# Buy Orders

Place a buy order to purchase $15 worth of Ethereum at a price of $1161.

`python manage.py buy --coin ETH --buy-price 1161 --amount 15 --fund 'Test Fund'`

For buy orders, the `--amount` is always in USD. See all the options with
`python manage.py buy --help`.

# Sell Orders

Plae a sell order to sell 0.04271681 of Bitcoin at a sell price of $16507.19.

`python manage.py sell --coin BTC --sell-price 16507.19 --amount 0.04271681 --fund 'Test Fund'`

For sell orders, the `--amount` is always in the units being sold. See all the options with
`python manage.py sell --help`.

# Report a Bug

Please report issues here: https://github.com/bmbouter/gdaxtrader/issues

# Avoiding Fees

GDAX maintains an order book with buy and sell orders in it. For example it could be an order to buy
0.01 BTC at 100 USD. For any newly placed order GDAX receives, it tries to fill it against the
existing order book. If it can be filled the transaction occurs immediately, if it can't the order
is added to the order book.

An order that is placed but is never put onto the order book is a "market taker" in the sense that
it is taking an order off of the order book which decreases liquidity. An order that is placed and
ends up being added to the order book is a "market maker" order because it is increasing liquidity.
[GDAX fees](https://www.gdax.com/fees) are only paid entirely by the "market taker", while the
"market maker" pays no fees.

`gdaxtrader` avoids fees by looking at the order book and making sure there is always an existing
order on the book that is more attractive. For a new buy order, the price per currency needs to be
lower than the highest buy order on the book already. For a new sell order, the price per currency
needs to be higher than the lowest sell order on the book already.

The manual trading commands and the bots all adhere to a no-fees-for-all-trades rule. Many of the
commands and bots had options to disable override this behavior.

Note that during times of high volume trading it is possible to incur fees. Specifically in between
the time the order book is checked and `gdaxtrader` places the new order on GDAX, the order book
could have changed such that the new order, unexpectedly, is the "market taker". In practice, this
happens very rarely.
