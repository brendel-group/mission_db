# Fetch API

## Overview
The `fetchapi.ts` file provides utility functions to interact with the Mission Database REST API. The functions handle API requests and responses, providing a simple interface for fetching, creating, updating, and deleting mission data.

**NOTE**: The functions return `BackendMissionData` as the REST API currently does not support all fields from `MissionData`. The function `fetchAndTransformMissions()` will fill in missing fields using data from `RandomData`, which is used when `USE_RANDOM_DATA=true`.

## Functions

### getMissions()
- Fetches all missions from the backend.
- **Returns**: `Promise<BackendMissionData[]>`
- **Endpoint**: `GET /restapi/missions/`

### createMission(mission)
- Creates a new mission in the database.
- **Parameters**: `MissionData` (without `id`)
- **Returns**: `Promise<MissionData>`
- **Endpoint**: `POST /restapi/missions/create`

### getMission(id)
- Fetches a single mission by its ID.
- **Parameters**: `id` (number)
- **Returns**: `Promise<BackendMissionData>`
- **Endpoint**: `GET /restapi/missions/{id}`

### updateMission(mission)
- Updates an existing mission.
- **Parameters**: `BackendMissionData` (all fields including `id`)
- **Returns**: `Promise<BackendMissionData>`
- **Endpoint**: `PUT /restapi/missions/{id}`

### deleteMission(id)
- Deletes a mission by its ID.
- **Parameters**: `id` (number)
- **Returns**: `Promise<void>`
- **Endpoint**: `DELETE /restapi/missions/{id}`

### fetchAndTransformMission(id)
- Fetches a mission using `getMission(id)` and transforms it into `MissionData`. If `USE_RANDOM_DATA=true`, it returns random data.
- **Parameters**: `id` (number)
- **Returns**: `Promise<MissionData>`

### fetchAndTransformMissions()
- Fetches all missions using `getMissions()` and transforms them into `MissionData`. Fills missing fields with random data if `USE_RANDOM_DATA=true`.
- **Returns**: `Promise<MissionData[]>`

### getTags()
- Fetches all tags from the backend.
- **Returns**: `Promise<Tag[]>`
- **Endpoint**: `GET /restapi/tags/`

### addTagToMission(missionId, tagName)
- Adds a tag to a mission.
- **Parameters**: `missionId` (number), `tagName` (string)
- **Returns**: `Promise<{ mission_id: number; tag_name: string }>`
- **Endpoint**: `POST /restapi/mission-tags/create/`

### removeTagFromMission(missionId, tagName)
- Removes a tag from a mission.
- **Parameters**: `missionId` (number), `tagName` (string)
- **Returns**: `Promise<void>`
- **Endpoint**: `DELETE /restapi/mission-tags/delete/{missionId}/{tagName}`

### changeTagColor(tagName, newColor)
- Changes the color of a tag.
- **Parameters**: `tagName` (string), `newColor` (string)
- **Returns**: `Promise<Tag>`
- **Endpoint**: `PUT /restapi/tags/{tagName}`

### createTag(tagName, color)
- Creates a new tag.
- **Parameters**: `tagName` (string), `color` (optional string, default: `#FFFFFF`)
- **Returns**: `Promise<Tag>`
- **Endpoint**: `POST /restapi/tags/create/`

### deleteTag(tagName)
- Deletes a tag by its name.
- **Parameters**: `tagName` (string)
- **Returns**: `Promise<void>`
- **Endpoint**: `DELETE /restapi/tags/{tagName}`

### getTagsByMission(missionId)
- Fetches all tags for a specific mission.
- **Parameters**: `missionId` (number)
- **Returns**: `Promise<Tag[]>`
- **Endpoint**: `GET /restapi/missions/tags/{missionId}`

### getMissionsByTag(tagName)
- Fetches all missions associated with a specific tag.
- **Parameters**: `tagName` (string)
- **Returns**: `Promise<{ id: number; name: string; location: string }[]>`
- **Endpoint**: `GET /restapi/tags/missions/{tagName}`
-------------------------
## Configuration
- **`FETCH_API_BASE_URL`**: The base URL for API requests, defined in `config.tsx`. Set to: `http://127.0.0.1:8000/restapi`
- **`USE_RANDOM_DATA`**: Flag in `config.tsx` to switch between using backend data or random data from `frontend/app/RandomData.tsx` for mission fields.

## Notes
- All functions use `credentials: 'include'`.
- Error handling is implemented for each function individually, with specific error messages for different statuses (e.g., `400`, `404`).
- `fetchAndTransformMissions()` and `fetchAndTransformMission()` will either use real backend data or fallback to random data depending on the `USE_RANDOM_DATA` flag. If random data is used, it comes from the `RandomData.tsx` file in the frontend.