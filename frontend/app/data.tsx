export interface Tag {
  name: string;
  color: string;
}

//Fetch this data by mission_id from MissionTableData
export interface DetailViewData {
  files: string[];
  durations: string[];
  sizes: string[];
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

  name: string;
  location: string;
  totalDuration: string;
  totalSize: string;
  robot: string;
  notes: string;

  tags: Tag[];
}

//User interface
export interface User {
  id: number;
  username: string;
  password: string;
}
