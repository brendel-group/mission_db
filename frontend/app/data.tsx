//This represents a single mission in the missions table
export interface Tag {
  tagId: number;

  name: string;
  color: string;
}

export interface MissionData {
  missionId: number;

  name: string;
  location: string;
  totalDuration: string;
  totalSize: string;
  robot: string;
  remarks: string;

  tags: Tag[];
}

//Fetch this data by mission_id from MissionTableData
export interface DetailViewData {
  files: string[];
  durations: string[];
  sizes: string[];
}

export interface BackendMissionData {
  id: number;

  name: string;
  location: string;
  date: string;
  other: string;
}

//User interface
export interface User {
  id: number;
  username: string;
  password: string;
}
