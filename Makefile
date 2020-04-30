runserver:
	@ python manage.py runserver 0.0.0.0:5000

migrate:
	@ echo 'Making and running migrations >>>'
	@ python manage.py makemigrations && python manage.py migrate

shell:
	@ python manage.py shell

load-fixtures:
	@ python manage.py loaddata accounts.json
	@ python manage.py loaddata firstaid.json
