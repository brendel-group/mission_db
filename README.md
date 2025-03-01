# Mission Explorer

## Documentation

### Prerequisites

Before setting up the project, ensure that you have the following installed on your system:


### Clone the Repository

```sh
git clone https://github.com/brendel-group/mission_db.git
cd mission_db
```

### Install Dependencies

#### Backend Setup

To compile opencv-python with the support for h264 codec some system packages are required:

#### In Ubuntu:
```bash
sudo apt install cmake gcc g++ python3-dev libavcodec-dev libavformat-dev libswscale-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libgtk-3-dev x264 libx264-dev
```
#### In Windows:
- install cmake

#### both:

```sh
cd backend
pip install -r requirements.txt 
```
This will install all required python packages and compile `opencv-python` which may take up to 30 minutes.

#### Frontend Setup

```sh
cd frontend
npm install 
```

### Database Setup
We are using postgreSQL for our database, so please make sure that you have it installed. Setting up your database can either be done in the PostgreSQL shell or in the pgAdmin GUI:
#### PostgreSQL shell:
 - access the shell: 
 ```sh
 sudo -u postgres psql`
 ```
 - create a new server and user: 
 ```sh
 CREATE USER <username> WITH SUPERUSER PASSWORD <password>;
 ```
 - create a new database:
 ```sh
 CREATE DATABASE <db_name>;
 ```

#### pgAdmin GUI
- expand the desired server and PostgreSQL insallation
- rightclick the databases section and click on create

### Environment Variables

Create a `.env` file in the `backend/backend` directory and configure the required environment variables. Refer to the following template:

```sh
DATABASE_URL=postgres://username:password@localhost:5432/db_name
SECRET_KEY=your_secret_key # django secret key
```

### Create an user
For authentication purposes, you need to create a user:
```sh
cd backend
python cli.py
user add --name <username>
```
You will then be asked to define your password and confirm it afterwards. These credentials will then be used when loggin in.

### Set cookie domain
In order that logging in on the frontend also authenticates you to access the database, we need to set the cookie domain accordingly.
You can either set an environment variable `COOKIE_DOMAIN` in the previously created `.env` file, or change the default value of the `COOKIE_DOMAIN` variable in the `backend/backend/settings.py` file. If you are using the mission explorer locally, the domain should be `localhost`, if it's deployed externally, it should be the corresponding domain.
 
### Using the application
### Syncing your local mission files with the database

In order to synchronise your local files with the database, first, you have to save the files in the `backend/media` folder. Then you'll need to start the CLI:
```sh
cd backend
python cli.py
sync
```

### Start the Application
#### Start Backend

```sh
cd backend
python manage.py runserver 
```

#### Start Frontend

```sh
cd frontend
npm run build
npm start  
```

#### Using the application
Go to the URL provided after running `npm start` and login using the credentials you have created in the CLI.

---

This guide should help you get the project up and running quickly. If you encounter issues, check the respective README files in the documentation.

