import { MissionData , Tag, DetailViewData} from "~/data";
import { FETCH_API_BASE_URL } from "~/config";

const headers: {
    'Content-Type': string,
    'Authorization'?: string
} = {
    'Content-Type': 'application/json',
}

if ('VITE_BACKEND_API_KEY' in import.meta.env) {
    headers['Authorization'] = 'Api-Key '+import.meta.env.VITE_BACKEND_API_KEY;
}

// Function to fetch all missions
export const getMissions = async (): Promise<MissionData[]> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/`, {
        method: 'GET',
        credentials: 'include',
        headers: headers,
    });
    if (!response.ok) {
        throw new Error('Failed to fetch missions');
    }
    return response.json();
};

// Function to create a new mission
export const createMission = async (mission: Omit<MissionData, 'id'>): Promise<MissionData> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/create`, {
        method: 'POST',
        credentials: 'include',
        headers: headers,
        body: JSON.stringify(mission),
    });
    if (!response.ok) {
        throw new Error('Failed to create mission');
    }
    return response.json();
};

// Function to fetch a single mission by ID
export const getMission = async (id: number): Promise<MissionData> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/${id}`, {
        method: 'GET',
        credentials: 'include',
        headers: headers,
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch mission with id ${id}`);
    }
    return response.json();
};

// Function to update an existing mission
export const updateMission = async (mission: MissionData): Promise<MissionData> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/${mission.id}`, {
        method: 'PUT',
        credentials: 'include',
        headers: headers,
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

// Get all tags
export const getTags = async (): Promise<Tag[]> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/tags/`, {
        method: 'GET',
        headers: headers,
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
        headers: headers,
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
        headers: headers,
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
        headers: headers,
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
        headers: headers,
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
        headers: headers,
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
        headers: headers,
    });
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error('Tag not found');
        }
        throw new Error('Failed to fetch missions for tag');
    }
    return response.json();
};

// Helper function to transform durations from seconds to hh:mm:ss
function transformDurations(durations: string[]): string[] {
    return durations.map(duration => {
        const totalSeconds = parseInt(duration, 10);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    })
}

// Helper function to transform sizes from bytes to megabytes
function transformSizes(sizes: string[]): string[] {
    return sizes.map(size => {
        const bytes = parseInt(size, 10);
        const kilobytes = bytes / 1024;
        const megabytes = kilobytes / 1024;

        let value = megabytes;
        let unit = 'MB';

        if (megabytes < 1) { value = kilobytes; unit = 'KB'; }
        else if (kilobytes < 1) { value = bytes; unit = 'B' }

        return `${value.toFixed(2)} ${unit}`
    });
}

// Get details by mission
export const getDetailsByMission = async (missionId: number): Promise<DetailViewData> => {
    const response = await fetch(`${FETCH_API_BASE_URL}/missions/${missionId}/files/`,{
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error(`Details of mission with ID ${missionId} not found`);
        }
        throw new Error(`Failed to fetch details by mission ID ${missionId}`);
    }
    
    const data = await response.json();
    
    const files: string[] = [];
    const rawDurations: string[] = [];
    const rawSizes: string[] = [];

    for (const d in data) {
        files.push(data[d].file.file_path);
        rawDurations.push(data[d].file.duration);
        rawSizes.push(data[d].file.size);
    }

    const durations = transformDurations(rawDurations);
    const sizes = transformSizes(rawSizes);

    return { files, durations, sizes }
};