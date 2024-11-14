//This represents a single mission in the missions table

export interface MissionData {
  mission_id: number;

  name: string;
  location: string;
  total_duration: string;
  total_size: string;
  robot: string;
  remarks: string;

  tags: string[];
}

//Fetch this data by mission_id from MissionTableData
export interface DetailViewData {
  files: string[];
  durations: string[];
  sizes: string[];
}