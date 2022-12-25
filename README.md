# Running locally

Activate venv: `source venv/bin/activate`

Start redis server: `redis-server`

Start a celery (with beat) worker: `celery -A pepebot.celery worker --pool=solo -l info --beat`

Localhost forwarding: `ngrok http 8000`

Start django server: `python manage.py runserver`
