import { Tag } from "~/data";
import { FETCH_API_BASE_URL } from "~/config";
import { getHeaders } from "./headers";

// Get all tags
export const getTags = async (): Promise<Tag[]> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/tags/`, {
    method: "GET",
    credentials: "include",
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch tags");
  }
  const data = await response.json();
  return data.map((tag: any) => ({
    tagId: tag.id,
    name: tag.name,
    color: tag.color,
  }));
};

// Add a tag to a mission
export const addTagToMission = async (
  missionId: number,
  tagName: string
): Promise<{ mission_id: number; tag_name: string }> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/mission-tags/create/`, {
    method: "POST",
    credentials: "include",
    headers: getHeaders(),
    body: JSON.stringify({ mission_id: missionId, tag_name: tagName }),
  });
  if (!response.ok) {
    if (response.status === 400) {
      throw new Error(
        "Invalid data. Ensure mission_id and tag_name are correct."
      );
    } else if (response.status === 404) {
      throw new Error("Mission or tag not found.");
    }
    throw new Error("Failed to add tag to mission");
  }
  return response.json();
};

// Remove a tag from a mission
export const removeTagFromMission = async (
  missionId: number,
  tagName: string
): Promise<void> => {
  const response = await fetch(
    `${FETCH_API_BASE_URL}/mission-tags/delete/${missionId}/${encodeURIComponent(
      encodeURIComponent(tagName)
    )}`,
    {
      method: "DELETE",
      credentials: "include",
      headers: getHeaders(),
    }
  );
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Mission, tag, or relationship not found.");
    }
    throw new Error("Failed to remove tag from mission");
  }
};

// change the name of a tag
export const changeTagName = async (
  tagName: string,
  newName: string
): Promise<Tag> => {
  const response = await fetch(
    `${FETCH_API_BASE_URL}/tags/${encodeURIComponent(
      encodeURIComponent(tagName)
    )}`,
    {
      method: "PUT",
      credentials: "include",
      headers: getHeaders(),
      body: JSON.stringify({ name: newName }),
    }
  );
  if (!response.ok) {
    if (response.status === 400) {
      throw new Error("Invalid data. Ensure the tag name is correct.");
    } else if (response.status === 404) {
      throw new Error(`Tag with name "${tagName}" not found.`);
    }
    throw new Error("Failed to change tag name");
  }
  const data = await response.json();
  return {
    name: data.name,
    color: data.color,
  };
};

// Change the color of a tag
export const changeTagColor = async (
  tagName: string,
  newColor: string
): Promise<Tag> => {
  const response = await fetch(
    `${FETCH_API_BASE_URL}/tags/${encodeURIComponent(
      encodeURIComponent(tagName)
    )}`,
    {
      method: "PUT",
      credentials: "include",
      headers: getHeaders(),
      body: JSON.stringify({ name: tagName, color: newColor }),
    }
  );
  if (!response.ok) {
    if (response.status === 400) {
      throw new Error(
        "Invalid data. Ensure the tag name and color are correct."
      );
    } else if (response.status === 404) {
      throw new Error(`Tag with name "${tagName}" not found.`);
    }
    throw new Error("Failed to change tag color");
  }
  const data = await response.json();
  return {
    name: data.name,
    color: data.color,
  };
};

// Create a new tag
export const createTag = async (
  tagName: string,
  color?: string
): Promise<Tag> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/tags/create/`, {
    method: "POST",
    credentials: "include",
    headers: getHeaders(),
    body: JSON.stringify({ name: tagName, color: color || "#FFFFFF" }),
  });
  if (!response.ok) {
    if (response.status === 400) {
      throw new Error("Failed to create tag. Check the provided data.");
    }
    throw new Error("Failed to create tag");
  }
  const data = await response.json();
  return {
    name: data.name,
    color: data.color,
  };
};

// Delete a tag by its name
export const deleteTag = async (tagName: string): Promise<void> => {
  const response = await fetch(
    `${FETCH_API_BASE_URL}/tags/${encodeURIComponent(
      encodeURIComponent(tagName)
    )}`,
    {
      method: "DELETE",
      credentials: "include",
      headers: getHeaders(),
    }
  );
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Tag with name "${tagName}" not found.`);
    }
    throw new Error("Failed to delete tag");
  }
};

// Get all tags for a mission
export const getTagsByMission = async (missionId: number): Promise<Tag[]> => {
  const response = await fetch(
    `${FETCH_API_BASE_URL}/missions/tags/${missionId}`,
    {
      method: "GET",
      credentials: "include",
      headers: getHeaders(),
    }
  );
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Mission not found");
    }
    throw new Error("Failed to fetch tags for mission");
  }
  const data = await response.json();
  return data.map((tag: any) => ({
    tagId: tag.id,
    name: tag.name,
    color: tag.color,
  }));
};

// Get all tags for a mission
export const getMissionsByTag = async (
  tagName: string
): Promise<{ id: number; name: string; location: string }[]> => {
  const response = await fetch(
    `${FETCH_API_BASE_URL}/tags/missions/${encodeURIComponent(
      encodeURIComponent(tagName)
    )}`,
    {
      method: "GET",
      credentials: "include",
      headers: getHeaders(),
    }
  );
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Tag not found");
    }
    throw new Error("Failed to fetch missions for tag");
  }
  return response.json();
};
