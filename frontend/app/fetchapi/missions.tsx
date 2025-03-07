import { MissionData } from "~/data";
import { FETCH_API_BASE_URL } from "~/config";
import { getHeaders } from "./headers";

// Function to fetch all missions
export const getMissions = async (): Promise<MissionData[]> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/missions/`, {
    method: "GET",
    credentials: "include",
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch missions");
  }
  return response.json();
};

// Function to create a new mission
export const createMission = async (
  mission: Omit<MissionData, "id">,
): Promise<MissionData> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/missions/create`, {
    method: "POST",
    credentials: "include",
    headers: getHeaders(),
    body: JSON.stringify(mission),
  });
  if (!response.ok) {
    throw new Error("Failed to create mission");
  }
  return response.json();
};

// Function to fetch a single mission by ID
export const getMission = async (id: number): Promise<MissionData> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/missions/${id}`, {
    method: "GET",
    credentials: "include",
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch mission with id ${id}`);
  }
  return response.json();
};

// Function to update an existing mission
export const updateMission = async (
  mission: MissionData,
): Promise<MissionData> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/missions/${mission.id}`, {
    method: "PUT",
    credentials: "include",
    headers: getHeaders(),
    body: JSON.stringify(mission),
  });
  await setWasModified(mission.id, true);
  if (!response.ok) {
    throw new Error(`Failed to update mission with id ${mission.id}`);
  }
  return response.json();
};

export const setWasModified = async (
  id: number,
  was_modified: boolean,
): Promise<void> => {
  const response = await fetch(
    `${FETCH_API_BASE_URL}/missions/${id}/was_modified`,
    {
      method: "PUT",
      credentials: "include",
      headers: getHeaders(),
      body: JSON.stringify({ was_modified }),
    },
  );
  if (!response.ok) {
    throw new Error(
      `Failed to set wasModified to ${was_modified} for mission with id ${id}`,
    );
  }
};

// Function to delete a mission by ID
export const deleteMission = async (id: number): Promise<void> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/missions/${id}`, {
    method: "DELETE",
    credentials: "include",
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Failed to delete mission with id ${id}`);
  }
};
