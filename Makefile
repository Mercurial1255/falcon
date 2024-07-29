run:
	python manage.py runserver

make:
	python manage.py makemigrations
	python manage.py migrate

create_user:
	python manage.py createsuperuser

celery: 
	celery -A root -l INFO

dumpdata:
	python3 manage.py dumpdata --indent=2 apps.Category > apps/fixtures/categories.json
	python3 manage.py dumpdata --indent=2 apps.Product > apps/fixtures/products.json

loaddata:
	python manage.py loaddata apps/fixtures/categories.json apps/fixtures/products.json
