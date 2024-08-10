run:
	python manage.py runserver

make:
	python manage.py makemigrations
	python manage.py migrate

create_user:
	python manage.py createsuperuser

celery:
	celery -A root worker -l INFO

beat:
	celery -A root beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

flower:
	celery -A root.celery.app flower --port=5001


dumpdata:
	python3 manage.py dumpdata --indent=2 apps.Category > apps/fixtures/categories.json
	python3 manage.py dumpdata --indent=2 apps.Product > apps/fixtures/products.json

loaddata:
	python manage.py loaddata apps/fixtures/categories.json apps/fixtures/products.json

image:
	docker build -t django_image .

container:
	docker run -p 8000:8000 -d django_image
