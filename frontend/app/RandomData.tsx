//This file contains demo data, showing the underlying structure the code is using.

import { DetailViewData, MissionData } from "./data";

const mission_table_data: MissionData[] = [
  {
    missionId: 0,
    name: "Apfelwiese Fa. Müller",
    location: "Tübingen",
    totalDuration: "02:15:30",
    totalSize: "1250",
    robot: "Spot",
    notes: "here",
    tags: [
      { name: "Apple", color: "#390099" },
      { name: "Field", color: "#ff0054" },
      { name: "Müller", color: "#2c7da0" },
    ],
  },
  {
    missionId: 1,
    name: "Bauer X",
    location: "San Francisco",
    totalDuration: "01:45:20",
    totalSize: "20",
    robot: "Spot",
    notes: "N/A",
    tags: [
      { name: "Hallo", color: "#ff5400" },
      { name: "Welt", color: "#007f5f" },
    ],
  },
  {
    missionId: 2,
    name: "Obstwiese Y",
    location: "Stuttgart",
    totalDuration: "00:30:15",
    totalSize: "25",
    robot: "Spot",
    notes: "is",
    tags: [
      { name: "Hier", color: "#ff0054" },
      { name: "könnte", color: "#ffbd00" },
      { name: "Ihre", color: "#007f5f" },
      { name: "Werbung", color: "#2c7da0" },
      { name: "stehen", color: "#9e0059" },
    ],
  },
  {
    missionId: 3,
    name: "Bebenhausen Schloss",
    location: "Bebenhausen",
    totalDuration: "03:10:45",
    totalSize: "10",
    robot: "Spot",
    notes: "something",
    tags: [],
  },
  {
    missionId: 4,
    name: "Bauernhof",
    location: "Rottweil",
    totalDuration: "04:00:00",
    totalSize: "30",
    robot: "Spot",
    notes: "extra",
    tags: [
      { name: "veryLongTagThatGetsTruncated", color: "#80b918" },
      { name: "Farm", color: "#ff5400" },
    ],
  },
];

const detail_view_data: { [mission_id: number]: DetailViewData } = {
  0: {
    files: ["file1.mcap", "file2.mcap", "file3.mcap"],
    durations: ["00:01:30", "00:02:45", "00:00:50"],
    sizes: ["2000", "4500", "1000"],
  },
  1: {
    files: ["file4.mcap", "file5.mcap", "file6.mcap"],
    durations: ["00:03:20", "00:01:10", "00:02:00"],
    sizes: ["5000", "2000", "3500"],
  },
  2: {
    files: ["file7.mcap", "file8.mcap", "file9.mcap"],
    durations: ["00:02:50", "00:04:15", "00:03:05"],
    sizes: ["3000", "600", "250"],
  },
  3: {
    files: ["file10.mcap", "file11.mcap", "file12.mcap"],
    durations: ["00:01:45", "00:02:35", "00:04:10"],
    sizes: ["150", "5000", "450"],
  },
  4: {
    files: ["file11.mcap", "5551.mcap", "DADAD.mcap"],
    durations: ["20:01:45", "01:02:35", "00:04:10"],
    sizes: ["4386", "4546", "782"],
  },
};

export { detail_view_data, mission_table_data };
