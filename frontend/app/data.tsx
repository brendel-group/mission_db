export interface Tag {
  name: string;
  color: string;
}

//Fetch this data by mission_id from MissionTableData
export interface DetailViewData {
  files: string[];
  durations: string[];
  sizes: string[];
  robots: string[];
}

//Represents a mission in the backend
export interface MissionData {
  id: number;

  name: string;
  location: string;
  date: string;
  notes: string;
}

//This is a local representation used for mission table and details view
export interface RenderedMission {
  id: number;
  // Pure mission fields
  name: string;
  location: string;
  date: string;
  notes: string;

  // Inherited from other data structures (details, tags, ...)
  totalDuration: string;
  totalSize: string;
  robot: string;
  tags: Tag[];
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
  renderedMission: RenderedMission
): MissionData {
  return {
    id: renderedMission.id,
    name: renderedMission.name,
    location: renderedMission.location,
    date: renderedMission.date,
    notes: renderedMission.notes,
  };
}
