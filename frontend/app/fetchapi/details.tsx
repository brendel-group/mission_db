import { DetailViewData } from "~/data";
import { FETCH_API_BASE_URL } from "~/config";
import { getHeaders } from "./headers";
import { transformDurations, transformSizes } from "~/utilities/FormatHandler";

// Get details by mission
export const getDetailsByMission = async (
  missionId: number,
): Promise<DetailViewData> => {
  const response = await fetch(
    `${FETCH_API_BASE_URL}/missions/${missionId}/files/`,
    {
      method: "GET",
      credentials: "include",
      headers: getHeaders(),
    },
  );
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Details of mission with ID ${missionId} not found`);
    }
    throw new Error(`Failed to fetch details by mission ID ${missionId}`);
  }

  const data = await response.json();

  const files: string[] = [];
  const videos: string[] = [];
  const durations: string[] = [];
  const sizes: string[] = [];
  const robots: string[] = [];

  for (const d in data) {
    files.push(data[d].file_path);
    videos.push(data[d].video_path);
    durations.push(data[d].duration);
    sizes.push(data[d].size);
    robots.push(data[d].robot);
  }

  return { files, videos, durations, sizes, robots };
};

// Get details by mission in correct format
export const getFormattedDetails = async (
  missionId: number,
): Promise<DetailViewData> => {
  const details = await getDetailsByMission(missionId);

  const files = details.files;
  const videos = details.videos;
  // transform durations and sizes to correct form
  const durations = transformDurations(details.durations);
  const sizes = transformSizes(details.sizes);
  const robots = details.robots;

  return { files, videos, durations, sizes, robots };
};

// Get total duration of all files in a mission by ID
export const getTotalDuration = async (missionId: number): Promise<string> => {
  const details = await getDetailsByMission(missionId);

  let total = 0;
  for (const duration in details.durations) {
    total += parseInt(details.durations[duration], 10);
  }
  const stringTotal = [`${total}`];

  return transformDurations(stringTotal)[0];
};

// Get total duration of all files in a mission by ID
export const getTotalSize = async (missionId: number): Promise<string> => {
  const details = await getDetailsByMission(missionId);

  let total = 0;
  for (const size in details.sizes) {
    total += parseInt(details.sizes[size], 10);
  }
  const stringTotal = [`${total}`];

  return transformSizes(stringTotal)[0];
};

// Get all robot names of a mission
export const getRobotNames = async (missionId: number): Promise<string[]> => {
  const details = await getDetailsByMission(missionId);

  return details.robots;
};
