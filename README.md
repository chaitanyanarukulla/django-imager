# django-imager

[![Build Status](https://travis-ci.org/chaitanyanarukulla/django-imager.svg?branch=master)](https://travis-ci.org/chaitanyanarukulla/django-imager)
[![Coverage Status](https://coveralls.io/repos/github/chaitanyanarukulla/django-imager/badge.svg?branch=master)](https://coveralls.io/github/chaitanyanarukulla/django-imager?branch=master)

**Author**: Megan Flood and Chaitanya Naru

**Version**: 2.0.0

## Overview
A simple image management website using Django.

## Routes
| Route | Name | Description |
|:--|--|:--|
|`/`|home|the landing page|
|`/login`|login|GET: the login form page<br>POST: logs a user into their account, {username, password}|
|`/logout`|logout|log out the currently logged in user|
|`/profile/<username>`|profile|profile file for given user|
|`/images/library`|library|library os all the logged in user's albums and photos|
|`/images/photos`|photo_gallery|gallery of all public photos|
|`/images/albums`|album_gallery|gallery of all public albums|
|`/images/photos/<id>`|photo_detail|detail of a single photo|
|`/images/albums/<id>`|album_detail|detail of asingel album|
|`/images/photos/add`|photos_create|upload new pictures|
|`/images/albums/add`|photos_create|create new albums|
|`/accounts/*`|all registration routes| included from [django-registration](http://django-registration.readthedocs.io/en/stable/index.html)|
|`/admin/*`|all built-in admin routes| included from [Django admin](https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#reversing-admin-urls)|

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
(ENV) django-imager $ export DEBUG='True'
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
(ENV) django-imager $ python imagersite/manage.py test imagersite
```

## Architecture
Built with Python and Django framework. Tested through Django testing suite.

## Change Log

12-02-2017 7:00pm - Added photos and albums create views

12-01-2017 8:37pm - Added photo, album, and profile views with tests.

11-28-2017 8:35pm - Added Photo and Album models with tests.

11-28-2017 1:35pm - Added registration, login, and logout functionality with tests.

11-21-2017 4:21pm - Added Profile Model for Users with tests.

11-20-2017 12:53pm - Initail scaffolding.
