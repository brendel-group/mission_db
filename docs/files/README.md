# File handling
When using local files the files have to be in the folder `backend/media/` for django to find them.

Django checks if files exists when a restapi response contains files.

## Download

Files can be downloaded using this URL format:\
`http[s]://<domain_name>[:port]/file/download/<file_path>?sessionid=<sessionid>`\
The url will be auto generated in the restapi responses. To have the correct domain_name set the environmental variable `DOMAIN` (default is `http://localhost:8000`)

The `sessionid` is used to confirm that the user is authenticated, so a user has to login first to get a sessionid and access files.

The download supports single-part and multi-part range requests as specified in the [mdn web docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests), but no conditional requests.

## S3 storage
To use S3 storage the following environmental variables are required:
- `USE_S3=TRUE`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

For more info on the required values see the [django-storages docs](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html).