# primary database
## install postgreSQL
- Download postgreSQL and pgAdmin4 from the official webpage and open the newly installed pgAdmin4.
- Rightclick the desired server and create a new database.
- (for Linux do the following to create a new server and user. In this example with Ubuntu):
    - access the PostgreSQL database shell:
    ```bash
    sudo su - postgres
    ```
    you will see this: `postgres=#`
    - create new server and user. For example user bob with password 'admin'
    ```bash
    postgres=# create user bob with superuser password 'admin';
    ```
    - now go to pgadmin4 and add the server with the usere data from the step before

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
- The secret key can be found in settings.py as a comment
- name should be postgres
- user is you user name (in our linux example from above it is "bob")
- passwort is you password (in our linux example from above it is "admin")
- host should be localhost

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

