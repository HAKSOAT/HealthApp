**HEALTHAPP**

HealthApp is a system built to bridge the communication gap between the students and the health centre at the Federal University of Agriculture, Abeokuta. 

The goal behind this system is to create a means for students to get quick response especially in times of emergencies, reducing the fatality rate in the process.

This repository holds the server-side code for the project that has three parts to it:

 1. Client-side web for the health centre
 2. Mobile app for the students
 3. [Alarm (IoT) system](https://github.com/HAKSOAT/HealthAppIoT) for the health centre
 4. Server-side web application

In this code base, you will find the code that the three sections above rely upon to function properly.

The code is written in Python, specifically Django and the Django Rest Framework for the creation of APIs.

Submission should be graded based on the **master** branch and is currently hosted [here](https://curefb.herokuapp.com). However, we are committed to improving the project beyond what we have at submission for the Solutions challenge. Hence, new code will be pushed to the **staging**.


**Setting up Locally**
It is advised that the project is set up on a Linux (Debian-based) operating system and Python 3 for compatibility.

Also ensure that the commands stated are run in the project's root directory.

Here are the steps to set it up:

**Virtual Environment**

Install the virtual environment library:

    sudo apt-get install python3-virtualenv

 Create virtual environment in app directory, replacing `3.6` with the `major`.`minor` version numbers of your Python installation:

    python3 -m virtualenv venv --python=python3.6

 Activate  the virtual environment:

    source venv/bin/activate

Install the dependencies

    pip install -r requirements.txt

Ensure to have `postgresql` and `redis` installed on your machine. Create a database with any name of choice. 

**Environment Variables**
Run:

```cp .env_sample .env```

Fill in the environment variables in the `env` file.

Here are the variables with their meanings

```SECRET_KEY ``` should be a long string of random characters.

```DB_NAME``` should be the name of the database created earlier.

```DB_USERNAME``` should be the username for the Postgresql installation

```DB_HOST ``` should be the location for the database host, ```localhost``` should suffice if running on a local machine.

```DB_PORT``` should be ```5432``` which is the port for Postgresql.

```DB_PASSWORD``` should be the password for the username stated in the ```DB_USERNAME``` variable.

```REDIS_CONNECTION_URL``` should be the location for the Redis connection, ```redis://127.0.0.1:6379/1``` should suffice if running on a local machine.

```EMAIL_HOST``` should be the domain for the email service provider. For example, ```smtp.sendgrid.net``` for Sendgrid.

```EMAIL_PORT``` should be ```465``` since SSL is being used for the connection.

```CUSTOM_EMAIL_SENDER``` should be any custom name which indicates the sender of the emails from the app.

```EMAIL_HOST_USER``` should be the username gotten from the email service provider.

```EMAIL_HOST_PASSWORD``` should be the password for the username in ```EMAIL_HOST_USER```.

**Fixtures**

To load the fixtures (mock data), run:

    make load-fixtures

**Starting the Server**

To run the server, use:

    make runserver


