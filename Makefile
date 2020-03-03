runserver:
	@ python manage.py runserver 0.0.0.0:5000

migrate:
	@ echo 'Making and running migrations >>>'
	@ yes | python manage.py makemigrations && yes | python manage.py migrate

shell:
	@ python manage.py shell
