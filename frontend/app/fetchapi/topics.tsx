import { Topic } from "~/data";
import { FETCH_API_BASE_URL } from "~/config";
import { getHeaders } from "./headers";

// Function to fetch all topics of a file
export const getTopicsByFile = async (file_path: string): Promise<Topic[]> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/topics/${file_path}`, {
    method: "GET",
    credentials: "include",
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Error ${response.status}: Failed to fetch topics of file ${file_path}`);
  }
  return response.json();
};

// Function to fetch all allowed topic names
export const getAllowedTopics = async (): Promise<Topic[]> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/topics-names`, {
      method: "GET",
      credentials: "include",
      headers: getHeaders(),
    });
    if (!response.ok) {
      throw new Error(`Error ${response.status}: Failed to fetch allowed topics`);
    }
    return response.json();
  };

// Function to create a new allowed topic
export const createAllowedTopic = async (topic_name: string): Promise<Topic> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/topics-names/create`, {
      method: "POST",
      credentials: "include",
      headers: getHeaders(),
      body: JSON.stringify({ topic_name }),
    });
    if (!response.ok) {
      throw new Error(`Error ${response.status}: Failed to create topic ${topic_name}`);
    }
    return response.json();
  };

// Function to delete an allowed topic by name
export const deleteAllowedTopic = async (topic_name: string): Promise<void> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/topics-names/${topic_name}`, {
      method: "DELETE",
      credentials: "include",
      headers: getHeaders(),
    });
    if (!response.ok) {
      throw new Error(`Error ${response.status}: Failed to delete topic ${topic_name}`);
    }
  };
