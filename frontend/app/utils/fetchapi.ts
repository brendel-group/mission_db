const BASE_URL = 'http://127.0.0.1:5432/missionlister/restapi';

export interface Mission {
    id?: number; // Optional because its not needed when creating a new mission
    name: string;
    location: string;
    duration: string;
    size: string;
    robot: string;
    other: string;
}

// Function to fetch all missions
export const getMissions = async (): Promise<Mission[]> => {
    const response = await fetch(`${BASE_URL}/missions/`);
    if (!response.ok) {
        throw new Error('Failed to fetch missions');
    }
    return response.json();
};

// Function to create a new mission
export const createMission = async (mission: Omit<Mission, 'id'>): Promise<Mission> => {
    const response = await fetch(`${BASE_URL}/missions/create`, {
        method: 'POST',
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
export const getMission = async (id: number): Promise<Mission> => {
    const response = await fetch(`${BASE_URL}/missions/${id}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch mission with id ${id}`);
    }
    return response.json();
};

// Function to update an existing mission
export const updateMission = async (mission: Mission): Promise<Mission> => {
    const response = await fetch(`${BASE_URL}/missions/${mission.id}`, {
        method: 'PUT',
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