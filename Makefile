migrate:
	@ echo 'Making and running migrations >>>'
	@ python HealthApp/manage.py makemigrations && python HealthApp/manage.py migrate
