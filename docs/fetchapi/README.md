# Fetch API

## Overview
The `fetchapi.ts` file provides utility functions for interacting with the Mission Database REST API in the frontend application.
The functions are designed to handle API requests and responses, and provide a simple interface for fetching data.

**NOTE**: The functions return BackendMissionData because the REST API does currently not support all fields from `MissionData`, therefor there is an extra function `fetchAndTransformMissions()` that will fill in missing fields with data from `RandomData` (with `USE_RANDOM_DATA=false`). This function will just return the random data if `USE_RANDOM_DATA = true`.

## Functions

### getMissions()
- Fetches all missions from the backend
- Returns: `Promise<BackendMissionData[]>`
- Endpoint: `GET /restapi/missions/`

### createMission(mission)
- Creates a new mission in the database
- Parameters: `MissionData` without `id`
- Returns: `Promise<MissionData>`
- Endpoint: `POST /restapi/missions/create`
- Parameters: `id` (number)
- Returns: `Promise<BackendMissionData>`
- Endpoint: `GET /restapi/missions/{id}`

### updateMission(mission)
- Updates an existing mission
- Parameters: `MissionData` (all fields)
- Returns: `Promise<BackendMissionData>`
- Endpoint: `PUT /restapi/missions/{id}`

### deleteMission(id)
- Deletes a mission by `id`
- Parameters: `id` (number)
- Returns: `Promise<void>`
- Endpoint: `DELETE /restapi/missions/{id}`

### fetchAndTransformMissions()
- Fetches missions using `getMissions()` and transforms them to frontend data format `MissionData` (filling in missing fields with random data)
- Can use random data or backend data based on `USE_RANDOM_DATA` flag
- Returns: `Promise<MissionData[]>`

## Configuration
- `BASE_URL`: Set to `http://127.0.0.1:8000/restapi`
- `USE_RANDOM_DATA`: Toggle between data from the backend and random data from `frontend/app/RandomData.tsx`

## Notes
- All functions use `credentials: 'include'`
- Error handling is implemented for each function individually