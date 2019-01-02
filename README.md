[![ESPCI Logo](https://i.imgur.com/qDFBCkQ.png)](https://www.espci.fr/en/)

# ESPCI Bar Web App

[![Build Status](https://travis-ci.org/Stryars/espci-bar-web-app.svg?branch=master)](https://travis-ci.org/Stryars/espci-bar-web-app)
[![Coverage Status](https://coveralls.io/repos/github/Stryars/espci-bar-web-app/badge.svg)](https://coveralls.io/github/Stryars/espci-bar-web-app)
[![Requirements Status](https://requires.io/github/Stryars/espci-bar-web-app/requirements.svg?branch=master)](https://requires.io/github/Stryars/espci-bar-web-app/requirements/?branch=master)
[![GitHub license](https://img.shields.io/badge/License-MIT-green.svg)](https://raw.githubusercontent.com/Stryars/espci-bar-web-app/master/LICENSE.md)

This is the final version of the ESPCI student bar web app, still in development. Written using Python Flask.

### Quickstart

1. Install requirements:
```
$ sudo apt -y update
$ sudo apt -y install python3 python3-venv python3-dev
$ sudo apt -y install mysql-server postfix supervisor nginx git
$ git clone https://github.com/Stryars/espci-bar-web-app.git
$ cd espci-bar-web-app
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

2. Configure your environment in a .env at the root of the project:
```
SECRET_KEY=yoursecretkey
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/bar_webapp

USERS_PER_PAGE=12
ITEMS_PER_PAGE=10

CURRENT_GRAD_CLASS=137

MAX_ALCOHOLIC_DRINKS_PER_DAY=4
MINIMUM_LEGAL_AGE=18
QUICK_ACCESS_ITEM_ID=1
```

3. Configure Flask:
```
(venv) $ echo "export FLASK_APP=espci_bar_web_app.py" >> ~/.profile
```

4. Create the MySQL database:
```
mysql> create database bar_webapp character set utf8 collate utf8_bin;
mysql> create user 'user'@'localhost' identified by '<db-password>';
mysql> grant all privileges on bar_webapp.* to 'user'@'localhost';
mysql> flush privileges;
mysql> quit;
```

5. Run the database migrations:
```
(venv) $ flask db upgrade
```

6. Run the web application:
```
(venv) $ flask run
```

7. Connect to http://localhost:5000/.

## Built With

* [Flask](http://flask.pocoo.org) - Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions.
* [jQuery](https://jquery.com) - jQuery is a fast, small, and feature-rich JavaScript library.
* [Popper.js](https://popper.js.org) - A kickass library
used to manage poppers in web applications.
* [Bootstrap](https://getbootstrap.com) - Bootstrap is an open source toolkit for developing with HTML, CSS, and JS.
* [Chart.js](https://www.chartjs.org) - Simple yet flexible JavaScript charting for designers & developers.
* [jsQR](https://github.com/cozmo/jsQR) - A pure javascript QR code reading library.

## Authors

* **Samuel Diebolt** - *Initial work* - [Stryars](https://github.com/Stryars)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by Miguel Grinberg
