This page is a step-by-step setup guide to setup `gdaxtrader` from scratch. It includes to setup
and deployment of a Django site on top of an sqlite database.


## Requirements

You'll need to have the following things already installed:
* Python 3, at least 3.5
* pip


## Create a virtualenv and activate it

```
python3 -m venv gdaxtrader
source gdaxtrader/bin/activate
```

You should see your terminal show `(gdaxtrader)` in it like:

`(gdaxtrader) [bmbouter@localhost ~]$`


## Verify your Python version is at least Python 3.5

```
(gdaxtrader) [bmbouter@localhost ~]$ python --version
Python 3.6.3
```


## Install the `gdaxtrader` application

`pip install gdaxtrader`


## Create your Django site

I call mine cryptosite

`django-admin startproject cryptosite`

## Enable the gdaxtrader application in your Django site

Using your favorite text editor add the `gdaxtrader` entry to `cryptosite/cryptosite/settings.py`

```
INSTALLED_APPS = [
    ...
    'gdaxtrader',
    ...
]
```

## Create the database

```
cd gdaxtrader
python manage.py migrate
```

## Configure your credentials

Create a file named `gdax_credentials.sh` with `touch gdax_credentials.sh`. Add the following
contents to the file:

```
export GDAX_KEY='...'
export GDAX_B64SECRET='...'
export GDAX_PASSPHRASE='...'
```

Then export these variables into your environment for `gdaxtrader` to user them with:

`source gdax_credentials.sh`
