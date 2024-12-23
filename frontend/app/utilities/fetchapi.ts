// Variable to switch between backend data and RandomData is in config.tsx

import { MissionData, BackendMissionData, Tag, DetailViewData} from "~/data";
import { mission_table_data } from "../RandomData";
import { FETCH_API_BASE_URL, USE_RANDOM_DATA } from "~/config";

// Function to fetch all missions
export const getMissions = async (): Promise<BackendMissionData[]> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error('Failed to fetch missions');
    }
    return response.json();
};

// Function to create a new mission
export const createMission = async (mission: Omit<BackendMissionData, 'id'>): Promise<MissionData> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/create`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(mission),
    });
    if (!response.ok) {
        throw new Error('Failed to create mission');
    }
    return response.json();
};

// Function to fetch a single mission by ID
export const getMission = async (id: number): Promise<BackendMissionData> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/${id}`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch mission with id ${id}`);
    }
    return response.json();
};

// Function to update an existing mission
export const updateMission = async (mission: BackendMissionData): Promise<BackendMissionData> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/${mission.id}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(mission),
    });
    if (!response.ok) {
        throw new Error(`Failed to update mission with id ${mission.id}`);
    }
    return response.json();
};

// Function to delete a mission by ID
export const deleteMission = async (id: number): Promise<void> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/${id}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        throw new Error(`Failed to delete mission with id ${id}`);
    }
};

//Debug functions because RestAPI and fetching is incomplete
export const fetchAndTransformMission = async (
    id: number
  ): Promise<MissionData> => {
    if (USE_RANDOM_DATA) {
      return mission_table_data[id % mission_table_data.length];
    } // Return only the RandomData
  
    try {
      const mission: BackendMissionData = await getMission(id); // Fetch the mission using the REST API
      const tags: Tag[] = await getTagsByMission(id); //Fetch the tags for the mission
      tags.sort((a, b) => a.name.localeCompare(b.name));
  
      const exampleData: MissionData = mission_table_data[id % mission_table_data.length];

  
      const transformedMission: MissionData = {
          missionId: mission.id,
          name: mission.name,
          location: mission.location,
          totalDuration: exampleData?.totalDuration || "",
          totalSize: exampleData?.totalSize || "",
          robot: exampleData?.robot || "",
          notes: mission.notes,
          tags: tags || [],
        };
  
      return transformedMission;
    } catch (error) {
      console.error("Failed to fetch and transform mission:", error);
      throw error; // Re-throw the error to handle it upstream if needed
    }
  };

export const fetchAndTransformMissions = async (): Promise<MissionData[]> => {
    if (USE_RANDOM_DATA) { return mission_table_data } // Return only the RandomData
    try {
        const missions: BackendMissionData[] = await getMissions(); // Fetch the missions using the REST API

        // Map BackendMissionData missions to MissionData
        let renderedMissions: MissionData[] = [];
        for (let i = 0; i < missions.length; i++) {
            const tags: Tag[] = await getTagsByMission(missions[i].id);
            tags.sort((a, b) => a.name.localeCompare(b.name));
            const exampleData = mission_table_data.at(i % 5);
            renderedMissions.push(
                {
                    missionId: missions[i].id,
                    name: missions[i].name,
                    location: missions[i].location,
                    totalDuration: exampleData?.totalDuration || "",
                    totalSize: exampleData?.totalSize || "",
                    robot: exampleData?.robot || "",
                    notes: missions[i].notes,
                    tags: tags || []
                }
            )
        }

        return renderedMissions;
    } catch (error) {
        console.error('Failed to fetch and transform missions:', error);
        throw error; // Re-throw the error to handle it upstream if needed
    }
};

// Get all tags
export const getTags = async (): Promise<Tag[]> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/tags/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error('Failed to fetch tags');
    }
    const data = await response.json();
    return data.map((tag: any) => ({
        tagId: tag.id,
        name: tag.name,
        color: tag.color,
    }));
};

// Add a tag to a mission
export const addTagToMission = async (missionId: number, tagName: string): Promise<{ mission_id: number; tag_name: string }> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/mission-tags/create/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mission_id: missionId, tag_name: tagName}),
    });
    if (!response.ok) {
        if (response.status === 400) {
            throw new Error('Invalid data. Ensure mission_id and tag_name are correct.');
        } else if (response.status === 404) {
            throw new Error('Mission or tag not found.');
        }
        throw new Error('Failed to add tag to mission');
    }
    return response.json();
};

// Remove a tag from a mission
export const removeTagFromMission = async (missionId: number, tagName: string): Promise<void> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/mission-tags/delete/${missionId}/${encodeURIComponent(encodeURIComponent(tagName))}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error('Mission, tag, or relationship not found.');
        }
        throw new Error('Failed to remove tag from mission');
    }
};

// Change the color of a tag
export const changeTagColor = async (tagName: string, newColor: string): Promise<Tag> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/tags/${encodeURIComponent(encodeURIComponent(tagName))}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: tagName, color: newColor }),
    });
    if (!response.ok) {
        if (response.status === 400) {
            throw new Error('Invalid data. Ensure the tag name and color are correct.');
        } else if (response.status === 404) {
            throw new Error(`Tag with name "${tagName}" not found.`);
        }
        throw new Error('Failed to change tag color');
    }
    const data = await response.json();
    return {
        name: data.name,
        color: data.color,
    };
};


// Create a new tag
export const createTag = async (tagName: string, color?: string): Promise<Tag> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/tags/create/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: tagName, color: color || '#FFFFFF' }),
    });
    if (!response.ok) {
        if (response.status === 400) {
            throw new Error('Failed to create tag. Check the provided data.');
        }
        throw new Error('Failed to create tag');
    }
    const data = await response.json();
    return {
        name: data.name,
        color: data.color,
    };
};

// Delete a tag by its name
export const deleteTag = async (tagName: string): Promise<void> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/tags/${encodeURIComponent(encodeURIComponent(tagName))}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error(`Tag with name "${tagName}" not found.`);
        }
        throw new Error('Failed to delete tag');
    }
};

// Get all tags for a mission
export const getTagsByMission = async (missionId: number): Promise<Tag[]> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/tags/${missionId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error('Mission not found');
        }
        throw new Error('Failed to fetch tags for mission');
    }
    const data = await response.json();
    return data.map((tag: any) => ({
        tagId: tag.id,
        name: tag.name,
        color: tag.color,
    }));
};

// Get all missions for a tag
export const getMissionsByTag = async (tagName: string): Promise<{ id: number; name: string; location: string }[]> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/tags/missions/${encodeURIComponent(encodeURIComponent(tagName))}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error('Tag not found');
        }
        throw new Error('Failed to fetch missions for tag');
    }
    return response.json();
};

// Get details by mission
export const getDetailsByMission = async (missionId: number): Promise<DetailViewData[]> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/${missionId}/files/`,{
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error(`Mission with ID ${missionId} not found`);
        }
        throw new Error(`Failed to fetch details by mission ID ${missionId}`);
    }
    return response.json();
};