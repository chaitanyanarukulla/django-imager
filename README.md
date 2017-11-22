# django-imager

[![Build Status](https://travis-ci.org/chaitanyanarukulla/django-imager.svg?branch=master)](https://travis-ci.org/chaitanyanarukulla/django-imager)
[![Coverage Status](https://coveralls.io/repos/github/chaitanyanarukulla/django-imager/badge.svg)](https://coveralls.io/github/chaitanyanarukulla/django-imager)

**Author**: Megan Flood and Chaitanya Naru

**Version**: 1.0.0

## Overview
A simple image management website using Django.

## Routes
| Route | Name | Description |
|:--|--|:--|


## Getting Started

Clone this repository to your local machine.
```
$ git clone https://github.com/chaitanyanarukulla/django-imager.git
```

Once downloaded, change directory into the `django-imager` directory.
```
$ cd django-imager
```

Begin a new virtual environment with Python 3 and activate it.
```
django-imager $ python3 -m venv ENV
django-imager $ source ENV/bin/activate
```

Install the application requirements with [`pip`](https://pip.pypa.io/en/stable/installing/).
```
(ENV) django-imager $ pip install -r requirements.txt
```

Create a [Postgres](https://wiki.postgresql.org/wiki/Detailed_installation_guides) database for use with this application.
```
(ENV) django-imager $ createdb imagersite
```

Export environmental variables pointing to the location of database, your username, hashed password, and secret
```
(ENV) django-imager $ export SECRET_KEY='secret'
(ENV) django-imager $ export DB_NAME='imagersite'
(ENV) django-imager $ export DB_USER='(your postgresql username)'
(ENV) django-imager $ export DB_PASS='(your postgresql password)'
(ENV) django-imager $ export DB_HOST='localhost'
```

Then initialize the database with the `migrate` command from `manage.py`
```
(ENV) django-imager $ python imagersite/manage.py migrate
```

Once the package is installed and the database is created, start the server with the `runserver` command from `manage.py`
```
(ENV) django-imager $ python imagersite/manage.py runserver
```

Application is served on http://localhost:8000

## Testing
You can test this application by first exporting an environmental variable pointing to the location of a testing database, then running the `test` command from `manage.py`.
```
(ENV) django-imager $ export TEST_DB='test_imagersite'
(ENV) django-imager $ python imagersite/manage.py test
```

## Architecture
Built with Python and Django framework. Tested through Django testing suite.

## Change Log

11-20-2017 12:53pm - Initail scaffolding.
