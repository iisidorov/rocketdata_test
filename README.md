# Employee Platform

### Run project with Docker Compose

```sh
$ docker compose build
$ docker compose up
```

###_To launch it manually follow the steps below:_

### Server Setup

The first thing to do is to clone the repository:

```sh
$ git clone git@github.com:iisidorov/rocketdata_test.git
$ cd rocketdata_test
```

If you haven't installed `virtualenv`:
```sh
$ pip install virtualenv
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python -m venv venv
$ venv/Scripts/activate
```

Then install the dependencies:

```sh
(venv)$ pip install -r requirements.txt
```

Clone `.env.example` file, rename it to `.env` and fill it with your data.

Once `pip` has finished downloading the dependencies, run `PostgreSQL` docker container localy:

```sh
(venv)$ docker run --name postgres -p 5432:5432 --env-file ./.env -d postgres:13.3
```

Apply migrations:

```sh
(venv)$ python manage.py migrate
```

And run the Django server:

```sh
(venv)$ python manage.py runserver
```

Navigate to `http://127.0.0.1:8000`.

### Database

Create admin:

```sh
(venv)$ python manage.py create_admin
```

To populate Database with random data run:
```sh
(venv)$ python manage.py seed --mode=refresh --number=40
~~~ OR ~~~
(venv)$ python db_script.py
```

### Celery

Run redis docker container:
```sh
(venv)$ docker run --name redis -d -p 6379:6379 redis
```
And then celery worker:
```sh
(venv)$ celery -A emplatform worker -l info -P eventlet
```

In another console start celery scheduler:

```sh
(venv)$ celery -A emplatform beat -l info -s ./data/celery 
```