# REST-API

## where is the code located
The request functions are located in the missionlister/restapi/views.py. The @api_view decorator describes, which request the function implements.

To test the API, one can use the django webserver. The missionlister/restapi/urls.py file defines the URL needed to visit, in order to test the function.

## how to test using the webserver
### starting the webserver
- cd into the missionlister dir
- run `python manage.py runserver`

### using the webserver
- GET Requests for missions
    - [GET Missions](http://127.0.0.1:8000/restapi/missions/) shows all stored missions in our database
- POST Requests for missions
    - [POST Mission](http://127.0.0.1:8000/restapi/missions/create) lets you create a new entry in our Missions database.
    - in order to do that, you'll need to past your mission data into the content box in a json format. example data:
    - ```json
      {
        "id": 0,
        "name": "picking apples",
        "date": "2024-10-29 14:58:33.732505",
        "location": "Tuebingen",
        "other": "good data"
      }  
      ```
- GET, PUT and DELETE mission by id
    - [GET Mission by id](http://127.0.0.1:8000/restapi/missions/0) to access a certain mission, you have to add the mission id to the end of the URL (with the mission with id 0 as an example)
    - PUT Mission by id: on the bottom of the just explained page, you can find a new content box, just like in the POST requests. Fill it with the complete and updated data of this particular mission and hit the PUT button afterwards
    - DELETE Mission by id: on the top right corner of the just explained page, you can find a red DELETE button. Hit this button, if you want to delete this mission

- GET Request to list tags by misison id
  - [GET Tags by Mission](http://localhost:8000/restapi/missions/tags/6) shows the tags of a mission.
  - The URL is of the format `restapi/missions/tags/<int:mission_id>`
  - The result is a list of jsons, with each containing the id and name of a tag.

- GET Requests for tags
    - [GET Tags](http://localhost:8000/restapi/tags/) shows all stored tags in our database.
- POST Requests for tags
    - [POST Tag](http://localhost:8000/restapi/tags/create/) lets you create a new tag.
    - The id is optional so you can create a new tag using only a name
    - The max length of the name is 42 characters
    - Example: 
    ```json
    {
      "name": "test tag"
    }
    ```
    - If an id is given but already in use the database will use another id
    - The repsonse is a json with the `id` and `name`
- GET, PUT and DELETE tag using name
    - Tags can be addressed using the name, because the name is unique.
    - With [GET](http://localhost:8000/restapi/tags/test%20tag) you can get details about a tag.
    - The URL is of the format `restapi/tags/<str:tag_name>`
    - With the same url using a PUT Request a tag can be edited. The PUT Request has to contain the complete updated tag data.
    - With the same url using a DELETE Request a tag can be deleted.

- GET Request to list missions by tag name
  - Using a [GET Request](http://localhost:8000/restapi/tags/missions/test%20tag) the missions with the same tag can be listed.
  - The URL is of the format `restapi/tags/missions/<str:tag_name>`
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
  - Neither the mission nor the tag itself will be deleted. Only the relation.

- Special bevior of relation between mission and tag
  - The relation is stored in a separate table in the database.
  - If the tag or the mission gets deleted the relation of mission and tag will also be deleted.


If you want to confirm your actions further, you can always check the current state of the database. The steps to achieve this are described in docs/database.
