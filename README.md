[![ESPCI Logo](https://i.imgur.com/qDFBCkQ.png)](https://www.espci.fr/en/)

# ESPCI Bar Web App

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
SECRET_KEY=52cb883e323b48d78a0a36e8e951ba4a
MAIL_SERVER=localhost
MAIL_PORT=25
DATABASE_URL=mysql+pymysql://user:<db-password>@localhost:3306/espci_bar
```

3. Configure Flask:
```
(venv) $ echo "export FLASK_APP=espci_bar_web_app.py" >> ~/.profile
```

4. Create the MySQL database:
```
mysql> create database bar character set utf8 collate utf8_bin;
mysql> create user 'user'@'espci_bar' identified by '<db-password>';
mysql> grant all privileges on user.* to 'espci_bar'@'localhost';
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

* [Flask](http://flask.pocoo.org) - The web framework used
* [jsQR](https://github.com/cozmo/jsQR) - The javascript QR code reading library

## Authors

* **Samuel Diebolt** - *Initial work* - [Stryars](https://github.com/Stryars)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by Miguel Grinberg
