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