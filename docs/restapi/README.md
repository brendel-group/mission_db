# REST-API

## where is the code located
The request functions are located in the backend/restapi/views.py. The @api_view decorator describes, which request the function implements.

To test the API, one can use the django webserver. The backend/restapi/urls.py file defines the URL needed to visit, in order to test the function.

## Authentication

Session Authentication is used to authenticate a user.\
To use the REST API you first need to login at the API ENDPOINT at `/restapi/auth/login` which will have a HTTP 204 response and sets 2 cookies in the browser if the login was successfull.\
These cookies are `csrftoken` and `sessionid`.\
The `sessionid` is used to authenticate the user and allows you to make other requests.

It is possible to set the cookie domain with the environmental variable `COOKIE_DOMAIN`

To logout use the API ENDPOINT at `/restapi/auth/logout` (only make a post request without any data) which will delete the `sessionid` cookie and the session stored in the backend. \
The respone will be
```json
{
    "detail": "Successfully logged out."
}
```
even if the user is already logged out.\
Without logout the cookie will be stored and keeps you logged in until the expiration date (currently 2 weeks).

## authentication for the frontend
Available URLs are:
- `/restapi/auth/login/` (POST) returns 204 status code if credentials are valid. Creates django session
- `/restapi/auth/logout/` (POST) Deletes django session
- `/restapi/auth/user/` (GET,PUT,PATCH) User details
- `/restapi/auth/password/change/` (POST) change password
- `/restapi/auth/password/reset/` (POST) not usable until email delivery is supported
- `/restapi/auth/password/reset/confirm/` (POST) also not usable until email delivery is supported

This should only be a short overview about what is suported.\
For more details about how to use the endpoints refer to the [dj-rest-auth documentation](https://dj-rest-auth.readthedocs.io/en/latest/api_endpoints.html).

## how to test using the webserver
### starting the webserver
- cd into the backend dir
- run `python manage.py runserver`

## using the webserver
- GET Requests for missions
    - [GET Missions](http://127.0.0.1:8000/restapi/missions/) shows all stored missions in our database
- POST Requests for missions
    - [POST Mission](http://127.0.0.1:8000/restapi/missions/create) lets you create a new entry in our Missions database.
    - in order to do that, you'll need to past your mission data into the content box in a json format. example data:
    ```json
      {
        "name": "picking apples",
        "date": "2024-10-29",
        "location": "Tuebingen",
        "notes": "good data"
      }  
    ```
    - `name` and `date` are required, while `location` and `notes` are optional.

- GET, PUT and DELETE mission by id
    - [GET Mission by id](http://127.0.0.1:8000/restapi/missions/0) to access a certain mission, you have to add the mission id to the end of the URL (with the mission with id 0 as an example)
    - PUT Mission by id: on the bottom of the just explained page, you can find a new content box, just like in the POST requests. Fill it with the complete and updated data of this particular mission and hit the PUT button afterwards
    - DELETE Mission by id: on the top right corner of the just explained page, you can find a red DELETE button. Hit this button, if you want to delete this mission

- GET Request to list tags by misison id
  - [GET Tags by Mission](http://localhost:8000/restapi/missions/tags/6) shows the tags of a mission.
  - The URL is of the format `restapi/missions/tags/<int:mission_id>`
  - The result is a list of jsons, with each containing the id, name and color of a tag.

- GET Requests for tags
    - [GET Tags](http://localhost:8000/restapi/tags/) shows all stored tags in our database.
- POST Requests for tags
    - [POST Tag](http://localhost:8000/restapi/tags/create/) lets you create a new tag.
    - The id is optional so you can create a new tag using only a name
    - The max length of the name is 42 characters
    - The color is also optional and will default to #FFFFFF (white)
    - Example: 
    ```json
    {
      "name": "test tag"
    }
    ```
    - If an id is given but already in use the database will use another id
    - The repsonse is a json with the `id`, `name` and `color`.
- GET, PUT and DELETE tag using name
    - Tags can be addressed using the name, because the name is unique.
    - If the name contains special characters it has to be url encoded twice, because the webserver is decoding it once and it needs to be passed in encoded format to correctly match the url.
    - With [GET](http://localhost:8000/restapi/tags/test%20tag) you can get details about a tag.
    - The URL is of the format `restapi/tags/<str:tag_name>`
    - With the same url using a PUT Request a tag can be edited. The PUT Request has to contain the complete updated tag data.
    - With the same url using a DELETE Request a tag can be deleted.

- GET Request to list missions by tag name
  - Using a [GET Request](http://localhost:8000/restapi/tags/missions/test%20tag) the missions with the same tag can be listed.
  - The URL is of the format `restapi/tags/missions/<str:tag_name>`
  - Again, if the name has special characters it has to be url encoded twice.
  - The result is of the same format as when listing tags by mission but with missions being listed.
- POST Request to add tag to mission
  - With a [POST Request](http://localhost:8000/restapi/mission-tags/create/) a tag can be added to a mission giving the mission id and a tag name.
  - Example:
  ```json
  {
    "mission_id": 6,
    "tag_name": "test"
  }
  ```
  - <span style="color:red">If there exists no tag with that name a new one will be created.</span>

- DELETE tag from misison
  - With a [DELETE Request](http://localhost:8000/restapi/mission-tags/delete/6/test) a tag can be removed from a mission.
  - The URL is of the format `restapi/mission-tags/delete/<int:mission_id>/<str:tag_name>`
  - Again, if the name has special characters it has to be url encoded twice.
  - Neither the mission nor the tag itself will be deleted. Only the relation.

- Special bevior of relation between mission and tag
  - The relation is stored in a separate table in the database.
  - If the tag or the mission gets deleted the relation of mission and tag will also be deleted.

- GET request to list files by mission ID
  - Using a [GET Request](http://localhost:8000/restapi/missions/0/files) the files of a mission can be listed.
  - The URL is of the format `restapi/missions/<int:mission_id>/files/`
  - The result will be a list of files associated with the specific mission.

- GET request to list all topics for a file path
  - Using a [GET Request](http://localhost:8000/restapi/topics/yourpathhere) the topics from a file path can be listed.
  - The URL is of the format `restapi/topics/<path:file_path>`
  - The result will be a list of topics.

- GET request to list all allowed topic names
  - Using a [GET Request](http://localhost:8000/restapi/topics-names/) the allowed topic names can be listed.
  - The URL is of the format `restapi/topics-names/`
  - The result will be a list of allowed topic names.

- POST request to add an allowed topic name
  - Using a [POST Request](http://localhost:8000/restapi/topics-names/create/) with a name field.
  - The URL is of the format `restapi/topics-names/create/`
  - The result will be an object containing the added name.

- DELETE request to delete an allowed topic name
  - Using a [DELETE Request](http://localhost:8000/topics-names/test) with the name.
  - The URL is of the format `topics-names/<str:name>`
  - The result will be HTTP_204_NO_CONTENT or HTTP_404_NOT_FOUND if the name is not found.

- PUT request to set the was_modified field of a mission
  - Using a [PUT Request](http://localhost:8000/restapi/missions/0/was-modified) with the mission id.
  - The URL is of the format `restapi/missions/<int:mission_id>/was-modified`
  
If you want to confirm your actions further, you can always check the current state of the database. The steps to achieve this are described in docs/database.
