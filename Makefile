runserver:
	@ python manage.py runserver 0.0.0.0:5000

migrate:
	@ echo 'Making and running migrations >>>'
	@ python manage.py makemigrations && python manage.py migrate

shell:
	@ python manage.py shell
