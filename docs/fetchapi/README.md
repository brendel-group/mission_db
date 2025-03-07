# Fetch API

## Overview
The `fetchapi.ts` file provides utility functions to interact with the Mission Database REST API. The functions handle API requests and responses, providing a simple interface for fetching, creating, updating, and deleting mission data.

## Functions

### setWasModified(id, was_modified)
- set the was_modified field of mission with id to was_modified

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

### getTags()
- Fetches all tags from the backend.
- **Returns**: `Promise<Tag[]>`
- **Endpoint**: `GET /restapi/tags/`

### addTagToMission(missionId, tagName)
- Adds a tag to a mission.
- **Parameters**: `missionId` (number), `tagName` (string)
- **Returns**: `Promise<{ mission_id: number; tag_name: string }>`
- **Endpoint**: `POST /restapi/mission-tags/create/`
`getFormattedDetails`
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

### getFilesByMission(missionID)
- Fetches all file data associated with a specific mission.
- **Parameters**: `missionID` (number)
- **Returns**: `Promise<{ FileData[] }>`
- **Endpoint**: `GET /restapi/missions/{missionID}/files/`

### getFileData(filePath)
- Fetch all file information related to a file path
- **Parameters**: `filePath` (filePath)
- **Returns**: `Promise<{ FileData }>`
- **Endpoint**: `GET /restapi//file/{filePath}`

### getTopicsByFile(file_path)
- Fetches all topics associated with a specific file.
- **Parameters**: `file_path` (string)
- **Returns**: `Promise<Topic[]>`
- **Endpoint**: `GET /topics/{file_path}`

### getAllowedTopics()
- Fetches all allowed topic names.
- **Returns**: `Promise<Topic[]>`
- **Endpoint**: `GET /topics-names`

### createAllowedTopic(topic_name)
- Creates a new allowed topic.
- **Parameters**: `topic_name` (string)
- **Returns**: `Promise<Topic>`
- **Endpoint**: `POST /topics-names/create`

### deleteAllowedTopic(topic_name)
- Deletes an allowed topic by its name.
- **Parameters**: `topic_name` (string)
- **Returns**: `Promise<string>`
- **Endpoint**: `DELETE /topics-names/{topic_name}`

-------------------------
## Configuration
- **`FETCH_API_BASE_URL`**: The base URL for API requests, defined in `config.tsx`. Set to: `http://127.0.0.1:8000/restapi`

## Notes
- All functions use `credentials: 'include'`.
- Error handling is implemented for each function individually, with specific error messages for different statuses (e.g., `400`, `404`).