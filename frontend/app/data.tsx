export interface Tag {
  name: string;
  color: string;
}

//Fetch this data by mission_id from MissionTableData
//This is essentially the FileData, but a seperate type is used to make the handling more easier.
export interface DetailViewData {
  files: string[];
  fileUrls: URL[];
  durations: string[];
  sizes: string[];
  robots: string[];
  types: string[];
}

export interface FileData {
  filePath: string;
  fileUrl: URL;
  videoPath: string | null;
  videoUrl: URL | null;
  duration: string;
  size: string;
  robot: string;
  type: string;
}

//Represents a mission in the backend
export interface MissionData {
  id: number;

  name: string;
  location: string;
  date: string;
  notes: string;
  total_duration: string;
  total_size: string;
  robots: string[];
}

//This is a local representation used for mission table and details view
export interface RenderedMission {
  id: number;
  // Pure mission fields
  name: string;
  location: string;
  date: string;
  notes: string;
  totalDuration: string;
  totalSize: string;
  robots: string[];

  // Inherited from other data structures (details, tags, ...)
  tags: Tag[];
}

//Topic
export interface Topic {
  id: number;
  file: string;
  name: string;
  type: string;
  message_count: number;
  frequency: number;
  video_path: string | null;
  video_url: string | null;
}

//User interface
export interface User {
  id: number;
  username: string;
  password: string;

  //Backend part
  backendCookie?: string[];
}

//Converts a rendered mission to mission data
export function convertToMissionData(
  renderedMission: RenderedMission,
): MissionData {
  return {
    id: renderedMission.id,
    name: renderedMission.name,
    location: renderedMission.location,
    date: renderedMission.date,
    notes: renderedMission.notes,
    total_duration: renderedMission.totalDuration,
    total_size: renderedMission.totalSize,
    robots: renderedMission.robots,
  };
}

export function convertToDetailViewData(fileData: FileData[]): DetailViewData {
  const files: string[] = [];
  const fileUrls: URL[] = [];
  const durations: string[] = [];
  const sizes: string[] = [];
  const robots: string[] = [];
  const types: string[] = [];

  for (const d in fileData) {
    files.push(fileData[d].filePath);
    fileUrls.push(fileData[d].fileUrl);
    durations.push(fileData[d].duration);
    sizes.push(fileData[d].size);
    robots.push(fileData[d].robot);
    types.push(fileData[d].type);
  }

  return { files, fileUrls, durations, sizes, robots, types };
}
