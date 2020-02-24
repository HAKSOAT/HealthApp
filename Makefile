runserver:
	@ python HealthApp/manage.py runserver 0.0.0.0:5000

migrate:
	@ echo 'Making and running migrations >>>'
	@ python HealthApp/manage.py makemigrations && python HealthApp/manage.py migrate
