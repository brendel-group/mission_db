const BASE_URL = 'http://127.0.0.1:8000/restapi';

import { MissionData, BackendMissionData } from "~/data";
import { mission_table_data } from "../RandomData"

// Function to fetch all missions
export const getMissions = async (): Promise<BackendMissionData[]> => {
    const response = await fetch(`${BASE_URL}/missions/`, {
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
    const response = await fetch(`${BASE_URL}/missions/create`, {
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
    const response = await fetch(`${BASE_URL}/missions/${id}`, {
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
    const response = await fetch(`${BASE_URL}/missions/${mission.id}`, {
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
    const response = await fetch(`${BASE_URL}/missions/${id}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        throw new Error(`Failed to delete mission with id ${id}`);
    }
};

export const fetchAndTransformMissions = async (): Promise<MissionData[]> => {
    try {
      const missions: BackendMissionData[] = await getMissions(); // Fetch the missions using the REST API
    
      // Map BackendMissionData missions to MissionData
      let renderedMissions: MissionData[] = [];
      for (let i = 0; i < missions.length; i++) {
        const exampleData = mission_table_data.at(i % 5);
        renderedMissions.push(
            {
            mission_id: missions[i].id,
            name: missions[i].name,
            location: missions[i].location,
            total_duration: exampleData?.total_duration || "",
            total_size: exampleData?.total_size || "",
            robot: exampleData?.robot || "",
            remarks: missions[i].other || "",
            tags: exampleData?.tags || []
            }
        )
      }
  
      return renderedMissions;
    } catch (error) {
      console.error('Failed to fetch and transform missions:', error);
      throw error; // Re-throw the error to handle it upstream if needed
    }
  };
