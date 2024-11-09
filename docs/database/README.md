# primary database
## install postgreSQL
Download postgreSQL from the official webpage and open the newly installed pgAdmin4.
Rightclick the desired server and create a new database.

## defining server details
We're using postreSQL, for which we need to specify our database name/ip/password/etc in the missionlister/missionlister/settings.py file.
For obvious reasons, it wouldn't be useful to put ip and password in a GitHub repo, therefore we're using the django-environ package.

In order to specify your database details, you need to create a .env file in the same directory as our settings.py file.
In that file please paste the following:
```python
SECRET_KEY= key
DATABASE_NAME=name
DATABASE_USER=user
DATABASE_PASSWORD=password
DATABASE_HOST=host
DATABASE_PORT=5432
```
and modify with your actual details.

## initialize database
cd into the missionlister directory and run the following commands:
```python
python manage.py makemigrations
```
```python
python manage.py migrate
```

## check if everything is setup correctly
In pgadmin4, navigate to the tables:![image](https://github.com/user-attachments/assets/249a4bf0-3735-415e-84e4-4a1a02fbd4ee)
Search for the `restapi_mission` table, rightclick on it and view all rows, the result should look something like this![image](https://github.com/user-attachments/assets/06cc9590-f2e4-4073-8793-2e6bbb3d3e2d)

