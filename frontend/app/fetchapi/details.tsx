import { DetailViewData, FileData, Topic } from "~/data";
import { FETCH_API_BASE_URL } from "~/config";
import { getHeaders } from "./headers";
import { transformDurations, transformSizes } from "~/utilities/FormatHandler";
import { getTopicsByFile } from "./topics";

export const GetFilesByMission = async (
  missionId: number,
): Promise<FileData[]> => {
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

  const files: FileData[] = [];

  for (const d in data) {
    files.push({
      filePath: data[d].file_path,
      fileUrl: new URL(data[d].file_url),
      videoPath: data[d].video_path,
      videoUrl: data[d].video_url ? new URL(data[d].video_url) : null,
      duration: transformDurations([data[d].duration])[0],
      size: transformSizes([data[d].size])[0],
      robot: data[d].robot,
      type: data[d].type,
    });
  }

  return files;
};

/**
 * Get details about a file by path
 * @param filePath file path
 * @returns FileData
 */
export const getFileData = async (filePath: string): Promise<FileData> => {
  const response = await fetch(`${FETCH_API_BASE_URL}/file/${filePath}`, {
    method: "GET",
    credentials: "include",
    headers: getHeaders(),
  });
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error((await response.json()).detail);
    }
    throw new Error(`Failed to fetch details for file ${filePath}`);
  }

  const data = await response.json();

  const topics: Topic[] = await getTopicsByFile(filePath);

  var videoPath: string | null = null;
  var videoUrl: URL | null = null;

  for (const topic of topics) {
    if (topic.video_path && topic.video_url) {
      videoPath = topic.video_path;
      videoUrl = new URL(topic.video_url);
      break;
    }
  }

  return {
    filePath: data.file_path,
    fileUrl: new URL(data.file_url),
    videoPath: videoPath,
    videoUrl: videoUrl,
    duration: transformDurations([data.duration])[0],
    size: transformSizes([data.size])[0],
    robot: data.robot,
    type: data.type,
  };
};
