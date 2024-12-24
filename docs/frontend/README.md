## Frontend Setup
1. **Install Node.js (if needed)**
   - If `npm` is not available on your system, [download and install Node.js](https://nodejs.org/). This will include `npm`.

2. **Install Project Dependencies**
   - Once Node.js is installed, navigate to the frontend directory and run:
     ```bash
     npm install
     ```
   - This command will download and set up all necessary dependencies for the project.

2. **Start the Web Server**
   - For development, it is recommended to use the dev server, start it by typing:
     ```bash
     npm run dev
     ```
     It offers additional features like debugging or hot reload, but this leads to higher loading times. Alternatively, use the production server. Build the project: 
     ```bash 
     npm run build
     ```
     Start the production server:
     ```bash 
     npm start
     ```

## Login
   Currently, there is no backend connection for the login system, so, use the default user instead:
   ```
   Username: admin
   Password: admin
   ```

## Frontend Configuration
   In the frontend configuration ```frontend/app/config.tsx``` you can set the base url for backend fetching, it is also possible to disable fetching from backend. ```MAX_SESSION_AGES``` determines how long a login session is valid. Setting it to ```undefined``` enables sessions without a time limit. 

## API KEY Configuration
   If the backend is started with `DEBUG=False` (the default) it is necessary to use an API KEY to communicate with the backend.\
   Create a `.env` file in the `frontend/` folder with the content:
   ```bash
   VITE_BACKEND_API_KEY = '<api-key>'
   ```
   and replace `<api-key>` with an actual API KEY.\
   For how to get an API KEY please refer to the [cli documentation](https://github.com/brendel-group/mission_db/blob/main/docs/cli/README.md) for the `api-key` command.\
   Make sure to not add the `.env` file to git or publish in any way.

