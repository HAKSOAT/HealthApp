**HEALTHAPP**

Take the following steps:
 - Create virtual environment in app directory:
	 - > python3 - m virtualenv envname
 - Activate virtual environment:
	 - > source envname/bin/activate

 - Install dependencies
	 - > pip install -r requirements.txt

Ensure to have postgresql and redis installed on your machine. Also create a database with table name of choice. 

Ensure the table name and other database details matches what exists in the ```.env``` file.


 - Load fixtures (mock_data)
	 - > make load-fixtures

To run the server, use:

 - make runserver

