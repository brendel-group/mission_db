const BASE_URL = 'http://127.0.0.1:8000/restapi';

import { MissionData } from "~/data";

// Function to fetch all missions
export const getMissions = async (): Promise<MissionData[]> => {
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
export const createMission = async (mission: Omit<MissionData, 'id'>): Promise<MissionData> => {
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
export const getMission = async (id: number): Promise<MissionData> => {
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
export const updateMission = async (mission: MissionData): Promise<MissionData> => {
    const response = await fetch(`${BASE_URL}/missions/${mission.mission_id}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(mission),
    });
    if (!response.ok) {
        throw new Error(`Failed to update mission with id ${mission.mission_id}`);
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