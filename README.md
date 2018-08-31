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

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
