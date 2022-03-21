# Employee Platform

## Setup

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

And run the Django server:

```sh
(venv)$ python manage.py runserver
```

Navigate to `http://127.0.0.1:8000`.
