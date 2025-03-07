# Environmental Variables
Many things in the backend can be controlled by environmental variables. Here is a summary about what they do:

## `DEBUG`
#### Default: `False`
Variable by django.
Allows more detailed information about errors and disables authentication. See [django settings](https://docs.djangoproject.com/en/5.1/ref/settings/#debug) for more.

## `SECRET_KEY`
#### Default: No default
Variable by django. See [django settings](https://docs.djangoproject.com/en/5.1/ref/settings/#secret-key) for more.

## `DATABASE_URL`
#### Default: No default
The url to access the database in the format:\
`postgres://<user>:<password>@<hostname>:<port>/<database_name>`\
See our [database documentation](../database/README.md) for more info.\
See [env.db_url](https://django-environ.readthedocs.io/en/latest/types.html#term-PostgreSQL) for other supported databases.

## `COOKIE_DOMAIN`
#### Default: `.mission-explorer.xyz`
Allows setting the cookie domain sent with the CSRF- and Session-Cookie. Should be set to the domain part shared by frontend and backend.

## `DOMAIN`
#### Default: `http://localhost:8000`
The domain on which the backend is hosted.

## `TEMP_FOLDER`
#### Default: `tmp`
Path to folder for temporary files. Used when extracting videos from a mcap file.\
Can be a path relative to the backend root folder (`backend/`).

## `STORE_VIDEO_LOCALLY`
#### Default: `False`
Enforces storing the extracted videos in a different folder and locally (instead of in S3). The folder can be selected with the `VIDEO_ROOT` in settings.py

## `USE_S3`
#### Default: `False`
Controls whether AWS S3 buckets are used for storing files. See [files documentation](../files/README.md) for more.

##  `USE_UNICODE`
#### Default: `True`
Controls the output of the CLI when printing a table.\
By default Unicode characters are used as delimiters, when set to `False` ASCII characters are used.
