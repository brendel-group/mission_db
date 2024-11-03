# REST-API

## where is the code located
The request functions are located in the missionlister/restapi/views.py. The @api_view decorator describes, which request the function implements.

To test the API, one can use the django webserver. The missionlister/restapi/urls.py file defines the URL needed to visit, in order to test the function.

## how to test using the webserver
### starting the webserver
- cd into the missionlister dir
- run `python manage.py runserver`

### using the webserver
- GET Requests
    - [GET Missions](http://127.0.0.1:8000/restapi/missions/) shows all stored missions in our database
- POST Requests
    - [POST Mission] lets you create a new entry in our Missions database.
    - in order to do that, you'll need to past your mission data into the content box in a json format. example data:
    - ```json
      {
        "id": 0,
        "name": "picking apples",
        "date": "2024-10-29 14:58:33.732505",
        "location": "Tuebingen",
        "other": ""
      }  
      ```
- GET, PUT and DELETE mission by id
    - [GET Mission by id](http://127.0.0.1:8000/restapi/missions/0) to access a certain mission, you have to add the mission id to the end of the URL (with the mission with id 0 as an example)
    - PUT Mission by id: on the bottom of the just explained page, you can find a new content box, just like in the POST requests. Fill it with the complete and updated data of this particular mission and hit the PUT button afterwards
    - DELETE Mission by id: on the top right corner of the just explained page, you can find a red DELETE button. Hit this button, if you want to delete this mission

If you want to confirm your actions further, you can always check the current state of the database. The steps to achieve this are described in docs/database.